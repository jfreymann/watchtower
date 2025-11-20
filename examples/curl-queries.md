# Useful curl Queries

---

## Test collector health

```bash
curl -k https://watchtower.local/healthz
```

## Query last 1 hour of events

```bash
curl -k "https://watchtower.local/events?hours=1&limit=50" \
  -H "X-Admin-Api-Key: <ADMIN_KEY>"
```

## Send a test login event manually

```bash
curl -k -X POST https://watchtower.local/login \
  -H "Content-Type: application/json" \
  -H "X-Login-Alert-Token: <TOKEN>" \
  -d @sample-event.json
```
