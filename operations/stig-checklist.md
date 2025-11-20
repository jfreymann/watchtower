# Watchtower STIG Checklist

This document outlines a STIG-style hardening checklist for deploying Watchtower securely.

---

# ✔ Section 1 — File & Directory Permissions

| Check | Status |
|-------|--------|
| `/opt/watchtower/collector` owned by `watchtower/collector` | ☐ |
| `/opt/watchtower/agent` owned by `watchtower/agent` | ☐ |
| `.env` files mode `600` | ☐ |
| `watchtower.db` mode `600` | ☐ |
| No writable files in code directories | ☐ |
| systemd unit files mode `644` | ☐ |

---

# ✔ Section 2 — systemd Hardening

| Control | Required | Status |
|--------|----------|--------|
| `NoNewPrivileges=yes` | Yes | ☐ |
| `ProtectSystem=strict` | Yes | ☐ |
| `ProtectHome=true` | Yes | ☐ |
| `PrivateTmp=true` | Yes | ☐ |
| `MemoryDenyWriteExecute=true` | Yes | ☐ |
| `RestrictSUIDSGID=true` | Yes | ☐ |
| `ProtectControlGroups=true` | Yes | ☐ |
| `ProtectKernelModules=true` | Yes | ☐ |
| `ProtectKernelTunables=true` | Yes | ☐ |
| `LockPersonality=yes` | Yes | ☐ |
| Non-root service user | Yes | ☐ |

---

# ✔ Section 3 — TLS & Networking

| Check | Status |
|-------|--------|
| Caddy running with `tls internal` | ☐ |
| uvicorn bound to `127.0.0.1:8000` | ☐ |
| Admin endpoints IP-restricted | ☐ |
| No HTTP listeners | ☐ |
| Firewall restricts inbound ports (80/443 only) | ☐ |

---

# ✔ Section 4 — Authentication

| Check | Status |
|-------|--------|
| Agent token is 256-bit random | ☐ |
| Admin API key stored securely | ☐ |
| No tokens printed in logs | ☐ |
| Token not embedded in code | ☐ |

---

# ✔ Section 5 — Application Integrity

| Check | Status |
|-------|--------|
| Pydantic validation enabled | ☐ |
| Event ingestion rejects unknown fields | ☐ |
| DB auto-migration on startup disabled | ☐ |
| Logging excludes sensitive values | ☐ |

---

# ✔ Section 6 — Monitoring & Health

| Check | Status |
|-------|--------|
| `/healthz` returns "ok" | ☐ |
| Agent journald logs monitored | ☐ |
| Alerts configured (optional webhook) | ☐ |

---

# ✔ Section 7 — Backup & Recovery

| Check | Status |
|-------|--------|
| SQLite DB backed up regularly | ☐ |
| .env values backed up | ☐ |
| Collector can restart cleanly | ☐ |

---

# ✔ Full Compliance Score

| Category | Score |
|----------|--------|
| Filesystem | /6 |
| systemd Hardening | /11 |
| TLS & Networking | /5 |
| Authentication | /4 |
| Application Integrity | /4 |
| Monitoring & Health | /3 |
| Backup & Recovery | /3 |

Total: **0 / 36** → *(fill during deployment)*

