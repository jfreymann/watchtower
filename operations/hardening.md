# Hardening Checklist

This checklist ensures Watchtower is deployed securely.

## ✔ System Users

- [ ] watchtower/agent created as nologin user
- [ ] watchtower/collector created as nologin user

## ✔ Filesystem

- [ ] `/opt/watchtower/collector/.env` is mode 600
- [ ] `/opt/watchtower/agent/.env` is mode 600
- [ ] SQLite DB owned by watchtower/collector
- [ ] No writable dirs exposed

## ✔ systemd Hardening

Both agent and collector have:

- [ ] NoNewPrivileges
- [ ] PrivateTmp
- [ ] ProtectSystem=strict
- [ ] ProtectHome
- [ ] MemoryDenyWriteExecute
- [ ] LockPersonality

## ✔ TLS

- [ ] Caddy configured with `tls internal`
- [ ] Agents trust internal CA
- [ ] No HTTP endpoint exposed

## ✔ Network

- [ ] uvicorn bound to 127.0.0.1 only
- [ ] Caddy IP fences admin APIs
- [ ] No extraneous ports exposed
