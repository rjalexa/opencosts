#!/bin/bash

# OpenCosts System Caddy Integration Script
# Adds OpenCosts configuration to existing system-wide Caddy

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SYSTEM_CADDY_CONFIG="${SYSTEM_CADDY_CONFIG:-/etc/caddy/Caddyfile}"
OPENCOSTS_CONFIG="$PROJECT_DIR/docker/Caddyfile.system"

echo "🔧 Adding OpenCosts to system-wide Caddy..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script needs to be run with sudo to modify system Caddy configuration"
    echo "Usage: sudo $0"
    exit 1
fi

# Check if system Caddy config exists
if [ ! -f "$SYSTEM_CADDY_CONFIG" ]; then
    echo "❌ System Caddy configuration not found at $SYSTEM_CADDY_CONFIG"
    echo "Please specify the correct path: SYSTEM_CADDY_CONFIG=/path/to/Caddyfile sudo $0"
    exit 1
fi

# Check if OpenCosts config exists
if [ ! -f "$OPENCOSTS_CONFIG" ]; then
    echo "❌ OpenCosts Caddy configuration not found at $OPENCOSTS_CONFIG"
    exit 1
fi

# Backup existing Caddy config
BACKUP_FILE="${SYSTEM_CADDY_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
echo "📋 Creating backup of existing Caddyfile: $BACKUP_FILE"
cp "$SYSTEM_CADDY_CONFIG" "$BACKUP_FILE"

# Check if OpenCosts config already exists in system config
if grep -q "opencosts.isagog.com" "$SYSTEM_CADDY_CONFIG"; then
    echo "⚠️  OpenCosts configuration already exists in system Caddyfile"
    echo "Please remove existing opencosts.isagog.com configuration first or run with --force"
    echo "Backup created at: $BACKUP_FILE"
    exit 1
fi

# Add OpenCosts configuration to system Caddy
echo "📝 Adding OpenCosts configuration to system Caddyfile..."
echo "" >> "$SYSTEM_CADDY_CONFIG"
echo "# OpenCosts Configuration - Added $(date)" >> "$SYSTEM_CADDY_CONFIG"
cat "$OPENCOSTS_CONFIG" >> "$SYSTEM_CADDY_CONFIG"

# Validate Caddy configuration
echo "✅ Validating Caddy configuration..."
if caddy validate --config "$SYSTEM_CADDY_CONFIG"; then
    echo "✅ Caddy configuration is valid"
else
    echo "❌ Caddy configuration validation failed!"
    echo "Restoring backup..."
    cp "$BACKUP_FILE" "$SYSTEM_CADDY_CONFIG"
    exit 1
fi

# Reload Caddy
echo "🔄 Reloading Caddy configuration..."
if systemctl is-active --quiet caddy; then
    systemctl reload caddy
    echo "✅ Caddy configuration reloaded successfully"
else
    echo "⚠️  Caddy service is not running. Starting Caddy..."
    systemctl start caddy
    echo "✅ Caddy service started"
fi

# Create log directory
echo "📁 Creating log directories..."
mkdir -p /var/log/caddy
chown caddy:caddy /var/log/caddy 2>/dev/null || chown $SUDO_USER:$SUDO_USER /var/log/caddy

echo ""
echo "🎉 OpenCosts successfully added to system Caddy!"
echo "📋 Configuration Summary:"
echo "   Domain: https://opencosts.isagog.com"
echo "   Frontend: localhost:44401"
echo "   Backend: localhost:8000"
echo "   Logs: /var/log/caddy/opencosts.log"
echo ""
echo "📝 Next steps:"
echo "   1. Start your OpenCosts backend on port 8000"
echo "   2. Start your OpenCosts frontend on port 44401"
echo "   3. Ensure DNS points opencosts.isagog.com to this server"
echo ""
echo "🚀 To start OpenCosts frontend:"
echo "   cd $PROJECT_DIR/frontend && pnpm dev"
echo ""
echo "🚀 To start OpenCosts backend:"
echo "   cd $PROJECT_DIR && make run"
echo ""
echo "🔍 To monitor Caddy:"
echo "   sudo journalctl -u caddy -f"
echo "   tail -f /var/log/caddy/opencosts.log"
echo ""
echo "📋 Backup created at: $BACKUP_FILE"