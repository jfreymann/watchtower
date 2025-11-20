#!/usr/bin/env bash
set -euo pipefail

APP_USER="watchtower-agent"
APP_GROUP="${APP_USER}"
INSTALL_ROOT="/opt/watchtower"
DEST_DIR="${INSTALL_ROOT}/agent"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC_DIR="${REPO_ROOT}/watchtower/agent"

if [[ "${EUID}" -ne 0 ]]; then
  echo "This script must be run as root (sudo)." >&2
  exit 1
fi

echo "=== Watchtower Agent Install ==="
echo "Repo source: ${SRC_DIR}"
echo "Install dest: ${DEST_DIR}"
echo

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "ERROR: Source directory ${SRC_DIR} not found."
  echo "Expected layout: <repo_root>/watchtower/agent"
  exit 1
fi

# 1) Create system user if needed
if id -u "${APP_USER}" >/dev/null 2>&1; then
  echo "[*] User ${APP_USER} already exists, skipping."
else
  echo "[+] Creating system user ${APP_USER}..."
  useradd --system --no-create-home --shell /usr/sbin/nologin "${APP_USER}"
  # Add to adm group so it can read journald logs
  usermod -aG adm "${APP_USER}" || true
fi

# 2) Create base install dir
echo "[+] Ensuring install root exists: ${INSTALL_ROOT}"
mkdir -p "${INSTALL_ROOT}"

# 3) Sync code into /opt/watchtower/agent
echo "[+] Syncing agent code into ${DEST_DIR} (excluding .venv, .env)..."
mkdir -p "${DEST_DIR}"
rsync -a \
  --delete \
  --exclude ".venv" \
  --exclude ".env" \
  "${SRC_DIR}/" "${DEST_DIR}/"

# 4) Create / fix permissions
echo "[+] Adjusting ownership and permissions..."
chown -R "${APP_USER}:${APP_GROUP}" "${DEST_DIR}"
chmod 750 "${DEST_DIR}"

# 5) Create virtualenv + install deps
if [[ ! -d "${DEST_DIR}/.venv" ]]; then
  echo "[+] Creating virtualenv..."
  sudo -u "${APP_USER}" python3 -m venv "${DEST_DIR}/.venv"
fi

if [[ -f "${DEST_DIR}/requirements.txt" ]]; then
  echo "[+] Installing Python dependencies..."
  sudo -u "${APP_USER}" "${DEST_DIR}/.venv/bin/pip" install --upgrade pip
  sudo -u "${APP_USER}" "${DEST_DIR}/.venv/bin/pip" install -r "${DEST_DIR}/requirements.txt"
else
  echo "[!] No requirements.txt found in ${DEST_DIR} – skipping pip install."
fi

# 6) Ensure .env exists (do not overwrite if present)
ENV_FILE="${DEST_DIR}/.env"
if [[ -f "${ENV_FILE}" ]]; then
  echo "[*] Existing .env found at ${ENV_FILE}, leaving it unchanged."
else
  echo "[+] Creating .env template at ${ENV_FILE}..."
  cat > "${ENV_FILE}" <<EOF
# Watchtower Agent configuration

# HTTPS URL of the Watchtower Collector /login endpoint
WATCHTOWER_COLLECTOR_URL=https://watchtower.local/login

# Token that must match WATCHTOWER_AGENT_TOKEN on the collector
WATCHTOWER_AGENT_TOKEN=CHANGE_ME_AGENT_TOKEN

# Verify TLS (set to false if using Caddy internal CA and haven't added it to trust store)
WATCHTOWER_VERIFY_TLS=true

# systemd unit name for ssh (usually ssh.service or sshd.service)
WATCHTOWER_SSH_UNIT=ssh.service

# Optional metadata
WATCHTOWER_REGION=us-east
WATCHTOWER_HOST_GROUP=default
WATCHTOWER_SEVERITY=info
WATCHTOWER_FLAGGED=false
EOF

  chown "${APP_USER}:${APP_GROUP}" "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"

  echo ">>> IMPORTANT: Edit ${ENV_FILE} and set a correct WATCHTOWER_COLLECTOR_URL and WATCHTOWER_AGENT_TOKEN."
fi

# 7) Create systemd service unit
SERVICE_FILE="/etc/systemd/system/watchtower-agent.service"
echo "[+] Writing systemd unit to ${SERVICE_FILE}..."

cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Watchtower Agent - SSH login monitoring
After=network-online.target systemd-journald.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${DEST_DIR}
EnvironmentFile=${DEST_DIR}/.env
ExecStart=${DEST_DIR}/.venv/bin/python ${DEST_DIR}/watchtower_agent.py

User=${APP_USER}
Group=${APP_GROUP}

Restart=always
RestartSec=5

# Hardening
NoNewPrivileges=yes
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
LockPersonality=yes
MemoryDenyWriteExecute=true
RestrictRealtime=true
RestrictSUIDSGID=true

[Install]
WantedBy=multi-user.target
EOF

echo "[+] Reloading systemd daemon..."
systemctl daemon-reload

echo "[+] Enabling and starting watchtower-agent.service..."
systemctl enable --now watchtower-agent.service

echo
echo "=== Agent install complete ==="
echo "Status:"
systemctl --no-pager status watchtower-agent.service || true
echo
echo "Next steps:"
echo "  1) Edit ${ENV_FILE} and set a correct WATCHTOWER_COLLECTOR_URL and WATCHTOWER_AGENT_TOKEN"
echo "  2) Ensure the collector is reachable via HTTPS from this host"
