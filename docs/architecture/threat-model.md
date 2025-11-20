# Threat Model for Watchtower

This document defines the threat model for the Watchtower platform using a STRIDE-aligned framework. Watchtower is designed for hostile networks, multi-tenant environments, and adversarial internal actors.


## 🎯 Assets

### Primary Assets

- Integrity of login telemetry
- Confidentiality of authentication data
- Availability of the collector service
- Agent integrity and authenticity
- Token and API key secrecy
- Database integrity (`login_events`)

### Secondary Assets

- Network metadata
- Journald-derived logs
- System identity (hostname, region, host_group)

## 👤 Actors

### Legitimate Actors

- Watchtower Agents installed on Linux hosts
- Watchtower Collector service
- Privileged administrators accessing the `/events` API

### Adversarial Actors

- Malicious internal user
- External attacker on same network segment
- Rogue agent attempting to impersonate another device
- Compromised host attempting forged event injection
- Adversary with packet interception capabilities
- Botnets scanning HTTPS endpoints


## 🧨 STRIDE Analysis

### ✔ Spoofing

**Threat:** Rogue agent attempts to submit events.

**Controls:**

- Token-based agent authentication
- Token is never logged
- Admin APIs require API key
- IP fencing for admin surfaces
- TLS certificates validate server identity

**Residual risk:** Token leakage from filesystem compromise.

### ✔ Tampering

**Threat:** Forging or modifying login events in transit.

**Controls:**

- HTTPS only (TLS)
- Pydantic validation rejects malformed data
- SQLite is write-protected (600)
- systemd sandboxing prevents agent or collector from being modified

**Residual risk:** Compromised agent host can send malicious (but authenticated) events.

### ✔ Repudiation

**Threat:** Actor denies submitting or querying events.

**Controls:**

- Collector logs authentication failures
- systemd logs all service activity
- Admin API requests traced by IP
- Optional webhook alerts for critical events

**Residual risk:** Collector does not maintain immutable logs (future roadmap: append-only storage).

### ✔ Information Disclosure

**Threat:** Sensitive login data leaked.

**Controls:**

- TLS encryption for all traffic
- Strict `.env` and DB permissions
- systemd protections prevent reading other directories
- Admin endpoints require API key and IP whitelist

**Residual risk:** Access to sqlite DB or `.env` compromises tokens.

### ✔ Denial of Service

**Threat:** Flooding `/login` endpoint or overloading collector.

**Controls:**

- systemd auto-restart
- uvicorn worker isolation
- SQLite is lightweight and resilient
- Ingress is only through Caddy, which can add rate limiting (optional)

**Residual risk:** Severe network flooding may block agent → collector communication.

### ✔ Elevation of Privilege

**Threat:** Agent or collector escalates to root.

**Controls:**

- Both run under non-root system users
- `NoNewPrivileges=yes`
- `ProtectSystem=strict`
- `RestrictSUIDSGID=true`
- `MemoryDenyWriteExecute=true`

**Residual risk:** OS 0-day permitting sandbox breakthrough.

## 📌 Summary

Watchtower has strong controls against:

- Spoofing
- MitM tampering
- Event forgery
- Unauthorized event access
- Privilege escalation
- Secret exposure
- Admin API misuse

Remaining residual risks relate to:

- Host compromise
- Token leakage
- Misconfigured TLS reverse proxy
- Large-scale network DoS

All residual risks are typical for distributed security telemetry systems.
