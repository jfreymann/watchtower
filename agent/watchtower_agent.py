#!/usr/bin/env python3
import os
import sys
import time
import json
import logging
import subprocess
import re
from datetime import datetime, timezone
from typing import Optional

import requests

# ---------------- Config from environment ----------------

COLLECTOR_URL = os.environ.get("WATCHTOWER_COLLECTOR_URL")
TOKEN = os.environ.get("WATCHTOWER_TOKEN")
REGION = os.environ.get("WATCHTOWER_REGION")
HOST_GROUP = os.environ.get("WATCHTOWER_HOST_GROUP")
DEFAULT_SEVERITY = os.environ.get("WATCHTOWER_SEVERITY", "info")

logging.basicConfig(
    level=DEFAULT_SEVERITY,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


DEFAULT_FLAGGED = (
    os.environ.get("WATCHTOWER_FLAGGED", "false").strip().lower() == "true"
)

VERIFY_TLS = not (
    os.environ.get("WATCHTOWER_VERIFY_TLS", "true").strip().lower() == "false"
)

SSH_UNIT = os.environ.get("WATCHTOWER_SSH_UNIT", "ssh.service")

# ---------------- Basic validation ----------------

if not COLLECTOR_URL:
    print("WATCHTOWER_COLLECTOR_URL is not set", file=sys.stderr)
    sys.exit(1)

if not TOKEN:
    print("WATCHTOWER_TOKEN is not set", file=sys.stderr)
    sys.exit(1)

# ---------------- Logging ----------------

logger = logging.getLogger("watchtower.agent")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
)
logger.addHandler(handler)

logger.info("Starting Watchtower Agent")
logger.info("Collector URL: %s", COLLECTOR_URL)
logger.info("SSH unit: %s", SSH_UNIT)
logger.info("TLS verification: %s", VERIFY_TLS)

# ---------------- SSH log parsing ----------------

# Typical Ubuntu auth log line patterns, e.g.:
# "Accepted publickey for jaye from 1.2.3.4 port 54321 ssh2"
ACCEPTED_RE = re.compile(
    r"Accepted\s+(\w+)\s+for\s+(\S+)\s+from\s+([\d.:a-fA-F]+)\s+port\s+(\d+)"
)


def parse_ssh_line(line: str) -> Optional[dict]:
    """
    Parse a log line for a successful SSH login.
    Returns None if not a match.
    """
    m = ACCEPTED_RE.search(line)
    if not m:
        return None

    method, user, source_ip, source_port = m.groups()
    now = datetime.now(timezone.utc).isoformat()

    payload = {
        "type": "user_login",
        "timestamp": now,
        "hostname": os.uname().nodename,
        "user": user,
        "method": method,
        "source_ip": source_ip,
        "source_port": source_port,
        "raw_message": line.strip(),
        "region": REGION,
        "host_group": HOST_GROUP,
        "severity": DEFAULT_SEVERITY,
        "flagged": DEFAULT_FLAGGED,
    }

    return payload


# ---------------- HTTP client ----------------

SESSION = requests.Session()
SESSION.headers.update(
    {
        # Collector still expects this header name
        "X-Login-Alert-Token": TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "watchtower/agent/0.1",
    }
)


def send_event(event: dict) -> None:
    """
    Send a single event to the Watchtower Collector.
    Uses small retry/backoff on transient failures.
    """
    max_retries = 3
    backoff = 2

    for attempt in range(1, max_retries + 1):
        try:
            resp = SESSION.post(
                COLLECTOR_URL,
                data=json.dumps(event),
                timeout=5,
                verify=VERIFY_TLS,
            )
            if resp.status_code == 200:
                logger.info(
                    "Sent event for user=%s from %s:%s",
                    event.get("user"),
                    event.get("source_ip"),
                    event.get("source_port"),
                )
                return
            else:
                if resp.ok:
                    logger.info("Collector accepted event id=%s", resp.json().get("id"))
                else:
                    logger.warning(
                        "Collector returned %s: %s", resp.status_code, resp.text
                    )

        except requests.RequestException as e:
            logger.error("Error sending event (attempt %d/%d): %s", attempt, max_retries, e)

        time.sleep(backoff)
        backoff *= 2  # exponential backoff

    logger.error(
        "Failed to send event after %d attempts; dropping. user=%s ip=%s",
        max_retries,
        event.get("user"),
        event.get("source_ip"),
    )


# ---------------- Journal follower ----------------

def follow_journal():
    """
    Follow ssh.service logs via journalctl.
    Uses 'journalctl -u <unit> -f -o cat' to get clean text lines.
    """
    cmd = ["journalctl", "-u", SSH_UNIT, "-f", "-o", "cat"]
    logger.info("Starting journalctl: %s", " ".join(cmd))

    while True:
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            # Read stdout line by line
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue

                event = parse_ssh_line(line)
                if event:
                    send_event(event)

            # If we exit the loop, journalctl died
            rc = proc.wait()
            logger.warning("journalctl exited with return code %s; restarting...", rc)
            time.sleep(2)

        except Exception as e:
            logger.exception("Error running journalctl follower: %s", e)
            time.sleep(5)


def main():
    try:
        follow_journal()
    except KeyboardInterrupt:
        logger.info("Watchtower Agent shutting down")
    except Exception:
        logger.exception("Fatal error in Watchtower Agent")
        sys.exit(1)


if __name__ == "__main__":
    main()
