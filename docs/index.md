# 🛡 Watchtower

<p align="center">
  <img src="diagrams/watchtower-logo.svg" alt="Watchtower logo" width="500" />
</p>

**Watchtower** is a lightweight, self-hosted security telemetry platform for monitoring SSH logins across fleets of Linux servers.

It consists of two main components:

- **Watchtower Agent** – runs on each host, tails authentication logs, and sends structured events.
- **Watchtower Collector** – central FastAPI service behind HTTPS that ingests, stores, and exposes login telemetry.

Watchtower is designed to be:

- 🔐 **Security-first** – TLS everywhere, token auth, systemd hardening
- ⚙️ **Operationally simple** – no heavy external dependencies, just Python + SQLite + Caddy
- 🧪 **Forensics-friendly** – structured, queryable event history for investigations

---

## 🌐 Architecture

At a high level:

- Agents watch `ssh.service` logs (via `journalctl`)
- Successful SSH logins are converted into structured JSON events
- Events are sent over HTTPS to the Watchtower Collector
- The Collector validates tokens, stores events, and exposes APIs for querying
- Caddy terminates TLS and fences off sensitive endpoints

You can view more detailed diagrams here:

- [Architecture Overview](architecture/overview.md)
- [Dataflow](architecture/dataflow.md)
- [Security Model](architecture/security.md)

---

## 🧩 Components

### Watchtower Agent

- Tails journald (`ssh.service`)
- Extracts username, method, source IP/port, hostname, timestamp, raw message
- Sends events over HTTPS using a shared token
- Runs as a non-root systemd service with strong sandboxing

📄 Documentation: [Install the Agent](operations/install-agent.md)

---

### Watchtower Collector

- FastAPI application running behind Caddy
- Accepts events at `/login` (authenticated with `X-Login-Alert-Token`)
- Stores events in SQLite for easy backup and portability
- Exposes `/events` (admin-only) for querying login history
- Uses systemd hardening and a dedicated service user

📄 Documentation: [Install the Collector](operations/install-collector.md)
📡 API Reference: [Collector API](api/collector-api.md)

---

## 🛠 Getting Started

1. **Deploy the Collector**
   - Install Python + Caddy
   - Deploy the FastAPI app to `/opt/watchtower/collector`
   - Configure `.env` with `ADMIN_API_KEY` and `WATCHTOWER_AGENT_TOKEN`
   - Enable `watchtower/collector.service`
   - Configure Caddy with TLS + reverse proxy

2. **Deploy the Agent on each host**
   - Install Python
   - Deploy `watchtower_agent.py` to `/opt/watchtower/agent`
   - Configure `.env` with `WATCHTOWER_COLLECTOR_URL` and the agent token
   - Enable `watchtower/agent.service`

3. **Verify end-to-end**
   - Hit `/healthz` on the collector
   - SSH into a monitored host
   - Query `/events` from the collector and confirm a new login event appears

Step-by-step guides:

- [Install the Collector](operations/install-collector.md)
- [Install the Agent](operations/install-agent.md)
- [Caddy Configuration](operations/caddy-config.md)

---

## 🔒 Security Highlights

- HTTPS everywhere (Caddy internal CA)
- Token-based auth for both agents and admins
- uvicorn bound to `127.0.0.1` only; Caddy is the only public face
- systemd sandboxing (`ProtectSystem=strict`, `NoNewPrivileges`, `MemoryDenyWriteExecute`, etc.)
- Minimal attack surface: only `/login` and `/healthz` are externally available

More details: [Security Model](architecture/security.md)
Hardening checklist: [Hardening Checklist](operations/hardening.md)

---

## 🧪 Examples

- [Sample Login Event JSON](examples/sample-event.json)
- [Useful curl queries](examples/curl-queries.md)

---

## 🚧 Roadmap

Planned features include:

- Failed login / brute-force detection
- sudo elevation monitoring
- Web UI for search & dashboards
- Optional Postgres backend
- Streaming integrations (SIEM / message queues)

See the main project overview for more:
[WATCHTOWER.md](../watchtower.md)

---

## 📜 License

Watchtower is released under the MIT License.
