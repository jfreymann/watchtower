# Installing the Watchtower Collector

This guide installs the Watchtower Collector on Ubuntu.

---

## 1. Install Dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip caddy
```

## 2. Create System User

```bash
sudo useradd --system --shell /usr/sbin/nologin watchtower/collector
```

## 3. Deploy to /opt

```bash
sudo mkdir -p /opt/watchtower/collector
sudo cp -r ./watchtower/collector/* /opt/watchtower/collector/
```

## 4. Create Python Environment

```bash
cd /opt/watchtower/collector
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
```

## 5. Create .env File

```bash
WATCHTOWER_DB_PATH=/opt/watchtower/collector/watchtower.db
WATCHTOWER_AGENT_TOKEN=<TOKEN>
ADMIN_API_KEY=<ADMIN_KEY>
```

Secure it:

```bash
sudo chown watchtower/collector:watchtower/collector /opt/watchtower/collector/.env
sudo chmod 600 /opt/watchtower/collector/.env
```

## 6. Install systemd Service

Place:

```bash
watchtower/collector.service
```

Then run:'

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now watchtower/collector
```

## 7. Install Caddy Reverse Proxy

See:
../operations/caddy-config.md


---
