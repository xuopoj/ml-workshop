#!/bin/bash
# Docker run commands for JupyterHub with DockerSpawner + DinD
# Each user gets their own container with isolated Docker daemon
# Includes proxy/cache services for air-gapped environments

set -e

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
echo "Building images..."

# Build proxy image (uses shared CA cert from certs/)
docker build -t ${PROXY_IMAGE} -f Dockerfile.proxy .

# Build hub image
docker build -t ${HUB_IMAGE} -f Dockerfile.hub .

# Build user image (uses shared CA cert from certs/)
docker build -t ${USER_IMAGE} -f Dockerfile.user .

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
    ${PROXY_IMAGE}

# =============================================================================
# Run JupyterHub
# =============================================================================
echo "Starting JupyterHub..."

docker run -d \
    --name ${HUB_CONTAINER} \
    --network ${NETWORK_NAME} \
    --restart unless-stopped \
    -p 8000:8000 \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v jupyterhub-data:/opt/jupyterhub \
    -e USER_IMAGE=${USER_IMAGE} \
    -e TZ=Asia/Shanghai \
    ${HUB_IMAGE}

echo ""
echo "========================================"
echo "ML Workshop Started!"
echo "========================================"
echo ""
echo "Services:"
echo "  JupyterHub:       http://localhost:8000"
echo "  Whistle Proxy UI: http://localhost:8900"
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
