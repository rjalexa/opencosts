#!/bin/bash

# OpenCosts Daily Data Scraping Script
# This script automates the daily data collection for OpenRouter models

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="/var/log/opencosts"
LOG_FILE="$LOG_DIR/daily-scrape.log"
LOCK_FILE="/tmp/opencosts-scrape.lock"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-admin@your-domain.com}"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to send notification
send_notification() {
    local subject="$1"
    local message="$2"
    
    # Send email notification (requires mail command)
    if command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "$subject" "$NOTIFICATION_EMAIL"
    fi
    
    # Log notification
    log "NOTIFICATION: $subject - $message"
}

# Function to cleanup on exit
cleanup() {
    rm -f "$LOCK_FILE"
}

# Set trap for cleanup
trap cleanup EXIT

# Check if another instance is running
if [ -f "$LOCK_FILE" ]; then
    log "ERROR: Another scraping process is already running (lock file exists)"
    exit 1
fi

# Create lock file
echo $$ > "$LOCK_FILE"

log "Starting daily data scraping process"

# Change to project directory
cd "$PROJECT_DIR"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    log "ERROR: Docker is not running"
    send_notification "OpenCosts Scrape Failed" "Docker is not running on the server"
    exit 1
fi

# Run the scraper using Docker Compose
log "Running data scraper..."
if docker compose -f docker/docker-compose.prod.yml run --rm scraper python src/main.py; then
    log "Data scraping completed successfully"
    
    # Check if CSV file was generated
    CSV_FILE="frontend/public/openrouter_models_providers.csv"
    if [ -f "$CSV_FILE" ]; then
        LINES=$(wc -l < "$CSV_FILE")
        log "Generated CSV with $LINES lines"
        
        # Create backup
        BACKUP_DIR="data/backups"
        mkdir -p "$BACKUP_DIR"
        BACKUP_FILE="$BACKUP_DIR/openrouter_models_$(date +%Y%m%d_%H%M%S).csv"
        cp "$CSV_FILE" "$BACKUP_FILE"
        log "Backup created: $BACKUP_FILE"
        
        # Clean old backups (keep last 30 days)
        find "$BACKUP_DIR" -name "openrouter_models_*.csv" -mtime +30 -delete
        log "Old backups cleaned up"
        
        send_notification "OpenCosts Scrape Success" "Data scraping completed successfully. Generated $LINES rows of data."
    else
        log "WARNING: CSV file was not generated"
        send_notification "OpenCosts Scrape Warning" "Scraping process completed but CSV file was not found"
    fi
else
    log "ERROR: Data scraping failed"
    send_notification "OpenCosts Scrape Failed" "Data scraping process failed. Check logs for details."
    exit 1
fi

log "Daily scraping process completed"