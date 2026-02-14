#!/bin/bash
set -e

source /opt/conda/etc/profile.d/conda.sh
conda activate env0

# =============================================================================
# SSH Setup (for VS Code Remote-SSH)
# =============================================================================

PERSISTENT_DIR="/root/share/.ssh-persist"
mkdir -p "$PERSISTENT_DIR"

# --- Password: env var > persisted > auto-generate ---
SHADOW_FILE="${PERSISTENT_DIR}/shadow"
PASSWORD_FILE="${PERSISTENT_DIR}/password"
SSH_PASSWORD="${SSH_PASSWORD:-}"

if [ -n "$SSH_PASSWORD" ]; then
    echo "root:${SSH_PASSWORD}" | chpasswd
    grep "^root:" /etc/shadow > "$SHADOW_FILE"
    echo "$SSH_PASSWORD" > "$PASSWORD_FILE"
    chmod 600 "$PASSWORD_FILE"
elif [ -f "$SHADOW_FILE" ]; then
    SHADOW_LINE=$(cat "$SHADOW_FILE")
    sed -i "s|^root:.*|${SHADOW_LINE}|" /etc/shadow
    SSH_PASSWORD=$(cat "$PASSWORD_FILE" 2>/dev/null || echo "")
else
    SSH_PASSWORD=$(openssl rand -base64 12)
    echo "root:${SSH_PASSWORD}" | chpasswd
    grep "^root:" /etc/shadow > "$SHADOW_FILE"
    echo "$SSH_PASSWORD" > "$PASSWORD_FILE"
    chmod 600 "$SHADOW_FILE" "$PASSWORD_FILE"
    echo ""
    echo "============================================"
    echo "SSH password auto-generated (first start)"
    echo "User: root"
    echo "Password: ${SSH_PASSWORD}"
    echo ""
    echo "Change password: passwd"
    echo "============================================"
    echo ""
fi

# --- Persist SSH host keys ---
SSH_KEYS_DIR="${PERSISTENT_DIR}/host-keys"
mkdir -p "$SSH_KEYS_DIR"
if [ ! -f "$SSH_KEYS_DIR/ssh_host_rsa_key" ]; then
    ssh-keygen -t rsa -f "$SSH_KEYS_DIR/ssh_host_rsa_key" -N ""
    ssh-keygen -t ed25519 -f "$SSH_KEYS_DIR/ssh_host_ed25519_key" -N ""
fi
cp "$SSH_KEYS_DIR"/ssh_host_* /etc/ssh/
chmod 600 /etc/ssh/ssh_host_*_key

# --- Export Ascend env vars to /etc/environment for VS Code Remote SSH ---
if [ -f /etc/profile.d/ascend.sh ]; then
    (
        source /etc/profile.d/ascend.sh
        for var in ASCEND_TOOLKIT_HOME ASCEND_AICPU_PATH ASCEND_OPP_PATH \
                   TOOLCHAIN_HOME ASCEND_HOME_PATH ASCEND_DRIVER_HOME \
                   LD_LIBRARY_PATH PYTHONPATH PATH; do
            val="${!var}"
            if [ -n "$val" ]; then
                sed -i "/^${var}=/d" /etc/environment
                echo "${var}=${val}" >> /etc/environment
            fi
        done
    )
fi

# --- Configure and start SSH ---
cat > /etc/ssh/sshd_config.d/vscode.conf <<EOF
PasswordAuthentication yes
PermitRootLogin yes
X11Forwarding no
EOF

/usr/sbin/sshd
echo "SSH server started on port 22"

# --- Persist VS Code Remote server across restarts ---
VSCODE_REMOTE_DIR="${PERSISTENT_DIR}/vscode-remote"
mkdir -p "$VSCODE_REMOTE_DIR"
rm -rf /root/.vscode-server
ln -sf "$VSCODE_REMOTE_DIR" /root/.vscode-server

# --- Generate setup guide from template ---
SSH_HOST="${SSH_HOST:-<workshop-host>}"
SSH_PORT="${SSH_PORT:-22}"
PASSWORD_DISPLAY="${SSH_PASSWORD:-<run passwd to set>}"
sed -e "s|SSH_HOST_PLACEHOLDER|${SSH_HOST}|g" \
    -e "s|SSH_PORT_PLACEHOLDER|${SSH_PORT}|g" \
    -e "s|SSH_PASSWORD_PLACEHOLDER|${PASSWORD_DISPLAY}|g" \
    /usr/local/share/getstarted.md > /root/share/getstarted.md

# =============================================================================
# Run command or interactive shell
# =============================================================================

if [ $# -eq 0 ] || [ "$1" = "zsh" ]; then
    exec zsh -l
elif [ "$1" = "bash" ]; then
    exec bash --login
else
    exec "$@"
fi
