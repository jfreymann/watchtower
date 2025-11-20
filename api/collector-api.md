# Collector API Reference

This document covers APIs exposed by the Watchtower Collector.

---

## Health Check

### GET /healthz


Response:

```json
{"status": "ok"}
```

### Ingest Login Event

```json
POST /login
```

### Authentication:

```json
X-Login-Alert-Token: <token>
```

Payload:
See Schemas.md

---

### Query Events (Admin)

```bash
GET /events?hours=<int>&limit=<int>
```

Authentication:

```bash
X-Admin-Api-Key: <key>
```

Example:

```bash
curl -k "https://watchtower.local/events?hours=12&limit=50" \
  -H "X-Admin-Api-Key: MYKEY"
```
