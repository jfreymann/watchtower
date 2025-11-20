# Architecture Overview

Watchtower is composed of two primary components:

- **Watchtower Agent** – a lightweight daemon running on each Linux host.
- **Watchtower Collector** – a central FastAPI service that receives login events over HTTPS.

The design focuses on simplicity, security, and low operational overhead.


## High-Level Diagram

```bash
              ┌────────────────────────────┐
              │    Watchtower Agents       │
              │ (login telemetry producers)│
              └────────────┬───────────────┘
                           │ HTTPS + token
                           ▼
         ┌──────────────────────────────────────────┐
         │            Watchtower Collector          │
         │------------------------------------------│
         │  Caddy TLS proxy → FastAPI backend → DB  │
         └──────────────────────────────────────────┘
```


## Key Goals

### ✔ Secure by default

TLS, token authentication, sandboxed services.

### ✔ Minimal dependencies

SQLite + Python everywhere.

### ✔ Easy deployment

Works on any Linux distribution with systemd.

### ✔ Structured telemetry

Normalized event structure supports filtering, forensics, and anomaly detection.
