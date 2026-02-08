#!/bin/bash
# Start script for user containers with Docker-in-Docker

set -e

HOME_DIR="/root"
WORK_DIR="${HOME_DIR}/work"

# =============================================================================
# SSH + code-server (only when VSCODE_SSH_PORT is set)
# =============================================================================
if [ -n "${VSCODE_SSH_PORT}" ]; then
    /usr/local/bin/start-vscode.sh "${WORK_DIR}"
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
if [ ! -L "${WORK_DIR}/workshop" ] && [ -d /opt/workshop ]; then
    ln -sf /opt/workshop "${WORK_DIR}/workshop"
fi

# =============================================================================
# Start JupyterLab
# =============================================================================

exec jupyterhub-singleuser \
    --ip=0.0.0.0 \
    --port=8888 \
    --notebook-dir="${WORK_DIR}" \
    --ServerApp.default_url=/lab \
    --ServerApp.allow_root=True
