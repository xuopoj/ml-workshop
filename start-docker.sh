#!/bin/bash
# Start ML Workshop containers (hub + proxy)
# Skips restart if containers are already running with the same image
#
# Usage: ./start-docker.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

NETWORK_NAME="ml-workshop-network"
HUB_CONTAINER="ml-workshop-hub"
PROXY_CONTAINER="ml-workshop-proxy"
HUB_IMAGE="ml-workshop-hub:latest"
USER_IMAGE="ml-workshop-user:latest"
OPENCLAW_IMAGE="ml-workshop-openclaw:latest"
HCIE_IMAGE="ml-workshop-hcie:latest"
PROXY_IMAGE="ml-workshop-proxy:latest"

# Check if container is running with the expected image
# Returns 0 if running with same image, 1 otherwise
container_up_to_date() {
    local name="$1" expected_image="$2"
    local running_image
    running_image=$(docker inspect --format '{{.Config.Image}}' "$name" 2>/dev/null) || return 1
    local state
    state=$(docker inspect --format '{{.State.Running}}' "$name" 2>/dev/null) || return 1
    [ "$state" = "true" ] && [ "$running_image" = "$expected_image" ]
}

# =============================================================================
# Generate CA certificate if not exists
# =============================================================================
if [ ! -f certs/rootCA.crt ]; then
    echo "Generating CA certificate..."
    mkdir -p certs
    openssl genrsa -out certs/rootCA.key 4096
    openssl req -x509 -new -nodes -key certs/rootCA.key \
        -sha256 -days 3650 -out certs/rootCA.crt \
        -subj "/C=CN/ST=Shanghai/L=Shanghai/O=ML-Workshop/CN=ML-Workshop-CA"
    echo "CA certificate generated in certs/"
fi

# =============================================================================
# Create network if not exists
# =============================================================================
echo "Creating network..."
docker network create ${NETWORK_NAME} 2>/dev/null || echo "Network ${NETWORK_NAME} already exists"

# =============================================================================
# Create shared volumes
# =============================================================================
echo "Creating volumes..."

docker volume create jupyterhub-data 2>/dev/null || true
docker volume create workshop-content 2>/dev/null || true
docker volume create proxy-data 2>/dev/null || true

# Note: Per-user volumes (jupyter-{username}, jupyter-{username}-docker)
# are created automatically by DockerSpawner when users log in

# =============================================================================
# Run Proxy/Cache Server (start first so it's available for user containers)
# =============================================================================
if container_up_to_date ${PROXY_CONTAINER} ${PROXY_IMAGE}; then
    echo "Proxy/Cache server already running with ${PROXY_IMAGE}, skipping"
else
    echo "Starting Proxy/Cache server..."
    docker stop ${PROXY_CONTAINER} 2>/dev/null || true
    docker rm ${PROXY_CONTAINER} 2>/dev/null || true

    docker run -d \
        --name ${PROXY_CONTAINER} \
        --network ${NETWORK_NAME} \
        --restart unless-stopped \
        -p 8899:8899 \
        -p 8900:8900 \
        -p 3141:3141 \
        -p 3142:3142 \
        -v proxy-data:/data \
        -e WHISTLE_USERNAME="${WHISTLE_USERNAME:-admin}" \
        -e WHISTLE_PASSWORD="${WHISTLE_PASSWORD:-Passwort}" \
        ${PROXY_IMAGE}
fi

# =============================================================================
# Run JupyterHub
# =============================================================================
if container_up_to_date ${HUB_CONTAINER} ${HUB_IMAGE}; then
    echo "JupyterHub already running with ${HUB_IMAGE}, skipping"
else
    echo "Starting JupyterHub..."
    docker stop ${HUB_CONTAINER} 2>/dev/null || true
    docker rm ${HUB_CONTAINER} 2>/dev/null || true

    # Optional mounts for local development
    HUB_DEV_MOUNTS=""
    if [ -f "$(pwd)/hub/jupyterhub_config.py" ]; then
        HUB_DEV_MOUNTS="$HUB_DEV_MOUNTS -v $(pwd)/hub/jupyterhub_config.py:/etc/jupyterhub/jupyterhub_config.py:ro"
    fi
    if [ -d "$(pwd)/hub/templates" ]; then
        HUB_DEV_MOUNTS="$HUB_DEV_MOUNTS -v $(pwd)/hub/templates:/etc/jupyterhub/templates:ro"
    fi

    # Workshop content from host (contains lessons/, models/, datasets/)
    WORKSHOP_CONTENT_ENV=""
    if [ -d "$(pwd)/workshop-content" ]; then
        WORKSHOP_CONTENT_ENV="-e WORKSHOP_CONTENT=$(pwd)/workshop-content"
    fi

    # Student work directory (each student gets their own subdir)
    # Mount to hub so it can create user subdirs before spawning
    STUDENT_WORK_ENV=""
    STUDENT_WORK_MOUNT=""
    if [ -d "$(pwd)/student-work" ]; then
        STUDENT_WORK_ENV="-e STUDENT_WORK=/data/student-work -e STUDENT_WORK_HOST=$(pwd)/student-work"
        STUDENT_WORK_MOUNT="-v $(pwd)/student-work:/data/student-work"
    fi

    docker run -d \
        --name ${HUB_CONTAINER} \
        --network ${NETWORK_NAME} \
        --restart unless-stopped \
        -p 28000:8000 \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v jupyterhub-data:/opt/jupyterhub \
        ${HUB_DEV_MOUNTS} \
        ${STUDENT_WORK_MOUNT} \
        -e USER_IMAGE=${USER_IMAGE} \
        -e OPENCLAW_IMAGE=${OPENCLAW_IMAGE} \
        -e HCIE_IMAGE=${HCIE_IMAGE} \
        -e OPENCLAW_GATEWAY_HOST=${OPENCLAW_GATEWAY_HOST:-100.102.191.233} \
        -e VSCODE_SSH_HOST=${VSCODE_SSH_HOST:-100.102.191.233} \
        -e TZ=Asia/Shanghai \
        -e ASCEND_VISIBLE_DEVICES=${ASCEND_VISIBLE_DEVICES:-4,5,6,7} \
        ${WORKSHOP_CONTENT_ENV} \
        ${STUDENT_WORK_ENV} \
        ${HUB_IMAGE}
fi

echo ""
echo "========================================"
echo "ML Workshop Started!"
echo "========================================"
echo ""
echo "Services:"
echo "  JupyterHub:       http://localhost:28000"
echo "  Whistle Proxy UI: http://localhost:8900 (user: ${WHISTLE_USERNAME:-admin}, pass: ${WHISTLE_PASSWORD:-Passwort})"
echo "  devpi (pip):      http://localhost:3141"
echo "  apt-cacher-ng:    http://localhost:3142"
echo ""
echo "CA Certificate:     certs/rootCA.crt"
echo ""
echo "Commands:"
echo "  View logs:    docker logs -f ${HUB_CONTAINER}"
echo "                docker logs -f ${PROXY_CONTAINER}"
echo "  Stop all:     docker stop ${HUB_CONTAINER} ${PROXY_CONTAINER} && docker rm ${HUB_CONTAINER} ${PROXY_CONTAINER}"
echo ""
