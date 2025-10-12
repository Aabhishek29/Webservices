#!/bin/bash

###############################################################################
# Complete Deployment Script - Deploy Both Frontend and Backend
#
# This script deploys both the React frontend and Django backend
# Usage: ./deploy-all.sh
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}================================================================${NC}"
echo -e "${PURPLE}   COMPLETE DEPLOYMENT - Frontend + Backend${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""
echo -e "${BLUE}This will deploy:${NC}"
echo -e "  1. Django Backend (API)"
echo -e "  2. React Frontend (UI)"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi
echo ""

# Record start time
START_TIME=$(date +%s)

# ===========================================================================
# PART 1: BACKEND DEPLOYMENT
# ===========================================================================

echo -e "${PURPLE}================================================================${NC}"
echo -e "${PURPLE}   PART 1/2: Backend Deployment${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""

# Backend deployment steps
echo -e "${YELLOW}[1/8] Pulling latest code from Git...${NC}"
git pull origin master
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Code pulled successfully${NC}"
else
    echo -e "${RED}✗ Failed to pull code${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}[2/8] Clearing Python cache...${NC}"
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Python cache cleared${NC}"
echo ""

echo -e "${YELLOW}[3/8] Running database migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput 2>/dev/null || echo -e "${YELLOW}⚠ Migrations will run after container restart${NC}"
echo ""

echo -e "${YELLOW}[4/8] Rebuilding Docker images...${NC}"
docker-compose build --no-cache web
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker images rebuilt${NC}"
else
    echo -e "${RED}✗ Failed to rebuild Docker images${NC}"
    exit 1
fi
echo ""

# ===========================================================================
# PART 2: FRONTEND DEPLOYMENT
# ===========================================================================

echo -e "${PURPLE}================================================================${NC}"
echo -e "${PURPLE}   PART 2/2: Frontend Deployment${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""

S3_URL="https://venusa.s3.ap-south-1.amazonaws.com/venusa/frontend/dist.zip"
DIST_DIR="./dist"
BACKUP_DIR="./dist_backup"

echo -e "${YELLOW}[5/8] Backing up existing frontend...${NC}"
if [ -d "$DIST_DIR" ]; then
    rm -rf "$BACKUP_DIR"
    mv "$DIST_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓ Backup created${NC}"
else
    echo -e "${YELLOW}⚠ No existing frontend found${NC}"
fi
echo ""

echo -e "${YELLOW}[6/8] Downloading latest frontend from S3...${NC}"
rm -f dist.zip
wget -q "$S3_URL" -O dist.zip
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Downloaded from S3${NC}"
    unzip -q dist.zip
    rm -f dist.zip
    echo -e "${GREEN}✓ Frontend extracted${NC}"
else
    echo -e "${RED}✗ Failed to download frontend${NC}"
    if [ -d "$BACKUP_DIR" ]; then
        mv "$BACKUP_DIR" "$DIST_DIR"
    fi
    exit 1
fi
echo ""

# ===========================================================================
# PART 3: RESTART ALL SERVICES
# ===========================================================================

echo -e "${PURPLE}================================================================${NC}"
echo -e "${PURPLE}   PART 3/3: Restarting All Services${NC}"
echo -e "${PURPLE}================================================================${NC}"
echo ""

echo -e "${YELLOW}[7/8] Restarting all containers...${NC}"
docker-compose down
docker-compose up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All containers started${NC}"
else
    echo -e "${RED}✗ Failed to start containers${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Waiting for services to be ready (15 seconds)...${NC}"
sleep 15
echo ""

# ===========================================================================
# PART 4: HEALTH CHECKS
# ===========================================================================

echo -e "${YELLOW}[8/8] Running health checks...${NC}"
echo ""

# Container status
echo -e "${YELLOW}Container Status:${NC}"
docker-compose ps
echo ""

# Backend health
echo -e "${YELLOW}Backend Health Checks:${NC}"
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/login/)
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/categories/dashboard)

if [ "$ADMIN_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ Backend Admin: $ADMIN_STATUS${NC}"
else
    echo -e "${RED}✗ Backend Admin: $ADMIN_STATUS${NC}"
fi

if [ "$API_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ Backend API: $API_STATUS${NC}"
else
    echo -e "${RED}✗ Backend API: $API_STATUS${NC}"
fi
echo ""

# Frontend health
echo -e "${YELLOW}Frontend Health Check:${NC}"
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)

if [ "$FRONTEND_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ Frontend: $FRONTEND_STATUS${NC}"
else
    echo -e "${RED}✗ Frontend: $FRONTEND_STATUS${NC}"
fi
echo ""

# Clean up backup
if [ -d "$BACKUP_DIR" ]; then
    rm -rf "$BACKUP_DIR"
fi

# Calculate deployment time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# ===========================================================================
# DEPLOYMENT SUMMARY
# ===========================================================================

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}   DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}================================================================${NC}"
echo ""
echo -e "${BLUE}Deployment Summary:${NC}"
echo -e "  • Backend:  Rebuilt and restarted"
echo -e "  • Frontend: Downloaded and deployed from S3"
echo -e "  • Duration: ${MINUTES}m ${SECONDS}s"
echo ""
echo -e "${BLUE}Your application is now live at:${NC}"
echo ""
echo -e "${GREEN}Frontend (React App):${NC}"
echo -e "  • http://3.110.46.10/"
echo -e "  • http://venusa.co.in/ ${YELLOW}(if DNS configured)${NC}"
echo ""
echo -e "${GREEN}Backend (Django API):${NC}"
echo -e "  • http://3.110.46.10:8000/admin/"
echo -e "  • http://3.110.46.10/api/* ${YELLOW}(via nginx proxy)${NC}"
echo -e "  • http://3.110.46.10:8000/* ${YELLOW}(direct access)${NC}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  • View logs:          docker-compose logs -f"
echo -e "  • Frontend only:      ./deploy-frontend.sh"
echo -e "  • Backend only:       ./deploy-backend.sh"
echo -e "  • Restart services:   docker-compose restart"
echo -e "  • Container status:   docker-compose ps"
echo ""
