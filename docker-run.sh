#!/bin/bash
# Docker run commands for JupyterHub with DockerSpawner + DinD
# Each user gets their own container with isolated Docker daemon
# Includes proxy/cache services for air-gapped environments
#
# Usage:
#   ./docker-run.sh              # Normal mode (build images)
#   ./docker-run.sh --no-build   # Skip building images

set -e

NO_BUILD=false
for arg in "$@"; do
    case $arg in
        --no-build) NO_BUILD=true ;;
    esac
done
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

NETWORK_NAME="ml-workshop-network"
HUB_CONTAINER="ml-workshop-hub"
PROXY_CONTAINER="ml-workshop-proxy"
HUB_IMAGE="ml-workshop-hub:latest"
USER_IMAGE="ml-workshop-user:latest"
PROXY_IMAGE="ml-workshop-proxy:latest"

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
# Build images
# =============================================================================
if [ "$NO_BUILD" = false ]; then
    echo "Building images..."

    # Build proxy image (uses shared CA cert from certs/)
    docker build -t ${PROXY_IMAGE} -f Dockerfile.proxy .

    # Build hub image
    docker build -t ${HUB_IMAGE} -f Dockerfile.hub .

    # Build user image (uses shared CA cert from certs/)
    docker build -t ${USER_IMAGE} -f Dockerfile.user .
else
    echo "Skipping image builds (--no-build)"
fi

# =============================================================================
# Stop and remove existing containers
# =============================================================================
echo "Stopping existing containers..."
docker stop ${HUB_CONTAINER} ${PROXY_CONTAINER} 2>/dev/null || true
docker rm ${HUB_CONTAINER} ${PROXY_CONTAINER} 2>/dev/null || true

# =============================================================================
# Run Proxy/Cache Server (start first so it's available for user containers)
# =============================================================================
echo "Starting Proxy/Cache server..."

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

# =============================================================================
# Run JupyterHub
# =============================================================================
echo "Starting JupyterHub..."

# Optional mounts for local development
HUB_DEV_MOUNTS=""
if [ -f "$(pwd)/jupyterhub_config.py" ]; then
    HUB_DEV_MOUNTS="$HUB_DEV_MOUNTS -v $(pwd)/jupyterhub_config.py:/etc/jupyterhub/jupyterhub_config.py:ro"
fi
if [ -d "$(pwd)/templates" ]; then
    HUB_DEV_MOUNTS="$HUB_DEV_MOUNTS -v $(pwd)/templates:/etc/jupyterhub/templates:ro"
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
    -e TZ=Asia/Shanghai \
    -e ASCEND_VISIBLE_DEVICES=${ASCEND_VISIBLE_DEVICES:-4,5,6,7} \
    ${WORKSHOP_CONTENT_ENV} \
    ${STUDENT_WORK_ENV} \
    ${HUB_IMAGE}

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
