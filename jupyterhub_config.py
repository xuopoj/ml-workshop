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

# User container image
c.DockerSpawner.image = os.environ.get('USER_IMAGE', 'ml-workshop-user:latest')

# Network - must match docker-compose network
c.DockerSpawner.network_name = 'ml-workshop-network'
c.DockerSpawner.use_internal_ip = True

# Container naming
c.DockerSpawner.name_template = 'ml-workshop-user-{username}'

# Remove containers when stopped
c.DockerSpawner.remove = True

# User containers need --privileged for DinD
c.DockerSpawner.extra_host_config = {
    'privileged': True,
}

# Default URL
c.DockerSpawner.default_url = '/lab'

# Notebook directory inside container
c.DockerSpawner.notebook_dir = '/home/jovyan'

# Environment variables for proxy (air-gapped environment)
c.DockerSpawner.environment = {
    'HTTP_PROXY': 'http://ml-workshop-proxy:8899',
    'HTTPS_PROXY': 'http://ml-workshop-proxy:8899',
    'http_proxy': 'http://ml-workshop-proxy:8899',
    'https_proxy': 'http://ml-workshop-proxy:8899',
    'NO_PROXY': 'localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy',
    'no_proxy': 'localhost,127.0.0.1,ml-workshop-hub,ml-workshop-proxy',
    'PIP_INDEX_URL': 'http://ml-workshop-proxy:3141/root/pypi/+simple/',
    'PIP_TRUSTED_HOST': 'ml-workshop-proxy',
}

# =============================================================================
# Volume Mounts - Different for Admin vs Regular Users
# =============================================================================

def pre_spawn_hook(spawner):
    """
    Configure volumes based on user role.
    Admins get read-write access, regular users get read-only.
    """
    username = spawner.user.name
    is_admin = spawner.user.admin

    # Base volumes for all users
    volumes = {
        # Persistent user data
        f'jupyter-{username}': '/home/jovyan/work',
        # Docker data for DinD (isolated per user)
        f'jupyter-{username}-docker': '/var/lib/docker',
    }

    # Workshop content - single volume with lessons/datasets/models subdirs
    if is_admin:
        # Admin: read-write access
        volumes['workshop-content'] = '/opt/workshop'
        spawner.log.info(f"Admin user {username}: read-write access")
    else:
        # Regular user: read-only access
        volumes['workshop-content'] = {'bind': '/opt/workshop', 'mode': 'ro'}
        spawner.log.info(f"Regular user {username}: read-only access")

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
