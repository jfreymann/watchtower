# 🛡️ Watchtower

<p align="center">
  <img src="docs/diagrams/watchtower-logo.svg" alt="Watchtower logo" width="500" />
</p>

<p align="center">
  <strong>Distributed Security Telemetry for Linux Login Monitoring</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-security">Security</a> •
  <a href="#-documentation">Documentation</a>
</p>

---

## Overview

**Watchtower** is a lightweight, secure, distributed telemetry system designed to monitor authentication activity across fleets of Linux servers. It provides real-time login visibility, centralized auditing, and hardened communication channels — all without requiring a SIEM or heavy observability stack.

Watchtower is built from two core components:

- **Watchtower Agent** — A minimal Python daemon that tails system authentication logs and streams structured login events to the collector over hardened HTTPS.
- **Watchtower Collector** — The central secured FastAPI backend that ingests, stores, and exposes login telemetry.

Together, they form a portable, fully self-hosted security observability platform suitable for homelabs, enterprises, and distributed global environments.

---

## ✨ Features

### 🔐 Security-First Design
- **TLS everywhere** — Caddy reverse proxy with internal CA
- **Token-based authentication** — Separate tokens for agents and admins
- **IP-fenced admin endpoints** — Network-level access controls
- **systemd sandboxing** — `ProtectSystem=strict`, `NoNewPrivileges`, `MemoryDenyWriteExecute`
- **Minimal attack surface** — Only `/login` and `/healthz` publicly exposed

### ⚙️ Operationally Simple
- **Zero external dependencies** — SQLite for storage, Python for everything else
- **Lightweight footprint** — Agent uses ~20-30 MB memory, near-zero CPU
- **Easy deployment** — Automated installation scripts for both components
- **Production-ready** — Hardened systemd services with auto-restart

### 🧪 Forensics-Friendly
- **Structured event storage** — Queryable JSON with metadata (region, host_group, severity)
- **Real-time monitoring** — Events appear instantly in the collector
- **Flexible filtering** — Query by user, hostname, region, time range
- **Optional webhooks** — Slack notifications for critical events

---

## 🌐 Architecture

```
                        ┌────────────────────────────────────┐
                        │        Watchtower Agents           │
                        │  (SSH login watchers on each host) │
                        └───────────────┬────────────────────┘
                                        │ HTTPS + Token Auth
                                        ▼
                   ┌──────────────────────────────────────────────────────┐
                   │                  Watchtower Collector                │
                   │                                                      │
                   │  ┌──────────────────────────────────────────────┐    │
                   │  │               Caddy Reverse Proxy            │    │
                   │  │  - TLS internal CA                           │    │
                   │  │  - IP access rules                           │    │
                   │  │  - Forward to localhost uvicorn              │    │
                   │  └──────────────────────────────────────────────┘    │
                   │                                                      │
                   │  ┌──────────────────────────────────────────────┐    │
                   │  │ FastAPI Collector Service                    │    │
                   │  │ - Agent token validation                     │    │
                   │  │ - Admin API surface                          │    │
                   │  │ - Login event ingestion                      │    │
                   │  │ - SQLite datastore                           │    │
                   │  └──────────────────────────────────────────────┘    │
                   └──────────────────────────────────────────────────────┘
```

### Data Flow

1. **SSH login occurs** on a monitored Linux host
2. **journald records** the authentication event
3. **Watchtower Agent** parses the journal with regex
4. **Structured JSON event** is built with metadata
5. **Agent sends event** to collector over HTTPS with token auth
6. **Collector validates** the token and stores the event in SQLite
7. **Admins query** events via `/events` API with filtering

For detailed architecture documentation, see:
- [Architecture Overview](docs/architecture/overview.md)
- [Component Breakdown](docs/architecture/components.md)
- [Dataflow](docs/architecture/dataflow.md)

---

## 🚀 Quick Start

### Prerequisites

- Linux system with systemd
- Python 3.8+
- Caddy (for collector only)
- Root/sudo access for installation

### 1. Deploy the Collector

```bash
# Clone the repository
git clone https://github.com/jfreymann/watchtower.git
cd watchtower

# Run the collector installation script
sudo ./scripts/install-collector.sh

# Configure environment variables
sudo nano /opt/watchtower/collector/.env
# Set: LOGIN_ALERT_TOKEN, ADMIN_API_KEY, SLACK_WEBHOOK_URL (optional)

# Start the service
sudo systemctl start watchtower-collector
sudo systemctl status watchtower-collector
```

### 2. Deploy the Agent (on monitored hosts)

```bash
# Run the agent installation script
sudo ./scripts/install-agent.sh

# Configure environment variables
sudo nano /opt/watchtower/agent/.env
# Set: WATCHTOWER_COLLECTOR_URL, WATCHTOWER_TOKEN, WATCHTOWER_REGION, etc.

# Start the service
sudo systemctl start watchtower-agent
sudo systemctl status watchtower-agent
```

### 3. Verify End-to-End

```bash
# Check collector health
curl -k https://watchtower.local/healthz

# SSH into a monitored host to generate an event
ssh user@monitored-host

# Query recent events
curl -k "https://watchtower.local/events?hours=1&limit=10" \
  -H "X-Admin-Api-Key: YOUR_ADMIN_KEY"
```

---

## 📦 Installation

### Automated Installation

Use the provided installation scripts for streamlined deployment:

**Collector:**
```bash
sudo ./scripts/install-collector.sh
```

**Agent:**
```bash
sudo ./scripts/install-agent.sh
```

### Manual Installation

For detailed manual installation instructions, see:
- [Install the Collector](operations/install-collector.md)
- [Install the Agent](operations/install-agent.md)
- [Caddy Configuration](operations/caddy-config.md)

### Docker Deployment

A `docker-compose.yml` is provided for the collector:

```bash
cd collector
docker-compose up -d
```

---

## 🔒 Security

Watchtower is designed from the ground up with a defense-in-depth approach.

### Threat Model

Watchtower assumes:
- Untrusted or compromised networks
- Potentially hostile LAN traffic
- Malicious internal actors
- Replay attempts and forged event injection

### Security Controls

**Transport Security:**
- HTTPS enforced at all layers
- TLS certificates from Caddy's internal CA
- No plaintext endpoints

**Authentication:**
- Agent authentication: `X-Login-Alert-Token` header
- Admin authentication: `X-Admin-Api-Key` header
- Token rotation support via `/admin/rotate-token`

**System Hardening:**
- Both services run as non-root system users
- Aggressive systemd sandboxing
- Read-only filesystem access
- Memory execution protections

**Attack Surface:**
- Only `/login` and `/healthz` are publicly exposed
- `/events` and `/admin/*` are IP-restricted
- uvicorn never exposed to network (127.0.0.1 only)

For comprehensive security documentation, see:
- [Security Model](docs/architecture/security.md)
- [Threat Model](docs/architecture/threat-model.md)
- [Hardening Checklist](operations/hardening.md)
- [STIG Checklist](operations/stig-checklist.md)
- [Security Policy](security.md)

---

## 📡 API Reference

### Health Check
```bash
GET /healthz
```

### Ingest Login Event (Agent)
```bash
POST /login
Headers: X-Login-Alert-Token: <token>
Content-Type: application/json

{
  "type": "user_login",
  "timestamp": "2025-11-20T10:00:00Z",
  "hostname": "web-01",
  "user": "admin",
  "method": "publickey",
  "source_ip": "192.168.1.100",
  "source_port": "52345",
  "region": "us-east",
  "host_group": "prod-api"
}
```

### Query Events (Admin)
```bash
GET /events?hours=24&limit=100&user=admin&hostname=web-01
Headers: X-Admin-Api-Key: <key>
```

### Rotate Agent Token (Admin)
```bash
POST /admin/rotate-token
Headers: X-Admin-Api-Key: <key>
```

For more examples, see:
- [API Documentation](api/collector-api.md)
- [Sample Event JSON](examples/sample-event.json)
- [Curl Query Examples](examples/curl-queries.md)

---

## 🛠️ Management

### Using watchtowerctl

The `watchtowerctl` utility simplifies service management:

```bash
# View status of both services
watchtowerctl status

# Start/stop/restart services
watchtowerctl start
watchtowerctl restart

# View logs
watchtowerctl logs collector 100
watchtowerctl logs agent 50

# Tail logs in real-time
watchtowerctl tail collector
```

### systemd Management

Direct systemd commands:

```bash
# Collector
sudo systemctl status watchtower-collector
sudo journalctl -u watchtower-collector -f

# Agent
sudo systemctl status watchtower-agent
sudo journalctl -u watchtower-agent -f
```

---

## 📊 Event Data Model

Each login event includes:

| Field             | Type    | Description                          |
|-------------------|---------|--------------------------------------|
| `id`              | int     | Unique event ID                      |
| `created_at`      | datetime| Ingestion timestamp                  |
| `event_timestamp` | string  | Original event time from agent       |
| `hostname`        | string  | Server hostname                      |
| `user`            | string  | Authenticated username               |
| `method`          | string  | Auth method (publickey, password)    |
| `source_ip`       | string  | Client IP address                    |
| `source_port`     | string  | Client port                          |
| `raw_message`     | string  | Original syslog line                 |
| `region`          | string  | Optional region tag                  |
| `host_group`      | string  | Optional host group tag              |
| `severity`        | string  | Optional severity (info, high, etc.) |
| `flagged`         | bool    | Anomaly/alert flag                   |

---

## 📚 Documentation

### Architecture
- [Overview](docs/architecture/overview.md)
- [Components](docs/architecture/components.md)
- [Dataflow](docs/architecture/dataflow.md)
- [Security Model](docs/architecture/security.md)
- [Threat Model](docs/architecture/threat-model.md)

### Operations
- [Install Collector](operations/install-collector.md)
- [Install Agent](operations/install-agent.md)
- [Caddy Configuration](operations/caddy-config.md)
- [Hardening Guide](operations/hardening.md)
- [Secure Deployment](operations/secure-deployment-guide.md)
- [STIG Checklist](operations/stig-checklist.md)

### API & Examples
- [Collector API Reference](api/collector-api.md)
- [Sample Event JSON](examples/sample-event.json)
- [Curl Query Examples](examples/curl-queries.md)

### Troubleshooting
- [Troubleshooting Guide](troubleshooting.md)

---

## 🧭 Roadmap

### Near-term
- [ ] Web UI (React or FastAPI-Templates)
- [ ] Export formats (CSV, JSONL, Parquet)
- [ ] CLI enhancements for `watchtowerctl`
- [ ] PostgreSQL backend option
- [ ] Failed login detection

### Medium-term
- [ ] Multi-collector clustering
- [ ] Message queue integration (NATS or Redis streams)
- [ ] Per-host-group webhooks
- [ ] Slack/Discord/SMTP alerting
- [ ] sudo elevation monitoring

### Long-term
- [ ] Pluggable event types (file monitoring, process anomalies)
- [ ] Endpoint response workflows
- [ ] Anomaly detection engine (basic ML)
- [ ] GeoIP and ASN enrichment
- [ ] SIEM integration (Splunk, ELK, Wazuh)

---

## 🤝 Contributing

Contributions are welcome! Whether it's new event types, UI improvements, or clustering features.

**Important:** By contributing, you agree that your contributions will be licensed under the Watchtower Community License 1.0.

**PRs should:**
- Include tests where applicable
- Pass linting (ruff, black, or equivalent)
- Include documentation updates
- Maintain the security posture
- Include proper copyright headers

**Before submitting:**
1. Review the [Security Policy](security.md)
2. Review the [Licensing Guide](docs/licensing-guide.md)
3. Check existing issues and PRs
4. Open an issue for discussion on major changes

---

## 🏗️ Design Philosophy

Watchtower is built on three principles:

### 1. Minimum Dependencies
Everything should work on a tiny VM, a Raspberry Pi, or a global infrastructure cluster.

### 2. Zero Trust by Default
All components assume hostile networks. Token auth, TLS, SBOM-friendly Python, constrained systemd units.

### 3. Operator-Centric
Readable logs, searchable events, simple deployment, CLI-friendly, Git-friendly.

---

## 📜 License

Watchtower is released under the **Watchtower Community License 1.0**.

### License Summary

- ✅ **Permitted:** Personal use, internal business use, viewing and modifying source code
- ❌ **Prohibited:** Commercial use, redistribution, SaaS hosting, competitive products
- 💼 **Commercial licensing available** for enterprise use, redistribution, or SaaS deployment

**Key Restrictions:**
- No redistribution of the software or modified versions
- No commercial use without a valid commercial license
- No offering Watchtower as a hosted/SaaS service
- No use in competing monitoring or security products
- Attribution and copyright notices must be preserved

**Commercial License:**
For commercial usage, redistribution rights, SaaS hosting, enterprise deployment, or integration into paid products, contact **jfreymann@gmail.com** for licensing options.

See [LICENSE.md](LICENSE.md) for complete terms.

---

## 🙏 Acknowledgments

Built with a focus on security, simplicity, and operational excellence.

Special thanks to the open-source community for tools like FastAPI, Caddy, and SQLAlchemy that make projects like this possible.

---

## 📧 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/jfreymann/watchtower/issues)
- **Security:** See [Security Policy](security.md) for responsible disclosure
- **Discussions:** [GitHub Discussions](https://github.com/jfreymann/watchtower/discussions)

---

<p align="center">
  Made with ❤️ for security operators everywhere
</p>
