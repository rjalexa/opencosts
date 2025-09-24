# OpenCosts Production Deployment with Containers

This guide covers deploying OpenCosts using Docker containers with system-wide Caddy.

## Architecture

- **Backend Container**: Runs on `localhost:44400`
- **Frontend Container**: Runs on `localhost:44401` 
- **System Caddy**: Routes `opencosts.isagog.com` to containers
- **External Access**: `https://opencosts.isagog.com`

## Prerequisites

- Docker and Docker Compose installed
- System-wide Caddy already running
- DNS pointing `opencosts.isagog.com` to your server
- Ports 44400 and 44401 available

## Deployment Steps

### 1. Add OpenCosts to System Caddy

```bash
# Run the automated script
sudo ./scripts/add-to-system-caddy.sh

# Or follow manual steps in scripts/manual-caddy-deployment.md if needed
```

This adds the OpenCosts configuration to your existing system Caddy, routing:
- `https://opencosts.isagog.com/api/*` → `localhost:44400` (backend container)
- `https://opencosts.isagog.com/*` → `localhost:44401` (frontend container)

### 2. Configure Environment

Ensure `.env.prod` has the correct settings:
```bash
BACKEND_PORT=44400
FRONTEND_PORT=44401
VITE_API_URL=https://opencosts.isagog.com/api
```

### 3. Deploy Containers

```bash
# Build and start containers
docker compose -f docker/docker-compose.prod.yml up -d --build

# Check status
docker compose -f docker/docker-compose.prod.yml ps

# View logs
docker compose -f docker/docker-compose.prod.yml logs -f
```

### 4. Verify Deployment

```bash
# Check containers are running
docker ps | grep opencosts

# Test backend health
curl http://localhost:44400/health

# Test frontend
curl http://localhost:44401

# Test external access
curl https://opencosts.isagog.com/health
curl https://opencosts.isagog.com/
```

## Container Services

### Backend Container (`opencosts_prod-backend-1`)
- **Port**: `44400:44400`
- **Health Check**: `http://localhost:44400/health`
- **Command**: `uvicorn src.api:app --host 0.0.0.0 --port 44400 --workers 2`
- **Volumes**: Data, logs, frontend public assets

### Frontend Container (`opencosts_prod-frontend-1`)
- **Port**: `44401:44401`
- **Health Check**: `http://localhost:44401`
- **Command**: `serve -s dist -l 44401`
- **Built**: Production-optimized React build

### Scraper Container (`opencosts_prod-scraper-1`)
- **Profile**: `scraper` (manual start only)
- **Usage**: Data collection and updates
- **Command**: `python src/main.py`

## Management Commands

### Start/Stop Services
```bash
# Start all services
docker compose -f docker/docker-compose.prod.yml up -d

# Stop all services
docker compose -f docker/docker-compose.prod.yml down

# Restart specific service
docker compose -f docker/docker-compose.prod.yml restart backend
docker compose -f docker/docker-compose.prod.yml restart frontend
```

### View Logs
```bash
# All services
docker compose -f docker/docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker/docker-compose.prod.yml logs -f backend
docker compose -f docker/docker-compose.prod.yml logs -f frontend

# Caddy logs (system service)
sudo journalctl -u caddy -f
tail -f /var/log/caddy/opencosts.log
```

### Run Scraper
```bash
# Run data scraper manually
docker compose -f docker/docker-compose.prod.yml run --rm scraper

# Or via profile
docker compose -f docker/docker-compose.prod.yml --profile scraper up scraper
```

### Updates and Rebuilds
```bash
# Pull latest code and rebuild
git pull
docker compose -f docker/docker-compose.prod.yml down
docker compose -f docker/docker-compose.prod.yml up -d --build

# Rebuild specific service
docker compose -f docker/docker-compose.prod.yml up -d --build frontend
```

## Troubleshooting

### Container Issues
```bash
# Check container status
docker compose -f docker/docker-compose.prod.yml ps

# Inspect container
docker compose -f docker/docker-compose.prod.yml logs backend
docker compose -f docker/docker-compose.prod.yml exec backend bash

# Restart unhealthy containers
docker compose -f docker/docker-compose.prod.yml restart
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :44400
lsof -i :44401

# If ports are in use, stop conflicting services
sudo systemctl stop <service-name>
```

### Caddy Issues
```bash
# Check Caddy configuration
sudo caddy validate --config /etc/caddy/Caddyfile

# Reload Caddy
sudo systemctl reload caddy

# Check Caddy status
sudo systemctl status caddy
```

### SSL/TLS Issues
```bash
# Check certificate status
curl -I https://opencosts.isagog.com

# Force certificate renewal (if needed)
sudo systemctl restart caddy
```

## Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:44400/health

# Frontend availability  
curl http://localhost:44401

# External access
curl https://opencosts.isagog.com/health
```

### Resource Usage
```bash
# Container resource usage
docker stats

# Disk usage
docker system df
```

### Log Monitoring
```bash
# Real-time logs
docker compose -f docker/docker-compose.prod.yml logs -f

# Caddy access logs
tail -f /var/log/caddy/opencosts.log

# System logs
sudo journalctl -u caddy -f
```

## Backup and Maintenance

### Data Backup
```bash
# Backup data directory
tar -czf opencosts-data-$(date +%Y%m%d).tar.gz data/

# Backup container volumes
docker run --rm -v opencosts_prod_log_data:/data -v $(pwd):/backup alpine tar czf /backup/logs-$(date +%Y%m%d).tar.gz /data
```

### Container Cleanup
```bash
# Remove unused containers and images
docker system prune -f

# Remove old images after updates
docker image prune -f
```

### Updates
```bash
# Update OpenCosts
git pull
docker compose -f docker/docker-compose.prod.yml down
docker compose -f docker/docker-compose.prod.yml up -d --build

# Update system Caddy (if needed)
sudo apt update && sudo apt upgrade caddy
sudo systemctl restart caddy
```

## Configuration Files

- **System Caddy**: `/etc/caddy/Caddyfile` (contains OpenCosts config)
- **Environment**: `.env.prod`
- **Docker Compose**: `docker/docker-compose.prod.yml`
- **OpenCosts Caddy Config**: `docker/Caddyfile.system` (for reference)

## Network Architecture

```
Internet → System Caddy (80/443) → Docker Containers
                ↓
        opencosts.isagog.com
                ↓
        localhost:44400 (backend)
        localhost:44401 (frontend)