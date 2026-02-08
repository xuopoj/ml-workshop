#!/bin/bash
# Setup SSH + code-server for VSCode Remote access
# Called from start-notebook.sh when VSCODE_SSH_PORT is set

WORK_DIR="${1:?Usage: start-vscode.sh <work-dir>}"
PERSISTENT_DIR="${WORK_DIR}/.vscode-server"
mkdir -p "${PERSISTENT_DIR}"

# Persist VS Code Remote SSH server across container restarts
# (Microsoft's VS Code Server downloads ~70MB on first SSH connection)
VSCODE_REMOTE_DIR="${PERSISTENT_DIR}/vscode-remote"
mkdir -p "${VSCODE_REMOTE_DIR}"
rm -rf /root/.vscode-server
ln -sf "${VSCODE_REMOTE_DIR}" /root/.vscode-server

# =============================================================================
# SSH Setup
# =============================================================================

SSH_HOST="${VSCODE_SSH_HOST:-<workshop-host>}"
SSH_PASSWORD="${VSCODE_PASSWORD:-}"

# --- Password: env var > persisted > auto-generate ---
SHADOW_FILE="${PERSISTENT_DIR}/shadow"
PASSWORD_FILE="${PERSISTENT_DIR}/password"
if [ -n "$SSH_PASSWORD" ]; then
    echo "root:${SSH_PASSWORD}" | chpasswd
    grep "^root:" /etc/shadow > "$SHADOW_FILE"
    echo "$SSH_PASSWORD" > "$PASSWORD_FILE"
    chmod 600 "$PASSWORD_FILE"
    echo "SSH password set from environment variable"
elif [ -f "$SHADOW_FILE" ]; then
    SHADOW_LINE=$(cat "$SHADOW_FILE")
    sed -i "s|^root:.*|${SHADOW_LINE}|" /etc/shadow
    SSH_PASSWORD=$(cat "$PASSWORD_FILE" 2>/dev/null || echo "")
    echo "SSH password restored from persistent storage"
else
    SSH_PASSWORD=$(openssl rand -base64 12)
    echo "root:${SSH_PASSWORD}" | chpasswd
    grep "^root:" /etc/shadow > "$SHADOW_FILE"
    echo "$SSH_PASSWORD" > "$PASSWORD_FILE"
    chmod 600 "$SHADOW_FILE" "$PASSWORD_FILE"
    echo ""
    echo "============================================"
    echo "SSH 密码已自动生成 (首次启动)"
    echo "用户名: root"
    echo "密码: ${SSH_PASSWORD}"
    echo ""
    echo "修改密码请运行: passwd"
    echo "============================================"
    echo ""
fi

# --- Persist SSH host keys ---
SSH_KEYS_DIR="${PERSISTENT_DIR}/ssh-host-keys"
mkdir -p "$SSH_KEYS_DIR"
if [ ! -f "$SSH_KEYS_DIR/ssh_host_rsa_key" ]; then
    ssh-keygen -t rsa -f "$SSH_KEYS_DIR/ssh_host_rsa_key" -N ""
    ssh-keygen -t ed25519 -f "$SSH_KEYS_DIR/ssh_host_ed25519_key" -N ""
fi
cp "$SSH_KEYS_DIR"/ssh_host_* /etc/ssh/
chmod 600 /etc/ssh/ssh_host_*_key

# --- Configure and start SSH ---
cat > /etc/ssh/sshd_config.d/vscode.conf <<EOF
PasswordAuthentication yes
PermitRootLogin yes
X11Forwarding no
EOF

/usr/sbin/sshd
echo "SSH server started on port 22 (host port: ${VSCODE_SSH_PORT})"

# --- Generate setup guide from template ---
PASSWORD_DISPLAY="${SSH_PASSWORD:-<run passwd to set>}"
HUB_USER="${JUPYTERHUB_USER:-root}"
sed -e "s|VSCODE_SSH_HOST_PLACEHOLDER|${SSH_HOST}|g" \
    -e "s|VSCODE_SSH_PORT_PLACEHOLDER|${VSCODE_SSH_PORT}|g" \
    -e "s|JUPYTERHUB_USER_PLACEHOLDER|${HUB_USER}|g" \
    -e "s|VSCODE_USER_PLACEHOLDER|root|g" \
    -e "s|VSCODE_PASSWORD_PLACEHOLDER|${PASSWORD_DISPLAY}|g" \
    /usr/local/share/getstarted.md > "${WORK_DIR}/getstarted.md"

# --- Recommended extensions for VS Code Remote SSH ---
mkdir -p "${WORK_DIR}/.vscode"
if [ ! -f "${WORK_DIR}/.vscode/extensions.json" ]; then
    cat > "${WORK_DIR}/.vscode/extensions.json" <<EOF
{
    "recommendations": [
        "ms-python.python",
        "ms-toolsai.jupyter",
        "charliermarsh.ruff"
    ]
}
EOF
fi

# =============================================================================
# code-server Setup
# =============================================================================

HOME_DIR="/root"
CONFIG_DIR="${HOME_DIR}/.config/code-server"
DATA_DIR="${HOME_DIR}/.local/share/code-server"
mkdir -p "${PERSISTENT_DIR}/config" "${PERSISTENT_DIR}/data"

# Seed pre-installed extensions on first run
if [ ! -d "${PERSISTENT_DIR}/extensions" ]; then
    cp -r /root/.local/share/code-server/extensions "${PERSISTENT_DIR}/extensions"
fi

mkdir -p "${HOME_DIR}/.config" "${HOME_DIR}/.local/share"
rm -rf "${CONFIG_DIR}" "${DATA_DIR}"
ln -sf "${PERSISTENT_DIR}/config" "${CONFIG_DIR}"
ln -sf "${PERSISTENT_DIR}/data" "${DATA_DIR}"

# Set VSCode proxy settings on first run
VSCODE_SETTINGS_DIR="${PERSISTENT_DIR}/data/User"
if [ ! -f "${VSCODE_SETTINGS_DIR}/settings.json" ]; then
    mkdir -p "${VSCODE_SETTINGS_DIR}"
    cat > "${VSCODE_SETTINGS_DIR}/settings.json" <<EOF
{
    "http.proxy": "http://ml-workshop-proxy:8899",
    "http.proxyStrictSSL": false
}
EOF
fi

if [ ! -f "${PERSISTENT_DIR}/config/config.yaml" ]; then
    cat > "${PERSISTENT_DIR}/config/config.yaml" <<EOF
bind-addr: 127.0.0.1:8080
auth: none
cert: false
disable-telemetry: true
disable-update-check: true
user-data-dir: ${PERSISTENT_DIR}/data
extensions-dir: ${PERSISTENT_DIR}/extensions
EOF
fi

echo "Starting code-server on port 8080..."
code-server --config "${PERSISTENT_DIR}/config/config.yaml" "${WORK_DIR}" &
