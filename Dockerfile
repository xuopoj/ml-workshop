# ML Workshop with JupyterHub
# Multi-user environment with JupyterLab and NPU support

ARG PYTORCH_NPU_IMAGE=pytorch:2.5.1-npu-910b
FROM ${PYTORCH_NPU_IMAGE}

USER root

# Install Node.js and configurable-http-proxy (required for JupyterHub)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g configurable-http-proxy

# Install Python packages
# Note: Pin torch versions to prevent upgrades that would remove torch_npu
RUN pip install --no-cache-dir \
    jupyterhub jupyterlab jupyterhub-idle-culler \
    jupyterhub-nativeauthenticator \
    jupyterlab-git ipywidgets \
    numpy pandas matplotlib seaborn plotly scikit-learn

# Install ML/AI packages with torch pinned to avoid version conflicts
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

# Copy configuration files
COPY spawn-wrapper.sh /usr/local/bin/spawn-wrapper.sh
COPY jupyterhub_config.py single_user_spawner.py /etc/jupyterhub/
RUN chmod +x /usr/local/bin/spawn-wrapper.sh

# Set up workshop environment
RUN mkdir -p /opt/workshop/{lessons,datasets,models,student-work} /etc/jupyterhub \
    && mkdir -p /opt/workshop/admin-edit/{lessons,datasets,models} \
    && chmod -R 755 /opt/workshop

# Create jupyter user for compatibility (kept for future flexibility)
# Note: All notebooks now run as root for NPU device access
# User isolation is maintained at JupyterHub database level
RUN useradd -m -s /bin/bash jupyter \
    && mkdir -p /home/jupyter/.jupyter

# Configure Jupyter defaults - allow root for NPU access
RUN mkdir -p /root/.jupyter \
    && printf "c.ServerApp.root_dir = '/opt/jupyterhub/users/{username}'\nc.ServerApp.allow_root = True\n" > /root/.jupyter/jupyter_lab_config.py

# Set permissions for workshop directories
# Running as root for NPU access, so ownership is already correct
# Regular directories are read-only (mounted as :ro)
# admin-edit directories are writable (mounted as :rw)
RUN chmod -R 755 /opt/workshop/admin-edit

WORKDIR /etc/jupyterhub
EXPOSE 8000 8081

CMD ["jupyterhub", "--config", "/etc/jupyterhub/jupyterhub_config.py"]
