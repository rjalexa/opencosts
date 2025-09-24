#!/bin/bash

# OpenCosts Caddy Setup Script
# Configures Caddy for production deployment

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔧 Setting up Caddy for OpenCosts..."

# Prompt for domain configuration
read -p "Enter your domain name (e.g., costs.yourdomain.com): " DOMAIN
read -p "Enter your admin email for Let's Encrypt: " ADMIN_EMAIL

if [ -z "$DOMAIN" ] || [ -z "$ADMIN_EMAIL" ]; then
    echo "❌ Domain and email are required"
    exit 1
fi

cd "$PROJECT_DIR"

# Update Caddyfile with actual domain
echo "📝 Updating Caddyfile with domain: $DOMAIN"
sed -i.bak "s/your-domain.com/$DOMAIN/g" docker/Caddyfile
sed -i.bak "s/admin@your-domain.com/$ADMIN_EMAIL/g" docker/Caddyfile

# Update environment file
if [ -f .env.prod ]; then
    echo "📝 Updating .env.prod with domain configuration"
    sed -i.bak "s/your-domain.com/$DOMAIN/g" .env.prod
    sed -i.bak "s/admin@your-domain.com/$ADMIN_EMAIL/g" .env.prod
fi

# Create log directories
echo "📁 Creating log directories..."
sudo mkdir -p /var/log/caddy
sudo chown -R $USER:$USER /var/log/caddy

# Test Caddyfile syntax
echo "✅ Testing Caddyfile syntax..."
if command -v caddy >/dev/null 2>&1; then
    caddy validate --config docker/Caddyfile
    echo "✅ Caddyfile syntax is valid"
else
    echo "⚠️  Caddy not installed locally - will validate in container"
fi

# Display configuration summary
echo ""
echo "🎉 Caddy configuration complete!"
echo "📋 Configuration Summary:"
echo "   Domain: https://$DOMAIN"
echo "   Admin Email: $ADMIN_EMAIL"
echo "   Let's Encrypt: Automatic"
echo "   Rate Limiting: Enabled"
echo "   Security Headers: Enabled"
echo ""
echo "🚀 To deploy:"
echo "   docker compose -f docker/docker-compose.prod.yml up -d --build"
echo ""
echo "🔍 To monitor:"
echo "   docker compose -f docker/docker-compose.prod.yml logs caddy -f"
echo "   curl localhost:2019/config/"
echo ""
echo "⚠️  Make sure your domain DNS points to this server!"