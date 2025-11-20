# Docker Quick Start

Quick reference for deploying Watchtower with Docker.

---

## 🚀 Fastest Start

### Collector Only (Recommended)

```bash
cd collector
cp .env.docker.example .env
# Edit .env with your tokens
docker-compose up -d
```

### Agent Only

```bash
cd agent
cp .env.docker.example .env
# Edit .env with collector URL and token
docker-compose up -d
```

### Complete Stack

```bash
# From repository root
docker-compose --profile with-agent up -d
```

---

## 📋 Configuration

### Required Environment Variables

**Collector:**
```bash
ADMIN_API_KEY=your-secure-admin-key
LOGIN_ALERT_TOKEN=your-secure-agent-token
```

**Agent:**
```bash
WATCHTOWER_COLLECTOR_URL=https://watchtower.local/login
WATCHTOWER_TOKEN=your-agent-token
```

---

## 🔧 Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose build --no-cache
docker-compose up -d

# Backup database
docker-compose exec collector sqlite3 /var/lib/watchtower/watchtower.db ".backup /tmp/backup.db"
docker cp watchtower-collector:/tmp/backup.db ./backup.db
```

---

## 🔍 Testing

```bash
# Health check
curl -k https://localhost/healthz

# Query events (requires admin key)
curl -k https://localhost/events?hours=1 \
  -H "X-Admin-Api-Key: your-admin-key"
```

---

## 📚 Full Documentation

See [docs/docker-deployment.md](docs/docker-deployment.md) for complete deployment guide.

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Caddy (443)    │  ← HTTPS + TLS
└────────┬────────┘
         │
┌────────▼────────┐
│  Collector      │  ← FastAPI
│  (port 8000)    │
└────────┬────────┘
         │
┌────────▼────────┐
│  SQLite DB      │  ← Volume: watchtower-data
└─────────────────┘
```

Agents connect to Caddy via HTTPS on port 443.

---

## 🔒 Security Notes

- Collector runs as non-root user
- Read-only filesystem
- No new privileges
- Resource limits enforced
- Minimal attack surface
- TLS everywhere

---

## 🐛 Troubleshooting

**Agent can't access journald:**
```bash
# Verify journal mounts exist
ls -la /var/log/journal
```

**Collector won't start:**
```bash
# Check environment variables
docker-compose config

# View detailed logs
docker-compose logs collector
```

**Can't reach collector:**
```bash
# Test health endpoint
curl -v http://localhost:8000/healthz

# Check Caddy status
docker-compose logs caddy
```

---

## 🎯 Production Checklist

- [ ] Generate secure random tokens
- [ ] Configure proper domain/hostname
- [ ] Set admin IP whitelist
- [ ] Enable HTTPS with proper certificates
- [ ] Configure resource limits
- [ ] Set up database backups
- [ ] Configure log forwarding
- [ ] Enable monitoring/health checks
- [ ] Review Caddyfile security headers
- [ ] Test failover/restart behavior
