
# Installing the Watchtower Agent

This document describes installing the Watchtower Agent on any Linux host.


## 1. Install Python + journald tools

```bash
sudo apt install -y python3 python3-venv python3-pip systemd-journal-remote
```

## 2. Deploy Agent

```bash
sudo mkdir -p /opt/watchtower/agent
sudo cp -r ./watchtower/agent/* /opt/watchtower/agent/
```

## 3. Install Python Dependencies

```bash
cd /opt/watchtower/agent
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
```

## 4. Create .env

```bash
WATCHTOWER_COLLECTOR_URL=https://watchtower.local/login
WATCHTOWER_AGENT_TOKEN=<TOKEN>
WATCHTOWER_TLS_VERIFY=true
WATCHTOWER_SSH_UNIT=ssh.service
```

Secure:

```bash
sudo chmod 600 /opt/watchtower/agent/.env
sudo chown watchtower/agent:watchtower/agent /opt/watchtower/agent/.env
```

## 5. Install systemd Service

```bash
sudo cp systemd/watchtower/agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now watchtower/agent
```

## 6. Test

```bash
sudo journalctl -u watchtower/agent -f
```