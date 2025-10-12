#!/bin/bash

###############################################################################
# Frontend Deployment Script - Deploy React App from S3
#
# This script downloads the latest React build from S3 and deploys it
# Usage: ./deploy-frontend.sh
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
S3_URL="https://venusa.s3.ap-south-1.amazonaws.com/venusa/frontend/dist.zip"
PROJECT_DIR="/home/ubuntu/Webservices"
DIST_DIR="${PROJECT_DIR}/dist"
BACKUP_DIR="${PROJECT_DIR}/dist_backup"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Frontend Deployment - React App${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Backup existing frontend (if exists)
echo -e "${YELLOW}[1/6] Backing up existing frontend...${NC}"
if [ -d "$DIST_DIR" ]; then
    rm -rf "$BACKUP_DIR"
    mv "$DIST_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓ Backup created at $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}⚠ No existing frontend found, skipping backup${NC}"
fi
echo ""

# Step 2: Download latest build from S3
echo -e "${YELLOW}[2/6] Downloading latest build from S3...${NC}"
cd "$PROJECT_DIR"
rm -f dist.zip
wget -q "$S3_URL" -O dist.zip
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Downloaded dist.zip from S3${NC}"
else
    echo -e "${RED}✗ Failed to download from S3${NC}"
    # Restore backup if download fails
    if [ -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}↻ Restoring backup...${NC}"
        mv "$BACKUP_DIR" "$DIST_DIR"
    fi
    exit 1
fi
echo ""

# Step 3: Extract build
echo -e "${YELLOW}[3/6] Extracting build files...${NC}"
unzip -q dist.zip
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build extracted successfully${NC}"
    rm -f dist.zip
else
    echo -e "${RED}✗ Failed to extract build${NC}"
    # Restore backup if extraction fails
    if [ -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}↻ Restoring backup...${NC}"
        mv "$BACKUP_DIR" "$DIST_DIR"
    fi
    exit 1
fi
echo ""

# Step 4: Verify build
echo -e "${YELLOW}[4/6] Verifying build files...${NC}"
if [ -f "$DIST_DIR/index.html" ]; then
    echo -e "${GREEN}✓ index.html found${NC}"
    echo -e "${GREEN}✓ Build verification successful${NC}"
else
    echo -e "${RED}✗ index.html not found - invalid build${NC}"
    # Restore backup if build is invalid
    if [ -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}↻ Restoring backup...${NC}"
        rm -rf "$DIST_DIR"
        mv "$BACKUP_DIR" "$DIST_DIR"
    fi
    exit 1
fi
echo ""

# Step 5: Set permissions
echo -e "${YELLOW}[5/6] Setting permissions...${NC}"
chmod -R 755 "$DIST_DIR"
echo -e "${GREEN}✓ Permissions set${NC}"
echo ""

# Step 6: Restart nginx container
echo -e "${YELLOW}[6/6] Restarting nginx container...${NC}"
cd "$PROJECT_DIR"
docker-compose restart nginx
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Nginx restarted successfully${NC}"
else
    echo -e "${RED}✗ Failed to restart nginx${NC}"
    exit 1
fi
echo ""

# Wait for nginx to be ready
echo -e "${YELLOW}Waiting for nginx to be ready (5 seconds)...${NC}"
sleep 5
echo ""

# Health check
echo -e "${YELLOW}Running health check...${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$HEALTH_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ Frontend is responding: $HEALTH_STATUS${NC}"
else
    echo -e "${RED}✗ Frontend health check failed: $HEALTH_STATUS${NC}"
fi
echo ""

# Clean up old backup
if [ -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Cleaning up old backup...${NC}"
    rm -rf "$BACKUP_DIR"
    echo -e "${GREEN}✓ Backup cleaned up${NC}"
fi
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Frontend Deployment Completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Frontend is now live at:${NC}"
echo -e "${BLUE}  • http://3.110.46.10/${NC}"
echo -e "${BLUE}  • http://venusa.co.in/ (if DNS configured)${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Backend API is accessible at:"
echo -e "  • http://3.110.46.10/api/*"
echo -e "  • http://3.110.46.10:8000/*"
echo ""
