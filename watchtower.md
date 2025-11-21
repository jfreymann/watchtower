# 🛡️ Watchtower

## Distributed Security Telemetry for Linux Login Monitoring

_(Collector + Agent Platform)_

Watchtower is a lightweight, secure, distributed telemetry system designed to monitor authentication activity across fleets of Linux servers. It provides real-time login visibility, centralized auditing, and hardened communication channels — all without requiring a SIEM or heavy observability stack.

Watchtower is built from two core components:

- Watchtower Collector.

  The central secured FastAPI backend that ingests, stores, and exposes login telemetry.

- Watchtower Agent

  A minimal Python daemon that tails system authentication logs and streams structured login events to the collector over hardened HTTPS.

Together, they form a portable, fully self-hosted security observability platform suitable for homelabs, enterprises, and distributed global environments.

---

### 🌐 High-Level Architecture

```bash
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

Watchtower is intentionally simple yet secure — designed for reliability in minimal environments such as air-gapped networks, remote bastion hosts, and resource-constrained servers.

---

### 🎯 Project Goals

Watchtower aims to provide:

✔ Distributed login monitoring

Every machine running the agent reports detailed login events to the collector.

✔ Security-first design

TLS everywhere, strong isolation, minimum attack surface.

✔ Zero external dependencies

SQLite for storage, Caddy for HTTPS, Python for everything else.

✔ Production-ready hardening

systemd sandboxing, locked-down filesystem access, non-root execution.

✔ Fast, structured, searchable logs

Each login event is enriched with metadata for filtering, alerting, and forensics.

---

### 🧩 Components Overview

#### 🔍 Watchtower Agent

```bash
/watchtower/agent/
```

The agent:

- Reads login activity from systemd-journald
- Extracts structured login events
- Sends them to the collector via HTTPS
- Handles retries, backoff, and recoverable errors
- Uses token-based authentication
- Runs under systemd as a sandboxed service

#### 📡 Watchtower Collector

```bash
/watchtower/collector/
```

The collector:

- Exposes /login for event ingestion
- Provides admin APIs under /events
- Authenticates agents and admins separately
- Stores structured events using SQLite
- Runs behind Caddy with internal CA TLS
- Isolated via systemd hardening

---

### 🔐 Security Model

#### Transport Security

- HTTPS enforced at all layers
- Caddy internal CA
- No plaintext endpoints

#### Authentication

- Agents authenticate with X-Login-Alert-Token
- Admins authenticate with X-Admin-Api-Key

#### Hardening

- systemd sandboxing
- Read-only filesystem
- Non-root user execution
- SQLite DB permissioned 600

#### Attack Surface

- Only /login and /healthz exposed
- /events and /admin/* IP-restricted
- uvicorn never exposed to the network

---

### 📦 Repository Structure

```bash
watchtower/
│
├── WATCHTOWER.md
│
├── watchtower/
│   ├── agent/                         # Lightweight login monitoring agent
│   │   ├── watchtower_agent.py
│   │   ├── requirements.txt
│   │   ├── .env-sample
│   │   ├── systemd/
│   │   │   └── watchtower-agent.service
│   │   └── README.md
│   │
│   └── collector/                     # Secure central collector
│       ├── main.py
│       ├── models.py
│       ├── database.py
│       ├── docker-compose.yml
│       ├── setup.sh
│       ├── requirements.txt
│       ├── systemd/
│       │   └── watchtower-collector.service
│       ├── Caddyfile.example
│       └── README.md
│
├── docs/
│   ├── index.md
│   ├── security.md
│   ├── troubleshooting.md
│   ├── watchtower.md
│   │
│   ├── architecture/
│   │   ├── components.md
│   │   ├── dataflow.md
│   │   ├── security.md
│   │   ├── overview.md
│   │   └── threat-model.md
│   │
│   ├── diagrams/
│   │   ├── watchtower-architecture.svg
│   │   ├── watchtower-dataflow.svg
│   │   └── watchtower-logo.svg
│   │
│   ├── examples/
│   │   ├── curl-queries.md
│   │   └── sample-event.json
│   │
│   └── operations/
│       ├── caddy-config.md
│       ├── hardening.md
│       ├── install-agent.md
│       ├── install-collector.md
│       ├── secure-deployment-guide.md
│       └── stig-checklist.md
│
├── bin/
│   └── watchtowerctl                # CLI helper
│
├── logs/                            # (optional)
│
└── LICENSE.md
```

---

### 📊 Data Model Summary

```bash
id
created_at
event_timestamp
hostname
user
method
source_ip
source_port
raw_message
region        ← optional
host_group    ← optional
severity      ← optional
flagged       ← anomaly/alert flag
```

---

### 🚀 Roadmap

#### Near-term:

- Web UI (React or FastAPI-Templates)
- Export formats (CSV, JSONL, Parquet)
- CLI (watchtowerctl) for event queries
- Postgres backend option

#### Medium-term:

- Multi-collector clustering
- Message queue (NATS or Redis streams)
- Webhooks per host-group
- Alerts → Slack / Discord / SMTP

#### Long-term:

- Pluggable event types (sudo, root escalation, file monitoring)
- Endpoint response workflows
- Anomaly detection engine (basic ML)

---

### 🏗️ Design Philosophy

Watchtower is built on three principles:

1. Minimum Dependencies

   - Everything should work on a tiny VM, a Raspberry Pi, or a global infrastructure cluster.

2. Zero Trust by Default

    - All components assume hostile networks.
    - Token auth, TLS, SBOM-friendly Python, constrained systemd units.

3. Operator-Centric

    - Readable logs.
    - Searchable events.
    - Simple deployment.
    - CLI friendly.
    - Git-friendly.

---

### 🧪 Testing the Platform

#### Check collector

 ```bash
 curl -k https://watchtower.local/healthz
```

#### Check agent connectivity:

```bash
sudo journalctl -u watchtower-agent -f
```

#### Retrieve latest events:

```bash
curl -k "https://watchtower.local/events?hours=1" \
  -H "X-Admin-Api-Key: YOUR_ADMIN_KEY"
```

---

### 🤝 Contributing

Contributions are welcome — from new event types, to UI, to clustering. PRs should:

- Include tests
- Pass ruff linting
- Include documentation updates
- Maintain security posture