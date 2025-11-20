# Secure Deployment Guide for Watchtower

This guide describes the recommended production-hardening steps for deploying Watchtower in a secure infrastructure environment.

It applies to:

- Homelabs
- Enterprise Linux environments
- Bastion hosts
- Distributed fleets

---

###  1. Prepare the Collector Host

#### 1.1 OS Hardening

Recommended:

```bash
sudo apt update
sudo apt install unattended-upgrades fail2ban ufw
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

Disable Password SSH:

```bash
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

---

### 2. Deploy Collector Securely

Follow installation steps from:

- install-collector.md

Then apply hardening:

#### 2.1 Confirm filesystem permissions

```bash
sudo chown -R watchtower/collector:watchtower/collector /opt/watchtower/collector
sudo chmod 700 /opt/watchtower/collector
sudo chmod 600 /opt/watchtower/collector/.env
sudo chmod 600 /opt/watchtower/collector/watchtower.db
```

#### 2.2 Confirm systemd restrictions

check

```bash
systemctl cat watchtower/collector.service
```

Ensure these exist:

- NoNewPrivileges=yes
- PrivateTmp=true
- ProtectSystem=strict
- MemoryDenyWriteExecute=true
- ProtectHome=true
- Non-root user

If missing:

→ You are not running the hardened version.

---

### 3. Deploy Caddy Securely

#### 3.1 Install Caddy

```bash
sudo apt install -y caddy
```

#### 3.2 Deploy hardened Caddyfile

```bash
watchtower.local {
    tls internal
    encode zstd gzip

    @admin_protected {
        path /events*
        path /admin/*
        not remote_ip 192.168.1.0/24
    }
    respond @admin_protected "Forbidden" 403

    reverse_proxy 127.0.0.1:8000
}
```

Reload:

```bash
sudo caddy reload
```

---

### 4. Deploy Agents Securely

See:
- install-agent.md

Ensure:

```bash
chmod 600 /opt/watchtower/agent/.env
chmod 700 /opt/watchtower/agent
```

And the service user has no shell:

```bash
sudo usermod --shell /usr/sbin/nologin watchtower/agent
```

---

### 5. Rotate and Manage Keys

#### 5.1 Generate new production tokens

```bash
openssl rand -base64 32
```

Set:

- WATCHTOWER_AGENT_TOKEN
- ADMIN_API_KEY

Then:

```bash
sudo systemctl restart watchtower/collector
sudo systemctl restart watchtower/agent
```

---

### 6. Post-Deployment Validation

#### 6.1 Check Caddy TLS

```bash
curl -k https://watchtower.local/healthz
```

Should return:

```json
{"status":"ok"}
```

#### 6.2 Check event ingestion

SSH into an agent host:

```bash
ssh user@host
```

Then view collector API:

```bash
curl -k "https://watchtower.local/events?hours=1&limit=10" \
  -H "X-Admin-Api-Key: <ADMIN_KEY>"
```

---

### 7. Ongoing Security Practices

#### ✔ Rotate agent tokens quarterly

#### ✔ Rotate admin API keys semi-annually

#### ✔ Backup SQLite weekly

#### ✔ Monitor systemd for failures

#### ✔ Validate Caddy certificates before expiry

#### ✔ Use your own CA for large deployments

---

### 8. Recommended Enhancements (Optional)

- Deploy behind WireGuard
- Move from SQLite → Postgres
- Add journald forwarding for additional event types
- Deploy Grafana dashboards
- Centralized Syslog integration

---

### 9. Summary

A secure Watchtower deployment includes:

- Hardened OS
- Secure collector with strict permissions
- Caddy TLS reverse proxy
- Agent → collector communication only over HTTPS
- Strong token-based authentication
- systemd sandboxing
- Regular backups & log monitoring
Watchtower is built to be secure by default — this guide ensures it stays that way in production.

