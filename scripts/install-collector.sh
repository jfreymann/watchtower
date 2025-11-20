#!/usr/bin/env bash
set -euo pipefail

APP_USER="watchtower-collector"
APP_GROUP="${APP_USER}"
INSTALL_ROOT="/opt/watchtower"
DEST_DIR="${INSTALL_ROOT}/collector"

# Resolve repo root (this script is in repo_root/scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SRC_DIR="${REPO_ROOT}/watchtower/collector"

if [[ "${EUID}" -ne 0 ]]; then
  echo "This script must be run as root (sudo)." >&2
  exit 1
fi

echo "=== Watchtower Collector Install ==="
echo "Repo source: ${SRC_DIR}"
echo "Install dest: ${DEST_DIR}"
echo

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "ERROR: Source directory ${SRC_DIR} not found."
  echo "Expected layout: <repo_root>/watchtower/collector"
  exit 1
fi

# 1) Create system user if needed
if id -u "${APP_USER}" >/dev/null 2>&1; then
  echo "[*] User ${APP_USER} already exists, skipping."
else
  echo "[+] Creating system user ${APP_USER}..."
  useradd --system --no-create-home --shell /usr/sbin/nologin "${APP_USER}"
fi

# 2) Create base install dir
echo "[+] Ensuring install root exists: ${INSTALL_ROOT}"
mkdir -p "${INSTALL_ROOT}"

# 3) Sync code into /opt/watchtower/collector
echo "[+] Syncing collector code into ${DEST_DIR} (excluding .venv, .env, DB)..."
mkdir -p "${DEST_DIR}"
rsync -a \
  --delete \
  --exclude ".venv" \
  --exclude ".env" \
  --exclude "watchtower.db" \
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
# Watchtower Collector configuration

# Path to SQLite database
WATCHTOWER_DB_PATH=${DEST_DIR}/watchtower.db

# Token used by Watchtower Agents (set this to a strong random value)
WATCHTOWER_AGENT_TOKEN=CHANGE_ME_AGENT_TOKEN

# Admin API key used for /events and other privileged endpoints
ADMIN_API_KEY=CHANGE_ME_ADMIN_API_KEY

# Optional webhook for critical events (leave empty if unused)
WATCHTOWER_WEBHOOK_URL=
EOF

  chown "${APP_USER}:${APP_GROUP}" "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"

  echo ">>> IMPORTANT: Edit ${ENV_FILE} and set WATCHTOWER_AGENT_TOKEN and ADMIN_API_KEY."
fi

# 7) Create systemd service unit
SERVICE_FILE="/etc/systemd/system/watchtower-collector.service"
echo "[+] Writing systemd unit to ${SERVICE_FILE}..."

cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Watchtower Collector API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=${DEST_DIR}
EnvironmentFile=${DEST_DIR}/.env
ExecStart=${DEST_DIR}/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --proxy-headers

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

echo "[+] Enabling and starting watchtower-collector.service..."
systemctl enable --now watchtower-collector.service

echo
echo "=== Collector install complete ==="
echo "Status:"
systemctl --no-pager status watchtower-collector.service || true
echo
echo "Next steps:"
echo "  1) Edit ${ENV_FILE} and set strong values for WATCHTOWER_AGENT_TOKEN and ADMIN_API_KEY"
echo "  2) Configure Caddy to reverse proxy https://watchtower.local to 127.0.0.1:8000"
echo "     (see docs/operations/caddy-config.md)"
