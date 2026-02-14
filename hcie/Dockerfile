# Multi-environment conda setup for HCIE Ascend NPU project
ARG BASE_IMAGE=cann:8.0rc1-910b
FROM ${BASE_IMAGE}

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget bzip2 ca-certificates git zsh curl openssh-server \
    && rm -rf /var/lib/apt/lists/*

# SSH runtime directory
RUN mkdir -p /run/sshd

# Install jupyterhub-singleuser + jupyterlab at system level (required by DockerSpawner)
RUN pip install --no-cache-dir jupyterhub jupyterlab

# Install Miniconda
ARG MINICONDA_VERSION=latest
ENV CONDA_DIR=/opt/conda
ENV PATH=${CONDA_DIR}/bin:${PATH}

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}-Linux-aarch64.sh -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p ${CONDA_DIR} && \
    rm /tmp/miniconda.sh && \
    conda clean -afy && \
    echo ". ${CONDA_DIR}/etc/profile.d/conda.sh" >> ~/.bashrc

SHELL ["/bin/bash", "--login", "-c"]

RUN conda tos accept

# Copy requirements files
COPY hcie/requirements-env0.txt hcie/requirements-env1.txt /workspace/

# --- env0: Python 3.9 ---
RUN conda create -n env0 python=3.9 -y && conda clean -afy

# Install deps first (skipping transformers/tokenizers), then pin transformers + tokenizers last
RUN conda run -n env0 bash -c "grep -v '^transformers==' /workspace/requirements-env0.txt | grep -v '^tokenizers==' | pip install --no-cache-dir -r /dev/stdin" && \
    conda run -n env0 pip install --no-cache-dir --no-deps transformers==4.29.0 tokenizers==0.15.0
RUN conda run -n env0 python -m ipykernel install --name env0 --display-name "env0 (NLP/LLM)"

# --- env1: Python 3.9 ---
RUN conda create -n env1 python=3.9 -y && conda clean -afy

RUN conda run -n env1 pip install --no-cache-dir -r /workspace/requirements-env1.txt
RUN conda run -n env1 python -m ipykernel install --name env1 --display-name "env1 (CV)"

# Default environment
ENV CONDA_DEFAULT_ENV=env0

# Clean up build artifacts
RUN conda clean -afy && rm -rf /workspace/requirements-*.txt

WORKDIR /root/share

# Install Oh My Zsh (skip if base image already has it)
RUN [ -d /root/.oh-my-zsh ] || sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Shell configuration
ENV SHELL=/usr/bin/zsh
RUN chsh -s $(which zsh)
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate env0" >> /root/.zshrc && \
    echo "source /opt/conda/etc/profile.d/conda.sh && conda activate env0" >> /root/.zprofile && \
    echo "source /opt/conda/etc/profile.d/conda.sh && conda activate env0" >> /root/.bashrc

# =============================================================================
# Runtime proxy configuration (only used when container runs in workshop network)
# =============================================================================

# CA certificate for Whistle HTTPS proxy
COPY certs/rootCA.crt /usr/local/share/ca-certificates/ml-workshop-ca.crt
RUN chmod 644 /usr/local/share/ca-certificates/ml-workshop-ca.crt && \
    update-ca-certificates || true

# Proxy env vars for all processes
ENV HTTP_PROXY=http://ml-workshop-proxy:8899 \
    HTTPS_PROXY=http://ml-workshop-proxy:8899 \
    http_proxy=http://ml-workshop-proxy:8899 \
    https_proxy=http://ml-workshop-proxy:8899 \
    NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com \
    no_proxy=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com

# pip → devpi cache
RUN mkdir -p /etc/pip \
    && printf "[global]\nindex-url = http://ml-workshop-proxy:3141/root/pypi/+simple/\ntrusted-host = ml-workshop-proxy\ntimeout = 120\n" > /etc/pip/pip.conf

# apt → apt-cacher-ng
RUN printf 'Acquire::http::Proxy "http://ml-workshop-proxy:3142";\n' > /etc/apt/apt.conf.d/00proxy

# Proxy for interactive shells (zsh/bash/SSH sessions)
RUN printf '#!/bin/sh\nexport HTTP_PROXY=http://ml-workshop-proxy:8899\nexport HTTPS_PROXY=http://ml-workshop-proxy:8899\nexport http_proxy=http://ml-workshop-proxy:8899\nexport https_proxy=http://ml-workshop-proxy:8899\nexport NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com\nexport no_proxy=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com\n' \
    > /etc/profile.d/proxy.sh
# Source /etc/profile.d/ for non-login SSH sessions (VS Code Remote-SSH)
RUN printf '#!/bin/sh\nfor f in /etc/profile.d/*.sh; do . "$f"; done\n' > /etc/ssh/sshrc \
    && chmod +x /etc/ssh/sshrc

COPY hcie/getstarted.md /usr/local/share/getstarted.md
COPY hcie/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22 8888

ENTRYPOINT ["/entrypoint.sh"]
CMD ["jupyterhub-singleuser", "--ip=0.0.0.0", "--port=8888", "--allow-root"]
