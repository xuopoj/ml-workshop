#!/bin/bash
# Start script for user containers with Docker-in-Docker
# Optionally includes SSH + code-server when VSCODE_SSH_PORT is set

set -e

# =============================================================================
# Detect user (ma-user on NPU image, jovyan on Mac testing)
# =============================================================================
if id ma-user &>/dev/null; then
    NB_USER="ma-user"
elif id jovyan &>/dev/null; then
    NB_USER="jovyan"
else
    NB_USER="$(whoami)"
fi
HOME_DIR=$(eval echo "~${NB_USER}")
NB_GROUP=$(id -gn "${NB_USER}")
WORK_DIR="${HOME_DIR}/work"

# =============================================================================
# SSH + code-server Setup (only when VSCODE_SSH_PORT is set)
# =============================================================================
if [ -n "${VSCODE_SSH_PORT}" ]; then
    SSH_HOST="${VSCODE_SSH_HOST:-<workshop-host>}"
    SSH_PASSWORD="${VSCODE_PASSWORD:-}"
    PERSISTENT_DIR="${WORK_DIR}/.vscode-server"
    mkdir -p "${PERSISTENT_DIR}"

    # --- Password: env var > persisted shadow > auto-generate ---
    SHADOW_FILE="${PERSISTENT_DIR}/shadow"
    if [ -n "$SSH_PASSWORD" ]; then
        echo "${NB_USER}:${SSH_PASSWORD}" | chpasswd
        grep "^${NB_USER}:" /etc/shadow > "$SHADOW_FILE"
        echo "SSH password set from environment variable"
    elif [ -f "$SHADOW_FILE" ]; then
        SHADOW_LINE=$(cat "$SHADOW_FILE")
        sed -i "s|^${NB_USER}:.*|${SHADOW_LINE}|" /etc/shadow
        echo "SSH password restored from persistent storage"
    else
        SSH_PASSWORD=$(openssl rand -base64 12)
        echo "${NB_USER}:${SSH_PASSWORD}" | chpasswd
        grep "^${NB_USER}:" /etc/shadow > "$SHADOW_FILE"
        chmod 600 "$SHADOW_FILE"
        echo ""
        echo "============================================"
        echo "SSH 密码已自动生成 (首次启动)"
        echo "用户名: ${NB_USER}"
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
PermitRootLogin no
X11Forwarding no
AllowUsers ${NB_USER}
EOF

    /usr/sbin/sshd
    echo "SSH server started on port 22 (host port: ${VSCODE_SSH_PORT})"

    # --- Generate setup guide from template ---
    PASSWORD_DISPLAY="${SSH_PASSWORD:-<run passwd to set>}"
    HUB_USER="${JUPYTERHUB_USER:-${NB_USER}}"
    sed -e "s|VSCODE_SSH_HOST_PLACEHOLDER|${SSH_HOST}|g" \
        -e "s|VSCODE_SSH_PORT_PLACEHOLDER|${VSCODE_SSH_PORT}|g" \
        -e "s|JUPYTERHUB_USER_PLACEHOLDER|${HUB_USER}|g" \
        -e "s|VSCODE_USER_PLACEHOLDER|${NB_USER}|g" \
        -e "s|VSCODE_PASSWORD_PLACEHOLDER|${PASSWORD_DISPLAY}|g" \
        /usr/local/share/getstarted.md > /opt/workshop/getstarted.md
    chown "${NB_USER}:${NB_GROUP}" /opt/workshop/getstarted.md 2>/dev/null || true

    # --- Start code-server in background ---
    CONFIG_DIR="${HOME_DIR}/.config/code-server"
    DATA_DIR="${HOME_DIR}/.local/share/code-server"
    mkdir -p "${PERSISTENT_DIR}/config" "${PERSISTENT_DIR}/data" "${PERSISTENT_DIR}/extensions"
    mkdir -p "${HOME_DIR}/.config" "${HOME_DIR}/.local/share"
    rm -rf "${CONFIG_DIR}" "${DATA_DIR}"
    ln -sf "${PERSISTENT_DIR}/config" "${CONFIG_DIR}"
    ln -sf "${PERSISTENT_DIR}/data" "${DATA_DIR}"
    chown -R "${NB_USER}:${NB_GROUP}" "${PERSISTENT_DIR}"
    chown -R "${NB_USER}:${NB_GROUP}" "${HOME_DIR}/.config" "${HOME_DIR}/.local"

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
        chown "${NB_USER}:${NB_GROUP}" "${PERSISTENT_DIR}/config/config.yaml"
    fi

    echo "Starting code-server on port 8080..."
    sudo -E -u "${NB_USER}" HOME="${HOME_DIR}" code-server --config "${PERSISTENT_DIR}/config/config.yaml" "${WORK_DIR}" &
fi

# =============================================================================
# Docker-in-Docker
# =============================================================================

echo "Starting Docker daemon..."
dockerd --host=unix:///var/run/docker.sock \
        --storage-driver=vfs \
        --iptables=false \
        --bridge=none \
        > /var/log/dockerd.log 2>&1 &

echo "Waiting for Docker daemon..."
timeout=30
while ! docker info > /dev/null 2>&1; do
    timeout=$((timeout - 1))
    if [ $timeout -le 0 ]; then
        echo "Docker daemon failed to start. Logs:"
        cat /var/log/dockerd.log
        echo "Continuing without Docker..."
        break
    fi
    sleep 1
done

if docker info > /dev/null 2>&1; then
    echo "Docker daemon ready!"
    docker --version
fi

# Create symlink to workshop materials if not exists
if [ ! -L "${HOME_DIR}/workshop" ] && [ -d /opt/workshop ]; then
    ln -sf /opt/workshop "${HOME_DIR}/workshop"
fi

# =============================================================================
# Start JupyterLab
# =============================================================================

exec jupyterhub-singleuser \
    --ip=0.0.0.0 \
    --port=8888 \
    --notebook-dir="${HOME_DIR}" \
    --ServerApp.default_url=/lab \
    --ServerApp.allow_root=True
