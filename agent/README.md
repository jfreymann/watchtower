# 🚨 Watchtower Agent

Lightweight Linux security telemetry agent for SSH login monitoring
(Part of the Watchtower distributed security telemetry system)

Watchtower Agent is a hardened Linux daemon that monitors successful SSH logins and forwards structured security events to a central Watchtower Collector over HTTPS. It is designed to run across distributed server fleets with minimal overhead and strong security boundaries.
```bash
📡 Architecture Overview
┌───────────────────────┐         HTTPS (TLS, Token Auth)          ┌────────────────────────┐
│      Linux Host       │ ───────────────────────────────────────▶ │   Watchtower Collector │
│  (SSH logins happen)  │                                          │    (FastAPI + Caddy)   │
│                       │                                          │                        │
│  ┌─────────────────┐  │ journalctl -f (ssh.service)              │ Stores events (SQLite) │
│  │ Watchtower Agent│──┼────────────────────────────────────────▶ │ Filters / Forensics    │
│  │ (Python script) │  │                                          │ Admin API + dashboards │
│  └─────────────────┘  │                                          └────────────────────────┘
│     systemd service   │
└───────────────────────┘
```

The agent:

* Watches systemd logs for successful SSH logins
* Extracts user details and connection metadata
* Adds region/host metadata
* Sends JSON events to the collector securely

## 🔐 Features

* Monitors successful SSH login events via journalctl
* Regex-based parsing for accepted logins
* Sends structured events over HTTPS
* Token-based authentication (X-Login-Alert-Token)
* Configurable metadata fields (region, host group, severity)
* Optional TLS verification (useful with internal CA)
* Hardened systemd service
* Very small footprint (<200 lines)
* Zero inbound ports/open attack surface

## 📁 Repository Structure

```bash
watchtower/agent/
├── watchtower_agent.py
├── README.md
├── Caddyfile.example
├── requirements.txt
└── systemd/
    └── watchtower/agent.service
```

## 🎛️ Environment Variables

### Create /opt/watchtower/agent/.env:
```bash
# Collector endpoint (HTTPS fronted by Caddy)
WATCHTOWER_COLLECTOR_URL=https://watchtower.local/login

# Token provided by the collector service
WATCHTOWER_TOKEN=YOUR_AGENT_TOKEN

# Optional metadata for filtering/organization
WATCHTOWER_REGION=us-east
WATCHTOWER_HOST_GROUP=prod-api
WATCHTOWER_SEVERITY=info
WATCHTOWER_FLAGGED=false

# Disable verification if using Caddy's internal CA
WATCHTOWER_VERIFY_TLS=false

# SSH service for journal monitoring
WATCHTOWER_SSH_UNIT=ssh.service
```

#### Make this readable only by the service:

```bash
sudo chmod 600 /opt/watchtower/agent/.env
sudo chown watchtower/agent:watchtower/agent /opt/watchtower/agent/.env
```

## 🛠️ Installation

#### 1. Install dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

#### 2. Create agent directory

```bash
sudo mkdir -p /opt/watchtower/agent
sudo cp watchtower_agent.py /opt/watchtower/agent/
```

#### 3. Create service user

```bash
sudo useradd --system --shell /usr/sbin/nologin -G adm watchtower/agent
```

**The adm group grants read access to logs/journalctl.**

#### 4. Install Python environment

```bash
cd /opt/watchtower/agent
sudo python3 -m venv .venv
sudo .venv/bin/pip install --upgrade pip requests
sudo chown -R watchtower/agent:watchtower/agent /opt/watchtower/agent
```

#### 5. Add environment file

```bash
sudo nano /opt/watchtower/agent/.env
````

Insert the environment variables above.

## ⚙️ Systemd Service Setup

### Create the service:

**/etc/systemd/system/watchtower/agent.service**

```bash
[Unit]
Description=Watchtower Agent - SSH login monitoring
After=network-online.target systemd-journald.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/watchtower/agent
EnvironmentFile=/opt/watchtower/agent/.env
ExecStart=/opt/watchtower/agent/.venv/bin/python /opt/watchtower/agent/watchtower_agent.py

User=watchtower/agent
Group=watchtower/agent

Restart=always
RestartSec=5

# ---- Hardening ----
NoNewPrivileges=yes
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
LockPersonality=yes
MemoryDenyWriteExecute=true
RestrictRealtime=true
RestrictSUIDSGID=true
CapabilityBoundingSet=
AmbientCapabilities=

# Allow agent to read system logs
ReadOnlyPaths=/var/log /var/log/journal

[Install]
WantedBy=multi-user.target
```

### Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now watchtower/agent.service
sudo systemctl status watchtower/agent.service
```

## 🧪 Testing the Agent'

### 1. SSH into the host

Open a new SSH session:

```bash
ssh user@agent-host
```

## 2. Check agent logs

```bash
journalctl -u watchtower/agent.service -n 50 -xe
```

**You should see:**

```bash
Sent event for user=jaye from 1.2.3.4:55231
```

## 3. Validate event ingestion on the collector

```bash
curl -k "https://watchtower.local/events?hours=1&limit=10" \
  -H "X-Admin-Api-Key: YOUR_ADMIN_KEY"
```

## 🧩 Example Event Payload

```bash
{
  "type": "user_login",
  "timestamp": "2025-11-19T19:32:55.102Z",
  "hostname": "zeus",
  "user": "jayefreymann",
  "method": "publickey",
  "source_ip": "203.0.113.54",
  "source_port": "55291",
  "raw_message": "Accepted publickey for jayefreymann from 203.0.113.54 port 55291 ssh2",
  "region": "us-east",
  "host_group": "prod-api",
  "severity": "info",
  "flagged": false
}
```

## 🏎️ Performance

* CPU usage: near zero
* Memory: ~20–30 MB
* Disk writes: none
* Journald-backed, efficient tailing
* No persistent queue required (events small & frequent)

## 🔒 Security Model

* Outbound-only connectivity
* Token-based auth
* No inbound ports
* TLS encryption (via Caddy proxy)
* systemd sandboxing
* Runs as non-root service user
* No filesystem writes (except logs)
* Safe for untrusted or exposed environments

## 🧭 Roadmap

* Failed login detection
* sudo elevation monitoring
* Persistent local queue for offline buffering
* .deb package generation
* Event enrichment (geoIP, ASN lookups)
* Process anomaly detection

## 📜 License

MIT License

## ❤️ Credits

Built as part of the Watchtower security telemetry platform.