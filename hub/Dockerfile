# JupyterHub Orchestrator
# This container only runs JupyterHub - users get spawned in separate containers

FROM python:3.11-slim

# Install Node.js and configurable-http-proxy
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g configurable-http-proxy

# Install JupyterHub with DockerSpawner
RUN pip install --no-cache-dir \
    jupyterhub \
    jupyterhub-idle-culler \
    jupyterhub-nativeauthenticator \
    dockerspawner

# Create directories
RUN mkdir -p /etc/jupyterhub /opt/jupyterhub /etc/jupyterhub/templates

# Copy configuration and templates
COPY hub/jupyterhub_config.py /etc/jupyterhub/jupyterhub_config.py
COPY hub/templates/ /etc/jupyterhub/templates/

WORKDIR /etc/jupyterhub
EXPOSE 8000

CMD ["jupyterhub", "--config", "/etc/jupyterhub/jupyterhub_config.py"]
