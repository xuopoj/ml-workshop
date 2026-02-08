#!/bin/bash
set -e

# Initialize devpi if not already done
if [ ! -f /data/devpi/.nodeinfo ]; then
    echo "Initializing devpi server..."
    devpi-init --serverdir /data/devpi
fi

# Ensure apt-cacher-ng directories exist
mkdir -p /data/apt-cacher-ng /var/log/apt-cacher-ng
chown -R apt-cacher-ng:apt-cacher-ng /data/apt-cacher-ng /var/log/apt-cacher-ng

echo "========================================"
echo "ML Workshop Proxy/Cache Server"
echo "========================================"
echo "Whistle Proxy:    http://0.0.0.0:8899"
echo "Whistle UI:       http://0.0.0.0:8900 (auth enabled)"
echo "devpi (pip):      http://0.0.0.0:3141"
echo "apt-cacher-ng:    http://0.0.0.0:3142"
echo ""
echo "CA Certificate:   /data/whistle/certs/rootCA.crt"
echo "========================================"

# Start supervisor (manages all services)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
