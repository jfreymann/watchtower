# Watchtower Collector

**Watchtower Collector** is a sentral security telemetry collector for distributed Linux login monitoring
(Part of the Watchtower security observability platform). Watchtower Collector is an API service that receives login events from distributed Watchtower Agents. It validates, stores, and exposes security telemetry through a hardened FastAPI backend protected by Caddy.

It’s designed as the central “brain” of the Watchtower stack:

- Agents on servers parse `/var/log/auth.log`
- Events are POSTed to Watchtower Collector over HTTPS
- Watchtower stores, filters, and forwards alerts as needed

## Features

- Secure HTTPS collector (Caddy reverse proxy)
- Token-based authentication for agents
- Admin API surface with API keys
- Enriched event storage (region, host group, severity)
- Searchable event history
- Built-in audit logging
- Designed for production (systemd, hardened)
- Optional Slack webhook notifications

## Architecture

```bash
                          ┌──────────────────────────────┐
                          │     Watchtower Agents        │
                          │ (SSH login monitors on hosts)│
                          └──────────────┬───────────────┘
                                         │ HTTPS + Token Auth
                                         ▼
                        ┌────────────────────────────────────────┐
                        │         Watchtower Collector           │
                        │   FastAPI backend listening on :8000   │
                        │                                        │
                        │  ┌──────────────┐    ┌──────────────┐  │
                        │  │ Caddy Proxy  │    │ SQLite DB    │  │
                        │  │ TLS/internal │    │ login_events │  │
                        │  │  firewalling │    │ api_tokens   │  │
                        │  └──────────────┘    └──────────────┘  │
                        │                                        │
                        └────────────────────────────────────────┘
```

## 📁 Repository Structure

```bash
watchtower/collector/
├── main.py
├── models.py
├── database.py
├── requirements.txt
├── README.md
├── setup.sh
├── docker-compose.yml
├── systemd/
│   └── watchtower/collector.service
└── Caddyfile.example
```

## 🧬 Environment Variables

```bash
# Path to SQLite database
WATCHTOWER_DB_PATH=/opt/watchtower/collector/watchtower.db

# Admin API Key for /events, /admin APIs
ADMIN_API_KEY=YOUR_ADMIN_KEY

# Token for Watchtower Agent authentication
WATCHTOWER_AGENT_TOKEN=YOUR_AGENT_TOKEN

# Optional webhook for critical events
WATCHTOWER_WEBHOOK_URL=
```

**Permissions:**

```bash
sudo chmod 600 /opt/watchtower/collector/.env
sudo chown watchtower/collector:watchtower/collector /opt/watchtower/collector/.env
```

## 🛠️ Installation

### 1. Install dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip caddy

```

### 2. Create system user

```bash
sudo useradd --system --shell /usr/sbin/nologin watchtower/collector
```

### 3. Create installation directory

```bash
sudo mkdir -p /opt/watchtower/collector
sudo cp -r . /opt/watchtower/collector
```

### 4. Install Python environment

```bash
cd /opt/watchtower/collector
sudo python3 -m venv .venv
sudo .venv/bin/pip install --upgrade pip
sudo .venv/bin/pip install -r requirements.txt
sudo chown -R watchtower/collector:watchtower/collector /opt/watchtower/collector

```

### 5. Create systemd unit

```bash
[Unit]
Description=Watchtower Collector API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/watchtower/collector
EnvironmentFile=/opt/watchtower/collector/.env
ExecStart=/opt/watchtower/collector/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --proxy-headers

User=watchtower/collector
Group=watchtower/collector

Restart=always
RestartSec=5

# Hardening
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

[Install]
WantedBy=multi-user.target
```

**Enable & start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now watchtower/collector.service
```

## 🔒 Caddy Reverse Proxy (HTTPS + IP Restrictions)

```nginx
watchtower.local {
	tls internal
	encode zstd gzip

	# Restrict admin API to specific workstation
	@admin_protected {
		path /events*
		path /admin/*
		not remote_ip 192.168.1.188/32
	}
	respond @admin_protected "Forbidden" 403

	reverse_proxy 127.0.0.1:8000
}
```

**Test & reload:**

## 🧪 API Usage

### Health Check

```json
curl -k https://watchtower.local/healthz
```

#### Response:

```json
{"status":"ok"}
```

### Submit an event (agent only)

```bash
curl -X POST https://watchtower.local/login \
  -H "Content-Type: application/json" \
  -H "X-Login-Alert-Token: YOUR_AGENT_TOKEN" \
  -d '{ ... }'
```

### Retrieve events (admin only)

```bash
curl -k "https://watchtower.local/events?hours=12&limit=100" \
  -H "X-Admin-Api-Key: YOUR_ADMIN_KEY"

```

### Example event document

```json
{
  "id": 14,
  "created_at": "2025-11-19T19:32:55Z",
  "event_timestamp": "2025-11-19T19:32:54Z",
  "hostname": "zeus",
  "user": "jayefreymann",
  "method": "publickey",
  "source_ip": "203.0.113.10",
  "source_port": "55211",
  "raw_message": "Accepted publickey for jayefreymann...",
  "region": "us-east",
  "host_group": "prod-api",
  "severity": "info",
  "flagged": false
}
```

## 🧱 Database Schema (SQLite)

```scss
login_events
├── id (int, PK)
├── created_at (datetime)
├── event_timestamp (string)
├── hostname (string)
├── user (string)
├── method (string)
├── source_ip (string)
├── source_port (string)
├── raw_message (string)
├── region (string)
├── host_group (string)
├── severity (string)
└── flagged (bool)

api_tokens
├── id (int, PK)
└── token (string)
```

## 🔐 Security Model

✔ Strong defaults

- HTTPS enforced via Caddy
- TLS certificates by internal CA
- No external access to uvicorn (localhost-only)
- All inbound traffic restricted at Caddy

✔ Authentication

- Agents authenticated with X-Login-Alert-Toke
- Admin APIs gated with X-Admin-Api-Key

✔ systemd sandboxing

- NoNewPrivileges
- MemoryDenyWriteExecute
- PrivateTmp
- ProtectSystem=strict
- Runs as non-root

✔ SQLite file protections

- Owned by watchtower/collector
- Mode 600

## 🧭 Roadmap

- Full web UI for event browsing
- Stream API for SIEM ingestion
- Per-agent rolling tokens
- Multi-region collectors
- Optional Postgres backend
- Query engine for anomaly detection

## Installation (Bare Metal)

```bash
git clone https://github.com/<you>/watchtower/collector.git
cd watchtower/collector
sudo ./setup.sh
```

The installer will:

- Create /opt/watchtower/collector
- Create /var/lib/watchtower/collector
- Create a watchtower system user
- Set up a Python venv and install dependencies
- Create /opt/watchtower/collector/.env
- Install and start watchtower/collector.service

Edit `.env`:

```bash
LOGIN_ALERT_TOKEN=YOUR_AGENT_TOKEN
ADMIN_API_KEY=YOUR_ADMIN_KEY
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

**Check the Status**

```bash
sudo systemctl status watchtower/collector
curl http://127.0.0.1:8000/healthz
```

## API Quickstart

**Ingest a login event:**

```bash
curl -X POST https://watchtower.local/login \
  -H "Content-Type: application/json" \
  -H "X-Login-Alert-Token: YOUR_AGENT_TOKEN" \
  -d '{
        "type":"user_login",
        "timestamp":"now",
        "hostname":"server01",
        "user":"ubuntu",
        "method":"publickey",
        "source_ip":"1.2.3.4",
        "source_port":"54321"
      }'
```

**Query recent events:**

```bash
curl "https://watchtower.local/events?hours=24&limit=50" -H "X-Admin-Api-Key: YOUR_ADMIN_KEY"

```
