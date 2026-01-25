# ML Workshop

Deep learning tutorial using JupyterHub with Docker.

## Quick Start

```bash
./docker-run.sh                        # Build images, start all containers
docker logs ml-workshop-hub            # View hub logs
docker stop ml-workshop-hub ml-workshop-proxy && docker rm ml-workshop-hub ml-workshop-proxy  # Stop all
```

Access: http://localhost:8000

## Architecture

```
docker-run.sh           # Main startup script
jupyterhub_config.py    # Hub config with DockerSpawner + NativeAuthenticator
Dockerfile.hub          # JupyterHub orchestrator (ml-workshop-hub)
Dockerfile.proxy        # Cache server (ml-workshop-proxy)
Dockerfile.user         # User container (ml-workshop-user-{username})
Dockerfile.user.mac     # User container (Mac testing)
templates/              # Custom JupyterHub templates
```

## Container Names

- `ml-workshop-hub` - JupyterHub orchestrator
- `ml-workshop-proxy` - Cache server (whistle, devpi, apt-cacher-ng)
- `ml-workshop-user-{username}` - Per-user Jupyter containers

## Proxy Configuration

Configure upstream proxy via Whistle UI: http://localhost:8900

## User Management

Uses NativeAuthenticator with admin approval workflow:

1. Users sign up at `/hub/signup`
2. Admin approves at `/hub/authorize` (link in navbar for admins)
3. Approved users can log in

- Admins: defined in `jupyterhub_config.py` (`superuser` by default)
- Admins get read-write access to workshop content

## Lessons

Notebooks in `lessons/`. Diagram code in `diagrams/` submodules.

### Language

- Diagram labels: English (font issues)
- Markdown: Chinese (target audience)
