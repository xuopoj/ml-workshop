#!/bin/bash
# Start script for OpenClaw showcase containers
# Architecture:
#   port 8888  -> jupyterhub-singleuser (JupyterLab for terminal access)
#   port 18789 -> OpenClaw Gateway (exposed directly on host port)

set -e

PERSISTENT_DIR="/home/jovyan/work/.openclaw"
OPENCLAW_DIR="/home/jovyan/.openclaw"

# Check for existing config in persistent volume
if [ -f "${PERSISTENT_DIR}/openclaw.json" ] && [ -f "${PERSISTENT_DIR}/token" ]; then
    echo "Found existing OpenClaw config in ${PERSISTENT_DIR}, reusing..."
    GATEWAY_TOKEN=$(cat "${PERSISTENT_DIR}/token")
else
    echo "No existing config found, generating fresh config..."
    mkdir -p "${PERSISTENT_DIR}"

    # Generate a random token for gateway auth
    GATEWAY_TOKEN=$(openssl rand -hex 16)

    # Write config from template
    sed "s|OPENCLAW_TOKEN_PLACEHOLDER|${GATEWAY_TOKEN}|g" \
        /usr/local/share/openclaw.json > "${PERSISTENT_DIR}/openclaw.json"

    # Save token
    echo "${GATEWAY_TOKEN}" > "${PERSISTENT_DIR}/token"
    chmod 600 "${PERSISTENT_DIR}/token"
fi

chown -R jovyan:jovyan "${PERSISTENT_DIR}"

# Symlink ~/.openclaw -> persistent volume
mkdir -p "$(dirname "${OPENCLAW_DIR}")"
rm -rf "${OPENCLAW_DIR}"
ln -s "${PERSISTENT_DIR}" "${OPENCLAW_DIR}"

# Generate getting-started page with actual connection info
HOST_PORT="${OPENCLAW_HOST_PORT:-18789}"
GATEWAY_HOST="${OPENCLAW_GATEWAY_HOST:-localhost}"
sed -e "s|GATEWAY_HOST:OPENCLAW_PORT|${GATEWAY_HOST}:${HOST_PORT}|g" \
    -e "s|OPENCLAW_TOKEN|${GATEWAY_TOKEN}|g" \
    /usr/local/share/openclaw-getting-started.md > /home/jovyan/getting-started.md
chown jovyan:jovyan /home/jovyan/getting-started.md

# Start OpenClaw Gateway in background on 18789
echo "Starting OpenClaw Gateway on port 18789 (host port: ${HOST_PORT})..."
su - jovyan -c "openclaw gateway > /tmp/openclaw.log 2>&1 &"

# Wait for gateway
timeout=30
while ! curl -s http://127.0.0.1:18789/ > /dev/null 2>&1; do
    timeout=$((timeout - 1))
    if [ $timeout -le 0 ]; then
        echo "OpenClaw Gateway failed to start. Logs:"
        cat /tmp/openclaw.log
        echo "Continuing without OpenClaw..."
        break
    fi
    sleep 1
done
echo "OpenClaw Gateway ready!"

# Start JupyterLab as jovyan (for terminal access via JupyterHub)
export HOME=/home/jovyan
exec sudo -E -u jovyan jupyterhub-singleuser
