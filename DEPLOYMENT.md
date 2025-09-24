# OpenCosts Production Deployment Guide

This guide covers deploying OpenCosts to a production server with automated data scraping.

## 🚀 Quick Production Setup

### Prerequisites

- **Server**: Ubuntu 20.04+ or CentOS 8+ with root access
- **Resources**: 2GB RAM, 10GB disk space, stable internet
- **Domain**: DNS pointing to your server (optional but recommended)
- **Dependencies**: Docker Engine 20.10+, Docker Compose v2

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reboot to apply group changes
sudo reboot
```

### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/rjalexa/opencosts.git
cd opencosts

# Configure environment
cp .env.prod .env.prod.local
nano .env.prod.local

# Edit these key settings:
# - VITE_API_URL=https://your-domain.com/api
# - CORS_ORIGINS=https://your-domain.com
# - NOTIFICATION_EMAIL=admin@your-domain.com

# Setup Caddy configuration (automated script)
chmod +x scripts/setup-caddy.sh
./scripts/setup-caddy.sh

# OR manually update Caddyfile:
# sed -i 's/your-domain.com/actual-domain.com/g' docker/Caddyfile
# sed -i 's/admin@your-domain.com/admin@actual-domain.com/g' docker/Caddyfile

# Start production services
docker compose -f docker/docker-compose.prod.yml up -d --build

# Verify deployment
curl -f http://localhost/health
```

### 3. Setup Automated Data Scraping

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Setup daily cron job (runs at 6:00 AM)
sudo ./scripts/setup-cron.sh

# Test manual scraping
./scripts/daily-scrape.sh
```

## 🔧 Configuration Details

### Environment Variables

Edit [`.env.prod.local`](.env.prod.local) with your specific settings:

```bash
# Your domain configuration
VITE_API_URL=https://your-domain.com/api
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Notification settings
NOTIFICATION_EMAIL=admin@your-domain.com

# Caddy will automatically handle SSL certificates via Let's Encrypt
# No manual SSL configuration needed

# Performance tuning
MAX_WORKERS=4
REQUEST_TIMEOUT=30
```

### Caddy Configuration

The [`docker/Caddyfile`](docker/Caddyfile) provides:
- Automatic HTTPS with Let's Encrypt certificates
- Reverse proxy to backend/frontend
- Security headers (HSTS, XSS protection, etc.)
- WebSocket support for development
- Automatic HTTP to HTTPS redirects
- Structured logging with log rotation

Update domain references:
```bash
sed -i 's/your-domain.com/yourdomain.com/g' docker/Caddyfile
sed -i 's/admin@your-domain.com/admin@yourdomain.com/g' docker/Caddyfile
```

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check service status
docker compose -f docker/docker-compose.prod.yml ps

# View logs
docker compose -f docker/docker-compose.prod.yml logs -f backend
docker compose -f docker/docker-compose.prod.yml logs -f frontend

# Test endpoints
curl https://your-domain.com/health
curl https://your-domain.com/api/models
```

### Log Management

Application logs are stored in:
- **Application**: `/var/log/opencosts/`
- **Caddy**: `/var/log/caddy/`
- **Docker**: `docker compose logs`

```bash
# View scraping logs
tail -f /var/log/opencosts/daily-scrape.log

# View Caddy access logs
tail -f /var/log/caddy/opencosts.log

# Rotate logs (setup logrotate)
sudo cat > /etc/logrotate.d/opencosts << EOF
/var/log/opencosts/*.log /var/log/caddy/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
```

### Data Backup

Automated backups are created daily in [`data/backups/`](data/backups/):

```bash
# Manual backup
cp frontend/public/openrouter_models_providers.csv \
   data/backups/manual_backup_$(date +%Y%m%d_%H%M%S).csv

# List backups
ls -la data/backups/

# Restore from backup
cp data/backups/openrouter_models_20240124_060001.csv \
   frontend/public/openrouter_models_providers.csv
```

## 🔄 Updates & Maintenance

### Application Updates

```bash
# Update application
cd opencosts
git pull origin main

# Rebuild and restart services
docker compose -f docker/docker-compose.prod.yml down
docker compose -f docker/docker-compose.prod.yml up -d --build

# Verify update
curl https://your-domain.com/health
```

### SSL Certificate Management

Caddy automatically handles SSL certificates:
```bash
# Certificates are automatically renewed by Caddy
# No manual intervention required

# View certificate status via Caddy admin API
curl localhost:2019/config/apps/tls/certificates

# Force certificate refresh (if needed)
docker compose -f docker/docker-compose.prod.yml restart caddy
```

### Database Migration

When moving to a new server:
```bash
# Export data
tar -czf opencosts-data-$(date +%Y%m%d).tar.gz data/ frontend/public/*.csv

# On new server, extract
tar -xzf opencosts-data-YYYYMMDD.tar.gz

# Deploy normally
docker compose -f docker/docker-compose.prod.yml up -d --build
```

## 🔍 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check Docker status
sudo systemctl status docker

# Check ports
sudo netstat -tlnp | grep -E ':(80|443|8000|5173)'

# Check logs
docker compose -f docker/docker-compose.prod.yml logs
```

**Data scraping fails:**
```bash
# Check scraper logs
tail -f /var/log/opencosts/daily-scrape.log

# Test manual scraping
docker compose -f docker/docker-compose.prod.yml run --rm scraper python src/main.py

# Check OpenRouter API access
curl -s https://openrouter.ai/api/v1/models | jq '.data | length'
```

**Frontend not loading:**
```bash
# Check backend connectivity
curl http://localhost:8000/health

# Verify CORS settings in .env.prod.local
grep CORS .env.prod.local

# Check Caddy config
docker compose -f docker/docker-compose.prod.yml exec caddy caddy validate --config /etc/caddy/Caddyfile

# View Caddy admin interface
curl localhost:2019/config/
```

### Performance Optimization

**Increase concurrency:**
```bash
# In .env.prod.local
MAX_WORKERS=8

# Restart backend
docker compose -f docker/docker-compose.prod.yml restart backend
```

**Enable caching:**
```bash
# Add Redis for API caching
# Add to docker-compose.prod.yml:
redis:
  image: redis:alpine
  restart: unless-stopped
```

## 📞 Support

- **Logs**: Check [`/var/log/opencosts/`](/var/log/opencosts/) for application logs
- **Health**: Monitor [`https://your-domain.com/health`](https://your-domain.com/health)
- **Email**: Automated notifications sent to configured email
- **GitHub**: [Issues](https://github.com/rjalexa/opencosts/issues) for bug reports

## 🔐 Security Checklist

- [ ] Domain DNS properly configured for Caddy auto-SSL
- [ ] Firewall configured (ports 80, 443, 2019 for Caddy admin)
- [ ] Regular security updates scheduled
- [ ] Strong passwords and SSH key authentication
- [ ] Security headers configured in Caddyfile
- [ ] Log monitoring setup
- [ ] Backup procedures verified
- [ ] CORS origins restricted to your domain
- [ ] Caddy admin interface secured (localhost only)

## 📈 Scaling Considerations

For high-traffic deployments:

1. **Load Balancing**: Multiple backend instances
2. **Database**: Move from CSV to PostgreSQL
3. **Caching**: Redis for API responses
4. **CDN**: CloudFlare for static assets
5. **Monitoring**: Prometheus + Grafana
6. **Container Orchestration**: Kubernetes deployment

---

**Need help?** Check the main [README.md](README.md) or open an [issue](https://github.com/rjalexa/opencosts/issues).