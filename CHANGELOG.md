# Changelog

All notable changes to Watchtower will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-01-20

### 🎉 Initial Production Release

The first stable release of Watchtower - a distributed security telemetry system for monitoring SSH login activity across Linux server fleets.

### Added

#### Core Components
- **Watchtower Agent** - Lightweight Python daemon for SSH login monitoring
  - Real-time journald log parsing via `journalctl`
  - Structured JSON event generation
  - Token-based authentication with collector
  - Automatic retry with exponential backoff
  - systemd service with security hardening
  - Support for metadata tagging (region, host_group, severity)

- **Watchtower Collector** - Central FastAPI service for event ingestion
  - `/login` endpoint for agent event submission
  - `/events` endpoint for admin querying with filters
  - `/admin/rotate-token` endpoint for token rotation
  - SQLite database with WAL mode
  - Token-based dual authentication (agent + admin)
  - Optional Slack webhook notifications
  - systemd service with security hardening

#### Security Features
- HTTPS/TLS enforcement via Caddy reverse proxy
- Token-based authentication for agents and admins
- IP-based access controls for admin endpoints
- systemd sandboxing (`ProtectSystem=strict`, `NoNewPrivileges`, `MemoryDenyWriteExecute`)
- Read-only filesystem mounting
- Non-root service execution
- SQLite database with strict permissions (600)

#### Deployment Options
- **Bare Metal** - Manual installation with systemd services
- **Docker** - Multi-stage production Dockerfiles
  - Collector with Caddy reverse proxy
  - Agent with journald access
  - Docker Compose configurations
  - Security-hardened containers
- **Automated Scripts** - Installation scripts for both components

#### Documentation
- Comprehensive README with architecture diagrams
- Installation guides (bare metal + Docker)
- Security model and threat analysis
- API reference documentation
- Troubleshooting guide
- Deployment best practices
- STIG compliance checklist

#### Licensing
- **Watchtower Community License 1.0** - Source-available, non-commercial
- Commercial licensing options for enterprises
- Contribution guidelines with CLA
- Copyright headers on all source files

#### Management Tools
- `watchtowerctl` - CLI utility for service management
- Status checking, log tailing, service restart
- Support for both collector and agent

### Technical Specifications

#### Agent
- **Language:** Python 3.12+
- **Dependencies:** requests, certifi
- **Memory:** ~20-30 MB
- **CPU:** Near-zero utilization
- **Supported Auth Methods:** publickey, password, keyboard-interactive

#### Collector
- **Language:** Python 3.12+
- **Framework:** FastAPI + Uvicorn
- **Database:** SQLite (with optional PostgreSQL roadmap)
- **Dependencies:** FastAPI, SQLAlchemy, Pydantic, Requests
- **Reverse Proxy:** Caddy 2 with internal CA

#### Event Data Model
- `id`, `created_at`, `event_timestamp`
- `hostname`, `user`, `method`
- `source_ip`, `source_port`
- `raw_message`
- `region`, `host_group`, `severity`, `flagged`

### Security Considerations

- All communication over HTTPS
- No plaintext credentials in code
- Environment-based configuration
- Minimal attack surface (only `/login` and `/healthz` public)
- Admin endpoints IP-restricted
- Comprehensive systemd hardening
- Regular security updates planned

### Known Limitations

- SQLite-only database backend (PostgreSQL planned)
- No web UI (planned for future release)
- Single collector architecture (clustering planned)
- No failed login detection yet (planned)
- Agent requires journald access (systemd dependency)

### Roadmap Highlights

**Near-term:**
- Web UI (React/FastAPI-Templates)
- Export formats (CSV, JSONL, Parquet)
- Failed login detection
- PostgreSQL backend support

**Medium-term:**
- Multi-collector clustering
- Message queue integration (NATS/Redis)
- Enhanced alerting (Slack, Discord, SMTP)
- sudo elevation monitoring

**Long-term:**
- Anomaly detection engine
- GeoIP enrichment
- SIEM integration
- Pluggable event types

---

## Release Notes

### Upgrade Instructions

This is the initial release. No upgrade path required.

### Breaking Changes

None - initial release.

### Deprecations

None - initial release.

---

## Versioning

Watchtower follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

---

## License

Released under the Watchtower Community License 1.0.
See [LICENSE.md](LICENSE.md) for details.

For commercial licensing: jfreymann@gmail.com

---

[1.0.0]: https://github.com/jfreymann/watchtower/releases/tag/v1.0.0
