# Manual OpenCosts Caddy Deployment

If the automated script hangs or fails, you can manually add OpenCosts to your system Caddy:

## Step 1: Backup Existing Configuration
```bash
sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.backup.$(date +%Y%m%d_%H%M%S)
```

## Step 2: Add OpenCosts Configuration
Append the contents of `docker/Caddyfile.system` to your system Caddyfile:

```bash
# Add a separator comment
echo "" | sudo tee -a /etc/caddy/Caddyfile
echo "# OpenCosts Configuration - Added $(date)" | sudo tee -a /etc/caddy/Caddyfile

# Append the OpenCosts config (skip the global options and just add the site config)
sudo tee -a /etc/caddy/Caddyfile << 'EOF'

# Snippet for OpenCosts security headers (renamed to avoid conflicts)
(opencosts_security) {
        header {
                X-Frame-Options "SAMEORIGIN"
                X-XSS-Protection "1; mode=block"
                X-Content-Type-Options "nosniff"
                Referrer-Policy "no-referrer-when-downgrade"
                Strict-Transport-Security "max-age=31536000; includeSubDomains"
        }
}

# OpenCosts main site
opencosts.isagog.com, www.opencosts.isagog.com {
        import opencosts_security

        # API routes - proxy to backend container running on localhost:44400
        handle /api/* {
                # Strip /api prefix and proxy to backend container
                uri strip_prefix /api
                reverse_proxy localhost:44400 {
                        header_up Host {host}
                        header_up X-Real-IP {remote_host}
                }
        }

        # Health check endpoint
        handle /health {
                reverse_proxy localhost:44400
        }

        # CSV download endpoint
        handle /csv {
                reverse_proxy localhost:44400 {
                        header_down Content-Disposition "attachment; filename=openrouter_models.csv"
                }
        }

        # Static files and frontend - proxy to frontend container running on localhost:44401
        handle {
                reverse_proxy localhost:44401 {
                        header_up Host {host}
                        header_up X-Real-IP {remote_host}
                        
                        # Enable WebSocket support for development/HMR
                        header_up Connection {>Connection}
                        header_up Upgrade {>Upgrade}
                }
        }

        # Logging
        log {
                output file /var/log/caddy/opencosts.log {
                        roll_size 100mb
                        roll_keep 5
                        roll_keep_for 720h
                }
        }
}

# Optional: Redirect from alternative domains
costs.isagog.com {
        redir https://opencosts.isagog.com{uri}
}
EOF
```

## Step 3: Validate Configuration
```bash
sudo caddy validate --config /etc/caddy/Caddyfile
```

## Step 4: Restart Caddy (if reload hangs)
If `systemctl reload caddy` hangs, use restart instead:
```bash
sudo systemctl restart caddy
```

## Step 5: Check Status
```bash
sudo systemctl status caddy
sudo journalctl -u caddy -f
```

## Step 6: Create Log Directory
```bash
sudo mkdir -p /var/log/caddy
sudo chown caddy:caddy /var/log/caddy 2>/dev/null || sudo chown $USER:$USER /var/log/caddy
```

## Step 7: Start Your Container Services
```bash
# Start containers with Docker Compose
cd ~/code/opencosts
docker compose -f docker/docker-compose.prod.yml up -d --build

# Check container status
docker compose -f docker/docker-compose.prod.yml ps
```

## Troubleshooting

### If SSL/TLS Issues Occur:
1. Ensure DNS points to your server
2. Check firewall allows ports 80/443
3. Verify no other processes use port 80/443

### If Services Don't Start:
- Backend: Check port 44400 is available with `lsof -i :44400`
- Frontend: Check port 44401 is available with `lsof -i :44401`
- Containers: Check `docker compose -f docker/docker-compose.prod.yml logs`

### Check Logs:
```bash
# Caddy logs
sudo journalctl -u caddy -f

# OpenCosts specific logs
tail -f /var/log/caddy/opencosts.log

# Container logs
docker compose -f docker/docker-compose.prod.yml logs -f backend
docker compose -f docker/docker-compose.prod.yml logs -f frontend