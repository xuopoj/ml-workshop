ARG PYTORCH_NPU_IMAGE=pytorch:2.5.1-npu-910b

# =============================================================================
# Stage 1: Build code-server with extensions
# =============================================================================
FROM ubuntu:22.04 AS vscode
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -fsSL https://code-server.dev/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*
RUN code-server --install-extension ms-python.python \
    && code-server --install-extension ms-toolsai.jupyter \
    && code-server --install-extension charliermarsh.ruff

# =============================================================================
# Stage 2: User Jupyter Container with Docker-in-Docker
# =============================================================================
FROM ${PYTORCH_NPU_IMAGE}

USER root

# Install Docker CLI and daemon for DinD
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg lsb-release sudo openssh-server \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    jupyterlab jupyterhub \
    jupyterlab-git ipywidgets jupyter-server-proxy \
    numpy pandas matplotlib seaborn plotly scikit-learn

# Install ML/AI packages with torch pinned
RUN pip install --no-cache-dir \
    --no-deps transformers datasets accelerate huggingface_hub \
    langchain langchain-community openai tiktoken && \
    pip install --no-cache-dir \
    torch==2.5.1 torch-npu==2.5.1 torchvision==0.20.1 \
    regex requests tqdm pyyaml filelock 'fsspec<=2025.10.0' packaging \
    safetensors tokenizers 'huggingface-hub<1.0,>=0.34.0' \
    aiohttp pydantic jsonpatch langsmith tenacity \
    'dill>=0.3.0,<0.4.1' 'multiprocess<0.70.19' 'pyarrow>=21.0.0' xxhash \
    'dataclasses-json>=0.6.7,<0.7.0' 'httpx-sse>=0.4.0,<1.0.0' \
    'langchain-core>=1.0.1,<2.0.0' 'langchain-classic>=1.0.0,<2.0.0' \
    'pydantic-settings>=2.10.1,<3.0.0' 'jiter>=0.10.0,<1' sniffio

# Copy code-server and pre-installed extensions from build stage
COPY --from=vscode /usr/lib/code-server /usr/lib/code-server
COPY --from=vscode /usr/bin/code-server /usr/bin/code-server
COPY --from=vscode /root/.local/share/code-server/extensions /root/.local/share/code-server/extensions

# Configure jupyter-server-proxy: /vscode/ -> code-server on 8080
RUN mkdir -p /etc/jupyter && printf '\
c.ServerProxy.servers = {\n\
    "vscode": {\n\
        "command": [],\n\
        "port": 8080,\n\
        "absolute_url": False,\n\
        "timeout": 30,\n\
        "launcher_entry": {\n\
            "enabled": True,\n\
            "title": "VS Code",\n\
        },\n\
    }\n\
}\n' > /etc/jupyter/jupyter_server_config.py

# Copy startup scripts and setup guide template
COPY user/start-notebook.sh user/start-vscode.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-notebook.sh /usr/local/bin/start-vscode.sh
COPY user/getstarted.md /usr/local/share/getstarted.md

# Copy CA certificate for proxy (enables HTTPS through Whistle)
COPY --chmod=644 certs/rootCA.crt /usr/local/share/ca-certificates/ml-workshop-ca.crt
RUN update-ca-certificates || true

# Configure proxy for all tools (git, curl, wget, etc.)
# ENV makes it available to entrypoint/JupyterLab; profile.d makes it available to SSH sessions
ENV HTTP_PROXY=http://ml-workshop-proxy:8899 \
    HTTPS_PROXY=http://ml-workshop-proxy:8899 \
    http_proxy=http://ml-workshop-proxy:8899 \
    https_proxy=http://ml-workshop-proxy:8899 \
    NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com \
    no_proxy=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com
RUN printf '#!/bin/sh\nexport HTTP_PROXY=http://ml-workshop-proxy:8899\nexport HTTPS_PROXY=http://ml-workshop-proxy:8899\nexport http_proxy=http://ml-workshop-proxy:8899\nexport https_proxy=http://ml-workshop-proxy:8899\nexport NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com\nexport no_proxy=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com\n' \
    > /etc/profile.d/proxy.sh
# Also write to /etc/environment for non-login SSH sessions (VS Code Remote)
RUN printf 'HTTP_PROXY=http://ml-workshop-proxy:8899\nHTTPS_PROXY=http://ml-workshop-proxy:8899\nhttp_proxy=http://ml-workshop-proxy:8899\nhttps_proxy=http://ml-workshop-proxy:8899\nNO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com\nno_proxy=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com\n' \
    >> /etc/environment

# Configure pip to use local devpi cache (can be overridden by env vars)
RUN mkdir -p /etc/pip \
    && printf "[global]\nindex-url = http://ml-workshop-proxy:3141/root/pypi/+simple/\ntrusted-host = ml-workshop-proxy\n" > /etc/pip/pip.conf

# Configure apt to use apt-cacher-ng (can be overridden)
RUN printf 'Acquire::http::Proxy "http://ml-workshop-proxy:3142";\n' > /etc/apt/apt.conf.d/00proxy

# Set up workshop directories (will be mounted)
RUN mkdir -p /opt/workshop/{lessons,datasets,models} /root/work

# SSH and code-server runtime directories
RUN mkdir -p /run/sshd

WORKDIR /root/work
EXPOSE 8888 22

# Start script handles DinD daemon + JupyterLab
CMD ["/usr/local/bin/start-notebook.sh"]
