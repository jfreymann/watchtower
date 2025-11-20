# Component Breakdown

## Watchtower Agent

### The agent:

- Reads login activity from journald.
- Extracts structured authentication events.
- Sends data to the collector with retries + exponential backoff.
- Runs under systemd with strong hardening.
- Uses a single authentication token.

It intentionally does *not* store logs locally — all critical data is sent upstream.

## Watchtower Collector

### The collector:

- Accepts login events via `/login`.
- Validates agent tokens.
- Stores events in SQLite.
- Exposes admin APIs for querying.
- Runs behind a Caddy HTTPS reverse proxy.
- Is heavily sandboxed under systemd.


## Caddy Reverse Proxy

### Caddy provides:

- HTTPS w/ internal CA (no Let's Encrypt needed).
- IP fencing of sensitive endpoints.
- Reverse proxying to uvicorn.
- Automatic TLS renewal & certificate management.

