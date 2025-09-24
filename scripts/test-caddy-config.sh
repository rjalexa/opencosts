#!/bin/bash

# OpenCosts Caddy Configuration Test Script
# Tests the system-wide Caddyfile configuration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OPENCOSTS_CONFIG="$PROJECT_DIR/docker/Caddyfile.system"

echo "🧪 Testing OpenCosts Caddy configuration..."

# Check if OpenCosts config exists
if [ ! -f "$OPENCOSTS_CONFIG" ]; then
    echo "❌ OpenCosts Caddy configuration not found at $OPENCOSTS_CONFIG"
    exit 1
fi

# Test Caddy configuration syntax
echo "✅ Testing Caddyfile syntax..."
if command -v caddy >/dev/null 2>&1; then
    if caddy validate --config "$OPENCOSTS_CONFIG"; then
        echo "✅ OpenCosts Caddyfile syntax is valid"
    else
        echo "❌ OpenCosts Caddyfile syntax validation failed!"
        exit 1
    fi
else
    echo "⚠️  Caddy not installed locally - syntax validation skipped"
fi

# Check if required ports are available
echo "🔍 Checking if required ports are available..."

check_port() {
    local port=$1
    local service=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use (needed for $service)"
        echo "   Current processes using port $port:"
        lsof -i :$port
    else
        echo "✅ Port $port is available for $service"
    fi
}

check_port 44401 "OpenCosts Frontend"
check_port 8000 "OpenCosts Backend"

# Check DNS resolution (if online)
echo "🌐 Testing DNS resolution..."
if command -v dig >/dev/null 2>&1; then
    if dig +short opencosts.isagog.com >/dev/null 2>&1; then
        echo "✅ DNS resolution for opencosts.isagog.com works"
        dig +short opencosts.isagog.com
    else
        echo "⚠️  DNS resolution for opencosts.isagog.com failed or not configured"
    fi
else
    echo "⚠️  dig command not available - DNS check skipped"
fi

# Check system Caddy status
echo "🔍 Checking system Caddy status..."
if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-active --quiet caddy 2>/dev/null; then
        echo "✅ System Caddy is running"
        systemctl status caddy --no-pager -l
    else
        echo "⚠️  System Caddy is not running"
        echo "   Start with: sudo systemctl start caddy"
    fi
else
    echo "⚠️  systemctl not available - Caddy status check skipped"
fi

# Test frontend configuration
echo "🎨 Testing frontend configuration..."
if [ -f "$PROJECT_DIR/frontend/vite.config.ts" ]; then
    if grep -q "port: 44401" "$PROJECT_DIR/frontend/vite.config.ts"; then
        echo "✅ Frontend configured for port 44401"
    else
        echo "❌ Frontend not configured for port 44401"
    fi
else
    echo "⚠️  Frontend vite.config.ts not found"
fi

# Test environment configuration
echo "🔧 Testing environment configuration..."
if [ -f "$PROJECT_DIR/.env.prod" ]; then
    if grep -q "FRONTEND_PORT=44401" "$PROJECT_DIR/.env.prod"; then
        echo "✅ Environment configured for frontend port 44401"
    else
        echo "❌ Environment not configured for frontend port 44401"
    fi
else
    echo "⚠️  .env.prod not found"
fi

echo ""
echo "🎉 Configuration test complete!"
echo ""
echo "📝 Next steps to deploy:"
echo "   1. Run: sudo ./scripts/add-to-system-caddy.sh"
echo "   2. Start backend: make run"
echo "   3. Start frontend: cd frontend && pnpm dev"
echo "   4. Visit: https://opencosts.isagog.com"
echo ""
echo "🔍 If issues occur:"
echo "   - Check logs: sudo journalctl -u caddy -f"
echo "   - Check OpenCosts logs: tail -f /var/log/caddy/opencosts.log"
echo "   - Validate config: caddy validate --config /etc/caddy/Caddyfile"