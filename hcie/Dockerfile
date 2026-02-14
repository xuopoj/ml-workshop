# Multi-environment conda setup for HCIE Ascend NPU project
ARG BASE_IMAGE=cann:8.0rc1-910b
FROM ${BASE_IMAGE}

WORKDIR /workspace

# Copy CA certificate for proxy (enables HTTPS through Whistle)
COPY --chmod=644 certs/rootCA.crt /usr/local/share/ca-certificates/ml-workshop-ca.crt
RUN update-ca-certificates || true

# Configure proxy for all tools (git, curl, wget, etc.)
ENV HTTP_PROXY=http://ml-workshop-proxy:8899 \
    HTTPS_PROXY=http://ml-workshop-proxy:8899 \
    http_proxy=http://ml-workshop-proxy:8899 \
    https_proxy=http://ml-workshop-proxy:8899 \
    NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com \
    no_proxy=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com

# Configure apt to use apt-cacher-ng
RUN printf 'Acquire::http::Proxy "http://ml-workshop-proxy:3142";\n' > /etc/apt/apt.conf.d/00proxy

# Configure pip to use devpi cache
RUN mkdir -p /etc/pip \
    && printf "[global]\nindex-url = http://ml-workshop-proxy:3141/root/pypi/+simple/\ntrusted-host = ml-workshop-proxy\ntimeout = 120\n" > /etc/pip/pip.conf

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget bzip2 ca-certificates git zsh curl openssh-server \
    && rm -rf /var/lib/apt/lists/*

# SSH runtime directory
RUN mkdir -p /run/sshd

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

# Create directory structure for offline wheels
RUN mkdir -p /home/ma-user/pkg \
             /home/ma-user/mindformers/output

# Copy offline wheel packages
COPY hcie/wheels/torch_npu-2.2.0.post2-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl \
     /home/ma-user/pkg/
COPY hcie/wheels/mindformers-1.1.0-py3-none-any.whl \
     /home/ma-user/mindformers/output/

# Copy requirements files
COPY hcie/requirements-env0.txt hcie/requirements-env1.txt /workspace/

# --- env0: Python 3.9 ---
RUN conda create -n env0 python=3.9 -y && conda clean -afy

# Install transformers first (pulls tokenizers<0.14), then force tokenizers 0.15.0,
# then install remaining deps (skipping transformers/tokenizers to avoid conflict)
RUN conda run -n env0 pip install --no-cache-dir transformers==4.29.0 && \
    conda run -n env0 pip install --no-cache-dir --upgrade --force-reinstall tokenizers==0.15.0 && \
    conda run -n env0 bash -c "grep -v '^transformers==' /workspace/requirements-env0.txt | grep -v '^tokenizers==' | pip install --no-cache-dir -r /dev/stdin"
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

# Install Oh My Zsh (bypass proxy - raw.githubusercontent.com may not be reachable through proxy at build time)
RUN env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# Shell configuration
ENV SHELL=/usr/bin/zsh
RUN chsh -s $(which zsh)
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate env0" >> /root/.zshrc && \
    echo "source /opt/conda/etc/profile.d/conda.sh && conda activate env0" >> /root/.zprofile && \
    echo "source /opt/conda/etc/profile.d/conda.sh && conda activate env0" >> /root/.bashrc

# Proxy env for interactive shells (zsh/bash/SSH sessions)
RUN printf '#!/bin/sh\nexport HTTP_PROXY=http://ml-workshop-proxy:8899\nexport HTTPS_PROXY=http://ml-workshop-proxy:8899\nexport http_proxy=http://ml-workshop-proxy:8899\nexport https_proxy=http://ml-workshop-proxy:8899\nexport NO_PROXY=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com\nexport no_proxy=localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com\n' \
    > /etc/profile.d/proxy.sh
# Source /etc/profile.d/ for non-login SSH sessions (VS Code Remote-SSH)
RUN printf '#!/bin/sh\nfor f in /etc/profile.d/*.sh; do . "$f"; done\n' > /etc/ssh/sshrc \
    && chmod +x /etc/ssh/sshrc

COPY hcie/getstarted.md /usr/local/share/getstarted.md
COPY hcie/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]
