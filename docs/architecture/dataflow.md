# Dataflow

This document describes the flow of authentication events from source system to the collector.

---

## Step-by-Step Flow

### 1. SSH login occurs

A user authenticates using publickey or password.

### 2. journald records the event

Entries appear in the `ssh.service` unit.

### 3. Watchtower Agent parses the journal

Regex + metadata extraction produce:

- timestamp
- hostname
- username
- authentication method
- source IP/port
- raw log line

### 4. Agent builds structured JSON

Example:

```json
{
  "type": "login",
  "user": "admin",
  "method": "publickey",
  "source_ip": "203.0.113.55",
  "hostname": "bastion-1",
  "timestamp": "2025-05-12T13:44:22Z"
}
```

### 5. Agent sends event to collector over HTTPS

#### Authenticated with:

```bash
X-Login-Alert-Token: <token>
```

### 6. Collector validates token

Unauthorized agents are rejected.

### 7. Event is written to SQLite

Enriched metadata is applied (region, host_group, etc).

### 8. Admins retrieve data via /events

Filtered by hours=, limit=, etc.

## 🔐 Security Model

Watchtower is designed with a defense-first mindset.

### Transport Security

- HTTPS enforced at all layers.
- TLS certificates provided by Caddy's internal CA.
- No plaintext endpoints.


### Authentication

#### **Agent Authentication**

Agents authenticate using a shared token sent via:

```bash
X-Login-Alert-Token
```

#### **Admin Authentication**

```bash
Admin-only APIs require:
```

#### **Token Storage**

```bash
Tokens are loaded from `/opt/watchtower/collector/.env`
Permissions restricted to the `watchtower/collector` user only.
```

### System Hardening

Both services use aggressive systemd hardening:

- `ProtectSystem=strict`
- `ProtectHome=true`
- `NoNewPrivileges=yes`
- `MemoryDenyWriteExecute=true`
- `PrivateTmp=true`
- Non-root users for both agent and collector

### Attack Surface

- Only `/login` and `/healthz` are publicly accessible.
- `/events` and `/admin/*` are IP-fenced using Caddy.
- uvicorn is *never* exposed (runs locally on 127.0.0.1).

