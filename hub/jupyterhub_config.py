# JupyterHub Configuration with DockerSpawner
# Each user gets their own container with isolated Docker daemon (DinD)
# v5: Signup with admin approval

import os

# =============================================================================
# Core JupyterHub Settings
# =============================================================================

c.JupyterHub.bind_url = 'http://0.0.0.0:8000'
c.JupyterHub.hub_ip = '0.0.0.0'
# Hub must be accessible from spawned containers via Docker network
c.JupyterHub.hub_connect_ip = 'ml-workshop-hub'

# Custom templates (adds Authorize link to navbar for admins)
c.JupyterHub.template_paths = ['/etc/jupyterhub/templates']

# =============================================================================
# Authentication - NativeAuthenticator with Admin Approval
# =============================================================================

c.JupyterHub.authenticator_class = 'nativeauthenticator.NativeAuthenticator'

c.Authenticator.admin_users = {'superuser'}

# Let NativeAuthenticator handle all authorization (bypass JupyterHub's allowed_users check)
c.Authenticator.allow_all = True

# Signup requires admin approval (open_signup = False is the default)
c.NativeAuthenticator.open_signup = False
c.NativeAuthenticator.enable_signup = True
c.NativeAuthenticator.ask_email_on_signup = False  # Collect email for contact
c.NativeAuthenticator.minimum_password_length = 8
c.NativeAuthenticator.check_common_password = True

# Security: block after failed login attempts
c.NativeAuthenticator.allowed_failed_logins = 5
c.NativeAuthenticator.seconds_before_next_try = 300  # 5 min lockout

# =============================================================================
# DockerSpawner Configuration
# =============================================================================

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# User container images - users pick from a dropdown when spawning
c.DockerSpawner.allowed_images = {
    'ML Workshop': os.environ.get('USER_IMAGE', 'ml-workshop-user:latest'),
    'OpenClaw Showcase': os.environ.get('OPENCLAW_IMAGE', 'ml-workshop-openclaw:latest'),
    'HCIE Lab': os.environ.get('HCIE_IMAGE', 'ml-workshop-hcie:latest'),
}
c.DockerSpawner.image = os.environ.get('USER_IMAGE', 'ml-workshop-user:latest')

# Network - must match docker-compose network
c.DockerSpawner.network_name = 'ml-workshop-network'
c.DockerSpawner.use_internal_ip = True

# Container naming
c.DockerSpawner.name_template = 'ml-workshop-user-{username}'

# Remove containers when stopped
c.DockerSpawner.remove = True

# User containers need --privileged for DinD
extra_host_config = {
    'privileged': True,
}

# Mount Ascend NPU devices if ASCEND_VISIBLE_DEVICES is set
# Example: ASCEND_VISIBLE_DEVICES=0,1,2,3 or ASCEND_VISIBLE_DEVICES=all
ascend_devices = os.environ.get('ASCEND_VISIBLE_DEVICES', '')
if ascend_devices:
    devices = [
        '/dev/davinci_manager:/dev/davinci_manager',
        '/dev/devmm_svm:/dev/devmm_svm',
        '/dev/hisi_hdc:/dev/hisi_hdc',
    ]
    if ascend_devices.lower() == 'all':
        for i in range(8):
            devices.append(f'/dev/davinci{i}:/dev/davinci{i}')
    else:
        for idx in ascend_devices.split(','):
            devices.append(f'/dev/davinci{idx.strip()}:/dev/davinci{idx.strip()}')

    extra_host_config['devices'] = devices
    extra_host_config['binds'] = {
        '/usr/local/Ascend/driver': {'bind': '/usr/local/Ascend/driver', 'mode': 'ro'},
        '/usr/local/sbin/npu-smi': {'bind': '/usr/local/sbin/npu-smi', 'mode': 'ro'},
    }

c.DockerSpawner.extra_host_config = extra_host_config

# Default URL
c.DockerSpawner.default_url = '/lab'

# Notebook directory inside container
c.DockerSpawner.notebook_dir = '/root/work'

# Environment variables for proxy (air-gapped environment)
c.DockerSpawner.environment = {
    'HTTP_PROXY': 'http://ml-workshop-proxy:8899',
    'HTTPS_PROXY': 'http://ml-workshop-proxy:8899',
    'http_proxy': 'http://ml-workshop-proxy:8899',
    'https_proxy': 'http://ml-workshop-proxy:8899',
    'NO_PROXY': 'localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com',
    'no_proxy': 'localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy,*.huawei.com',
    'PIP_INDEX_URL': 'http://ml-workshop-proxy:3141/root/pypi/+simple/',
    'PIP_TRUSTED_HOST': 'ml-workshop-proxy',
}

# =============================================================================
# Volume Mounts - Different for Admin vs Regular Users
# =============================================================================

# Host paths (set via environment variables):
# - WORKSHOP_CONTENT: lessons/, models/, datasets/
# - STUDENT_WORK: shared dir, each student gets {STUDENT_WORK}/{username}/

import os as _os
import json
import fcntl

OPENCLAW_PORT_BASE = 18789
OPENCLAW_PORT_FILE = '/opt/jupyterhub/openclaw-ports.json'

SSH_PORT_BASE = 22222
SSH_PORT_FILE = '/opt/jupyterhub/ssh-ports.json'

def _get_port(username, port_file, port_base):
    """Assign a sequential port per user, persisted in a JSON file."""
    try:
        with open(port_file, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            ports = json.load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
    except (FileNotFoundError, json.JSONDecodeError):
        ports = {}
    if username in ports:
        return ports[username]
    port = port_base + len(ports) + 1
    ports[username] = port
    with open(port_file, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(ports, f)
        fcntl.flock(f, fcntl.LOCK_UN)
    return port

def pre_spawn_hook(spawner):
    username = spawner.user.name
    is_admin = spawner.user.admin

    # Determine container type based on selected image
    openclaw_image = os.environ.get('OPENCLAW_IMAGE', 'ml-workshop-openclaw:latest')
    hcie_image = os.environ.get('HCIE_IMAGE', 'ml-workshop-hcie:latest')
    selected = spawner.user_options.get('image', '')
    resolved_image = spawner.allowed_images.get(selected, spawner.image)
    is_openclaw = (resolved_image == openclaw_image)
    is_hcie = (resolved_image == hcie_image)

    if is_openclaw:
        home_dir = '/home/jovyan'
    elif is_hcie:
        home_dir = '/root/share'
    else:
        home_dir = '/root/work'
    spawner.notebook_dir = home_dir

    # OpenClaw: expose gateway port directly on host
    if is_openclaw:
        host_port = _get_port(username, OPENCLAW_PORT_FILE, OPENCLAW_PORT_BASE)
        spawner.extra_create_kwargs.setdefault('ports', {})['18789/tcp'] = {}
        spawner.extra_host_config.setdefault('port_bindings', {})['18789/tcp'] = ('0.0.0.0', host_port)
        spawner.environment['OPENCLAW_HOST_PORT'] = str(host_port)
        spawner.environment['OPENCLAW_GATEWAY_HOST'] = os.environ.get('OPENCLAW_GATEWAY_HOST', 'localhost')

    # ML Workshop & HCIE: expose SSH port for VSCode Remote
    if not is_openclaw:
        ssh_port = _get_port(username, SSH_PORT_FILE, SSH_PORT_BASE)
        spawner.extra_create_kwargs.setdefault('ports', {})['22/tcp'] = {}
        spawner.extra_host_config.setdefault('port_bindings', {})['22/tcp'] = ('0.0.0.0', ssh_port)
        spawner.environment['VSCODE_SSH_PORT'] = str(ssh_port)
        spawner.environment['VSCODE_SSH_HOST'] = os.environ.get('VSCODE_SSH_HOST', 'localhost')
        if is_hcie:
            spawner.environment['SSH_PORT'] = str(ssh_port)
            spawner.environment['SSH_HOST'] = os.environ.get('VSCODE_SSH_HOST', 'localhost')

    volumes = {}
    volumes[f'jupyter-{username}'] = home_dir

    # Docker-in-Docker volume for ML Workshop only
    if not is_openclaw and not is_hcie:
        volumes[f'jupyter-{username}-docker'] = '/var/lib/docker'

    # Workshop content (skip for OpenClaw and HCIE)
    if not is_openclaw and not is_hcie:
        workshop_path = os.environ.get('WORKSHOP_CONTENT')
        if workshop_path:
            mode = 'rw' if is_admin else 'ro'
            volumes[workshop_path] = {'bind': '/opt/workshop', 'mode': mode}
        else:
            if is_admin:
                volumes['workshop-content'] = '/opt/workshop'
            else:
                volumes['workshop-content'] = {'bind': '/opt/workshop', 'mode': 'ro'}

    # Student work: admins see all, students see only their subdir
    student_work_path = os.environ.get('STUDENT_WORK')
    student_work_host = os.environ.get('STUDENT_WORK_HOST')
    if student_work_path and student_work_host:
        student_work_bind = f'{home_dir}/student-work'
        if is_admin:
            volumes[student_work_host] = {'bind': student_work_bind, 'mode': 'rw'}
        else:
            user_dir_local = f'{student_work_path}/{username}'
            _os.makedirs(user_dir_local, exist_ok=True)
            user_dir_host = f'{student_work_host}/{username}'
            volumes[user_dir_host] = {'bind': student_work_bind, 'mode': 'rw'}

    spawner.volumes = volumes

c.Spawner.pre_spawn_hook = pre_spawn_hook

# =============================================================================
# Resource Limits
# =============================================================================

c.DockerSpawner.cpu_limit = 4
c.DockerSpawner.mem_limit = '8G'

# =============================================================================
# Timeouts
# =============================================================================

c.DockerSpawner.start_timeout = 180
c.DockerSpawner.http_timeout = 120

# Pull image if not present
c.DockerSpawner.pull_policy = 'ifnotpresent'

# =============================================================================
# Services - Idle Culler
# =============================================================================

import sys
c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [
            sys.executable,
            '-m', 'jupyterhub_idle_culler',
            '--timeout=7200',  # 2 hours
        ],
    }
]

# =============================================================================
# Database
# =============================================================================

c.JupyterHub.db_url = 'sqlite:////opt/jupyterhub/jupyterhub.sqlite'

# =============================================================================
# Logging
# =============================================================================

c.JupyterHub.log_level = 'INFO'
