# OpenClaw Showcase Container
# Node.js base with OpenClaw AI assistant + JupyterLab

FROM node:24

# Install Python and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv sudo \
    && rm -rf /var/lib/apt/lists/*

# Install OpenClaw
RUN npm install -g openclaw@latest

# Install JupyterLab + JupyterHub (for singleuser server with terminal access)
RUN pip install --no-cache-dir --break-system-packages \
    jupyterlab jupyterhub

# Copy CA certificate for proxy
COPY --chmod=644 certs/rootCA.crt /usr/local/share/ca-certificates/ml-workshop-ca.crt
RUN update-ca-certificates

# Configure runtime proxies (apt-cacher-ng, pip cache)
RUN printf 'Acquire::http::Proxy "http://ml-workshop-proxy:3142";\n' > /etc/apt/apt.conf.d/00proxy \
    && mkdir -p /etc/pip \
    && printf "[global]\nindex-url = http://ml-workshop-proxy:3141/root/pypi/+simple/\ntrusted-host = ml-workshop-proxy\n" > /etc/pip/pip.conf

# Enable Node.js native proxy support (reads HTTP_PROXY/HTTPS_PROXY env vars)
ENV NODE_USE_ENV_PROXY=1

# Rename 'node' user (UID 1000) to 'jovyan' (JupyterHub convention)
RUN usermod -l jovyan -d /home/jovyan -m node \
    && groupmod -n jovyan node \
    && mkdir -p /home/jovyan/.jupyter \
    && chown -R jovyan:jovyan /home/jovyan \
    && echo "jovyan ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Copy startup script, config template, and getting-started template
COPY openclaw/start.sh /usr/local/bin/start-openclaw.sh
COPY openclaw/openclaw.json /usr/local/share/openclaw.json
COPY openclaw/getting-started.md /usr/local/share/openclaw-getting-started.md
RUN chmod +x /usr/local/bin/start-openclaw.sh

WORKDIR /home/jovyan
EXPOSE 8888 18789

CMD ["/usr/local/bin/start-openclaw.sh"]
