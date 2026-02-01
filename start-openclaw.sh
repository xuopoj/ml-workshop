#!/bin/bash
# Start script for OpenClaw showcase containers
# Architecture:
#   port 8888 (JupyterHub) -> openclaw-proxy.mjs -> OpenClaw Gateway (port 18789)
#   The proxy injects a script to fix the WebSocket URL in the frontend.

set -e

# Generate a random token for gateway auth
GATEWAY_TOKEN=$(openssl rand -hex 16)

# basePath matches the JupyterHub user URL prefix
BASE_PATH="${JUPYTERHUB_SERVICE_PREFIX%/}"

# Write OpenClaw config
mkdir -p /home/jovyan/.openclaw
cat > /home/jovyan/.openclaw/openclaw.json <<EOF
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "${GATEWAY_TOKEN}"
    },
    "controlUi": {
      "basePath": "${BASE_PATH}",
      "allowInsecureAuth": true,
      "dangerouslyDisableDeviceAuth": true
    }
  }
}
EOF
chown -R jovyan:jovyan /home/jovyan/.openclaw

# Start OpenClaw Gateway in background on 18789
echo "Starting OpenClaw Gateway (basePath: ${BASE_PATH})..."
su - jovyan -c "openclaw gateway > /tmp/openclaw.log 2>&1 &"

# Wait for gateway
timeout=30
while ! curl -s http://127.0.0.1:18789${BASE_PATH}/ > /dev/null 2>&1; do
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

# Start the proxy on 8888 (what JupyterHub connects to)
# It injects a script to fix the WebSocket URL and proxies WS upgrades
echo "Starting proxy on port 8888..."
export OPENCLAW_GATEWAY_TOKEN="${GATEWAY_TOKEN}"
exec node /usr/local/bin/openclaw-proxy.mjs
