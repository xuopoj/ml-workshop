#!/bin/bash
# Start script for user containers with Docker-in-Docker

set -e

# Start Docker daemon in background (DinD)
# The --storage-driver=vfs is safest for nested containers
echo "Starting Docker daemon..."
dockerd --host=unix:///var/run/docker.sock \
        --storage-driver=vfs \
        --iptables=false \
        --bridge=none \
        > /var/log/dockerd.log 2>&1 &

# Wait for Docker daemon to be ready
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
    # Show Docker version for user
    docker --version
fi

# Create symlink to workshop materials if not exists
if [ ! -L /home/jovyan/workshop ] && [ -d /opt/workshop ]; then
    ln -sf /opt/workshop /home/jovyan/workshop
fi

# Start JupyterLab
# $JUPYTERHUB_API_TOKEN and other env vars are set by DockerSpawner
exec jupyterhub-singleuser \
    --ip=0.0.0.0 \
    --port=8888 \
    --notebook-dir=/home/jovyan \
    --ServerApp.default_url=/lab \
    --ServerApp.allow_root=True
