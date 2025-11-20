# 🛡️ Watchtower Security Model

Watchtower is designed from the ground up with a defense-in-depth approach.
Both the Agent and Collector are intentionally minimal, sandboxed, authenticated, strongly encrypted, and hardened for hostile environments.

This document details the complete security posture of the Watchtower platform.

---

### 🔐 1. Threat Model

**Watchtower assumes the following adversarial conditions:**

- Untrusted or compromised networks
- Potentially hostile LAN traffic
- Malicious internal actors
- Compromised client machines
- Replay attempts, spoofing attempts, forged event injection
- Attempted database tampering

**Watchtower does not assume:**

- The Collector host is compromised
- systemd is compromised
- TLS termination (Caddy) is compromised
- The attacker has access to /opt/watchtower/collector/.env

## The system is designed to minimize attack surface such that:**

- A rogue agent cannot impersonate another
- The Collector is not reachable without TLS & tokens
- Admin endpoints are protected by both credentials and network location

## 🔒 2. Transport Security

### ✔ TLS Everywhere

All traffic between Agents and Collector is encrypted via HTTPS.
TLS is terminated by **Caddy** using:

```bash
tls internal
```

#### This provides:

- A private CA
- Auto-renewing, short-lived certs
- No external certificate dependencies
- Perfect for LAN and on-prem deployments

#### The Collector itself never exposes plain HTTP externally.

### ✔ No direct exposure of uvicorn

uvicorn is bound to:

```bash
127.0.0.1:8000
```

Meaning only Caddy can reach it.

Agents connect exclusively to the HTTPS surface handled by Caddy.


## 🧪 3. Authentication Model

### ✔ Agent Authentication (X-Login-Alert-Token)

All agents must provide:

```bash
X-Login-Alert-Token: <token>
```

Requests without a valid token are instantly rejected.

Properties of the token mechanism:

- 43+ character random string (256-bit entropy)
- Stored server-side in SQLite & .env
- Never logged in plaintext
- Same token may be shared among multiple agents (optional)
- Invalid tokens produce generic 401 Unauthorized messages

### ✔ Admin Authentication (X-Admin-Api-Key)

Admin endpoints require:

```bash
X-Admin-Api-Key: <key>
```

This key is unrelated to the agent token and is kept strictly separate.

Access control is implemented at two layers:

1. Application layer – FastAPI requires the admin header
2. Network layer – Caddy IP-restricts admin endpoints


## 🚧 4. Network-Level Access Controls (Caddy)

**Caddy enforces IP fences for sensitive surfaces.**

Example:

```bash
@admin_protected {
    path /events*
    path /admin/*
    not remote_ip 192.168.1.188/32
}
respond @admin_protected "Forbidden" 403
```

Benefits:

- No accidental exposure of admin API
- Even with a leaked admin key, requests must originate from trusted IP
- Admin panels effectively become “intranet only”

## 🧱 5. System Hardening (systemd)

Both the Agent and Collector are deployed with strict systemd sandboxes:

| Feature                       | Purpose                                 |
| ----------------------------- | --------------------------------------- |
| `NoNewPrivileges=yes`         | Prevents privilege escalation           |
| `ProtectSystem=strict`        | Mounts system dirs read-only            |
| `ProtectHome=true`            | Prevents access to user home dirs       |
| `PrivateTmp=true`             | Prevents temp directory snooping        |
| `MemoryDenyWriteExecute=true` | Blocks memory injection attacks         |
| `RestrictSUIDSGID=true`       | Prevents setuid binaries from elevation |
| `ProtectKernelTunables=true`  | Blocks kernel parameter changes         |
| `ProtectKernelModules=true`   | Prevents module loading                 |
| `LockPersonality=yes`         | Prevents changing system ABI            |

Both processes run under dedicated, non-login system users:

```bash
watchtower/agent
watchtower/collector
```

**No root access.**

**No shell access.**

**No ability to write outside their directory.**

## 📦 6. Secrets & Filesystem Protection

```bash
chmod 600
chown chown watchtower:watchtower
```

This prevents:

- Log scraping
- Key harvesting
- Privilege escalation via writable configs

### ✔ SQLite Database

SQLite DB is stored at:

```bash
/var/lib/watchtower/watchtower.db
```

Permissions:
```bash
chmod 600
chown watchtower:watchtower
```

The Collector user is the only process allowed to read/write.

### ✔ No writable code paths

Systemd enforces read-only access to application code.

## 📦 7. Event Validation & Ingestion Hardening

Incoming event JSON is validated using Pydantic schemas that:

- Require proper event structure
- Reject malformed or missing fields
- Prevent SQL injection vectors
- Remove unexpected fields
- Normalize timestamps

All ingestion endpoints:

- Reject empty payloads
- Reject oversized payloads
- Reject invalid headers
- Reject unknown fields

No raw passthrough is allowed.


## 🗃 8. Logging & Audit Controls

Collector logs include:

- Agent connection attempts
- Token validation failures
- Admin queries (without exposing data)
- System errors
- Event ingestion failures

Agents log:

- TLS errors
- Network failures
- Journal parsing issues
- Retries & backoff state

Crucially:

- Tokens and API keys are never printed
- Raw events are not logged by default

## 🚫 9. Attack Surface

The externally exposed surface is extremely small:

### Public endpoints:

| Endpoint   | Method | Purpose                |
| ---------- | ------ | ---------------------- |
| `/login`   | POST   | Agent event ingestion  |
| `/healthz` | GET    | Collector health probe |

### Privileged admin endpoints:

| Endpoint   | Method   | Gate                     |
| ---------- | -------- | ------------------------ |
| `/events`  | GET      | Admin API key + IP fence |
| `/admin/*` | GET/POST | Admin-only               |


#### **Not exposed:**

- uvicorn interface
- SQLite DB
- systemd APIs
- local filesystem
- journald on agents

## 🛡 10. Failure Modes & Safety Nets

### ✔ Invalid TLS cert → Agent refuses to connect

### ✔ Invalid token → Collector rejects event

### ✔ Caddy failure → Collector not reachable externally

### ✔ DB unavailable → Collector refuses writes, logs error

### ✔ Agent failure → systemd auto-restarts

### ✔ Collector failure → systemd auto-restarts

### ✔ Permissions misconfig → startup failure (safe)

### ✔ Bad payload → 422 with no processing

No silent failures.

## 🔍 11. Security Philosophy

Watchtower is intentionally:

- Small → easier to secure
- Sandboxed → harder to exploit
- Token-validated → no anonymous ingestion
- TLS-protected → safe on hostile networks
- Operator-first → readable errors, simple configs

Every line of this system was written with the same questions:

- Is this necessary?
- Does this enlarge the attack surface?
- Can we harden it further?
- What happens if it fails?

## 📜 12. Summary

**Watchtower provides:**

- End-to-end TLS encryption
- Token-based authentication
- IP-fenced admin surfaces
- Strong systemd sandboxing
- Protected secrets
- Validated event ingestion
- Minimal externally exposed endpoints

**It is a secure-by-default platform suitable for:**

- Homelabs
- Production servers
- Global distributed fleets
- Air-gapped networks
- Enterprise SOC pipelines

Watchtower’s security model emphasizes containment, verification, and minimalism, ensuring it remains safe even in hostile environments.
