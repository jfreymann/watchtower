# Docker Deployment Guide

This guide covers deploying Watchtower using Docker and Docker Compose.

---

## Overview

Watchtower provides three deployment options:

1. **Collector Only** - Deploy just the collector (most common)
2. **Agent Only** - Deploy just the agent on monitored hosts
3. **Complete Stack** - Deploy both collector and agent together

---

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Linux host with systemd (for agent)
- Root/sudo access

---

## Option 1: Collector Only

### Setup

```bash
cd collector

# Copy environment template
cp .env.docker.example .env

# Edit configuration
nano .env
```

Update the following in `.env`:
```bash
ADMIN_API_KEY=your-secure-admin-key-here
LOGIN_ALERT_TOKEN=your-secure-agent-token-here
WATCHTOWER_DOMAIN=watchtower.yourdomain.com
ADMIN_IP=192.168.1.0/24
```

### Deploy

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f collector
docker-compose logs -f caddy
```

### Verify

```bash
# Health check
curl -k https://localhost/healthz

# Should return: {"status":"ok"}
```

### Access

- **Health endpoint:** `https://watchtower.yourdomain.com/healthz`
- **Login endpoint:** `https://watchtower.yourdomain.com/login` (agents)
- **Events API:** `https://watchtower.yourdomain.com/events` (admins only)

---

## Option 2: Agent Only

### Setup

```bash
cd agent

# Copy environment template
cp .env.docker.example .env

# Edit configuration
nano .env
```

Update the following in `.env`:
```bash
WATCHTOWER_COLLECTOR_URL=https://watchtower.yourdomain.com/login
WATCHTOWER_TOKEN=your-agent-token-here
WATCHTOWER_REGION=us-east
WATCHTOWER_HOST_GROUP=production
WATCHTOWER_VERIFY_TLS=false  # If using internal CA
```

### Deploy

```bash
# Build and start agent
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agent
```

### Important Notes

**Journald Access:**
The agent requires access to the host's journald to monitor SSH logins. The container mounts:
- `/var/log/journal` (read-only)
- `/run/systemd/journal` (read-only)

**Network Mode:**
The agent uses `network_mode: host` to access the host's journal. This is required for journalctl access.

---

## Option 3: Complete Stack

Deploy both collector and agent on a single host.

### Setup

```bash
# From repository root
cp .env.example .env

# Edit configuration
nano .env
```

Set all required variables:
```bash
# Collector
ADMIN_API_KEY=your-admin-key
LOGIN_ALERT_TOKEN=your-agent-token
WATCHTOWER_DOMAIN=watchtower.local
ADMIN_IP=192.168.1.0/24

# Agent
WATCHTOWER_COLLECTOR_URL=https://localhost/login
WATCHTOWER_TOKEN=your-agent-token
WATCHTOWER_REGION=docker
WATCHTOWER_HOST_GROUP=local
WATCHTOWER_VERIFY_TLS=false
```

### Deploy

```bash
# Start collector and Caddy (without agent)
docker-compose up -d collector caddy

# Or start complete stack with agent
docker-compose --profile with-agent up -d

# Check status
docker-compose ps
```

---

## Configuration Details

### Collector Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOGIN_ALERT_TOKEN` | Yes | - | Agent authentication token |
| `ADMIN_API_KEY` | Yes | - | Admin API key |
| `SLACK_WEBHOOK_URL` | No | - | Optional Slack webhook |
| `WATCHTOWER_DOMAIN` | No | `watchtower.local` | Domain for Caddy |
| `ADMIN_IP` | No | `192.168.1.0/24` | Admin IP whitelist |

### Agent Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WATCHTOWER_COLLECTOR_URL` | Yes | - | Collector endpoint |
| `WATCHTOWER_TOKEN` | Yes | - | Agent token |
| `WATCHTOWER_REGION` | No | - | Region tag |
| `WATCHTOWER_HOST_GROUP` | No | - | Host group tag |
| `WATCHTOWER_SEVERITY` | No | `info` | Event severity |
| `WATCHTOWER_VERIFY_TLS` | No | `true` | TLS verification |
| `WATCHTOWER_SSH_UNIT` | No | `ssh.service` | systemd unit to monitor |

---

## Volume Management

### Collector Volumes

- **watchtower-data** - SQLite database storage
- **caddy-data** - Caddy certificates and data
- **caddy-config** - Caddy configuration

### Backup Database

```bash
# Create backup
docker-compose exec collector sqlite3 /var/lib/watchtower/watchtower.db ".backup /tmp/backup.db"
docker cp watchtower-collector:/tmp/backup.db ./watchtower-backup-$(date +%Y%m%d).db

# Restore from backup
docker cp ./watchtower-backup.db watchtower-collector:/tmp/restore.db
docker-compose exec collector sqlite3 /var/lib/watchtower/watchtower.db ".restore /tmp/restore.db"
```

---

## Network Configuration

### Collector Network

- **Network:** `watchtower-net` (172.28.0.0/16)
- **Exposed ports:** 443 (HTTPS), 80 (HTTP redirect)
- **Internal:** Collector only accessible via Caddy

### Agent Network

- **Network mode:** `host`
- **Reason:** Required for journalctl access

---

## Security Considerations

### Container Hardening

Both containers implement:
- Non-root user execution
- Read-only filesystem
- No new privileges
- Resource limits
- Minimal capabilities

### Collector Security

```yaml
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp:noexec,nosuid,size=64M
```

### Caddy Security

```yaml
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE  # Required for ports 80/443
```

---

## Troubleshooting

### Collector won't start

```bash
# Check logs
docker-compose logs collector

# Common issues:
# - Missing environment variables
# - Database permission issues
# - Port conflicts
```

### Agent can't access journald

```bash
# Verify journal mounts
docker-compose exec agent ls -la /var/log/journal

# Check permissions
ls -la /var/log/journal
```

### Caddy TLS issues

```bash
# Check Caddy logs
docker-compose logs caddy

# Verify Caddyfile
docker-compose exec caddy cat /etc/caddy/Caddyfile

# Test internal CA
curl -k https://localhost/healthz
```

### Can't query events

```bash
# Verify admin IP whitelist
curl -v https://localhost/events \
  -H "X-Admin-Api-Key: your-key"

# Update ADMIN_IP in .env if blocked
```

---

## Updating

### Update Collector

```bash
cd collector

# Pull latest code
git pull

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Verify
docker-compose logs -f collector
```

### Update Agent

```bash
cd agent

# Pull latest code
git pull

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Verify
docker-compose logs -f agent
```

---

## Production Recommendations

1. **Use external database** - Consider PostgreSQL for high-volume deployments
2. **Enable rate limiting** - Uncomment rate limit block in Caddyfile
3. **Set resource limits** - Adjust CPU/memory limits based on load
4. **Monitor health checks** - Integrate with your monitoring stack
5. **Backup regularly** - Automate database backups
6. **Use secrets management** - Store tokens in Docker secrets or vault
7. **Enable logging** - Forward logs to centralized logging system

---

## Multi-Host Deployment

### Collector Host

```bash
# Deploy collector only
cd collector
docker-compose up -d
```

### Agent Hosts

```bash
# Deploy agent on each monitored host
cd agent
docker-compose up -d
```

### Networking

Ensure agents can reach collector:
- Open firewall for port 443
- Configure DNS or /etc/hosts
- Use proper TLS certificates or internal CA

---

## Performance Tuning

### Collector

```yaml
deploy:
  resources:
    limits:
      cpus: '2'        # Increase for high load
      memory: 1G       # Increase for many events
```

### Caddy

Enable caching for static responses (if applicable):

```caddy
cache {
  ttl 5m
}
```

### Database

For high-volume deployments:
- Switch to PostgreSQL
- Enable WAL mode (enabled by default)
- Regular VACUUM operations

---

## Development Mode

Run with hot-reload for development:

```bash
# Collector with code changes
docker-compose up collector

# Agent with code changes
docker-compose up agent
```

Code changes are automatically reflected (volumes are mounted with source code).

---

## Complete Teardown

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker rmi watchtower-collector watchtower-agent
```
