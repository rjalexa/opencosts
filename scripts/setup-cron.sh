#!/bin/bash

# OpenCosts Cron Job Setup Script
# Sets up automated daily data scraping at 6:00 AM

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAILY_SCRAPE_SCRIPT="$SCRIPT_DIR/daily-scrape.sh"

# Make the daily scrape script executable
chmod +x "$DAILY_SCRAPE_SCRIPT"

echo "Setting up OpenCosts automated data scraping..."

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    echo "Setting up system-wide cron job..."
    
    # Create cron job file
    cat > /etc/cron.d/opencosts-scrape << EOF
# OpenCosts Daily Data Scraping
# Runs at 6:00 AM every day
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
NOTIFICATION_EMAIL=admin@your-domain.com

0 6 * * * root $DAILY_SCRAPE_SCRIPT >/dev/null 2>&1
EOF

    echo "System-wide cron job created in /etc/cron.d/opencosts-scrape"
    
else
    echo "Setting up user cron job..."
    
    # Add to user's crontab
    (crontab -l 2>/dev/null || true; echo "# OpenCosts Daily Data Scraping at 6:00 AM") | crontab -
    (crontab -l 2>/dev/null | grep -v "$DAILY_SCRAPE_SCRIPT" || true; echo "0 6 * * * $DAILY_SCRAPE_SCRIPT >/dev/null 2>&1") | crontab -
    
    echo "User cron job added to crontab"
fi

# Verify cron service is running
if systemctl is-active --quiet cron || systemctl is-active --quiet crond; then
    echo "✅ Cron service is running"
else
    echo "⚠️  Warning: Cron service may not be running. Start it with:"
    echo "   sudo systemctl start cron    # On Debian/Ubuntu"
    echo "   sudo systemctl start crond   # On RedHat/CentOS"
fi

# Show current cron jobs
echo ""
echo "Current cron configuration:"
if [ "$EUID" -eq 0 ]; then
    cat /etc/cron.d/opencosts-scrape
else
    crontab -l | grep -A1 -B1 "OpenCosts" || echo "No OpenCosts cron jobs found"
fi

echo ""
echo "✅ Automated data scraping setup complete!"
echo "📅 Data will be scraped daily at 6:00 AM"
echo "📧 Notifications will be sent to: ${NOTIFICATION_EMAIL:-admin@your-domain.com}"
echo ""
echo "To test the scraping script manually:"
echo "   $DAILY_SCRAPE_SCRIPT"
echo ""
echo "To remove the cron job:"
if [ "$EUID" -eq 0 ]; then
    echo "   sudo rm /etc/cron.d/opencosts-scrape"
else
    echo "   crontab -e  # Remove the OpenCosts line manually"
fi