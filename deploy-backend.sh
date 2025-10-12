#!/bin/bash

###############################################################################
# Backend Deployment Script - Deploy Django Application
#
# This script deploys the Django backend application
# Usage: ./deploy-backend.sh
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Backend Deployment - Django API${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running in project directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found. Are you in the project directory?${NC}"
    exit 1
fi

# Step 1: Pull latest code
echo -e "${YELLOW}[1/7] Pulling latest code from Git...${NC}"
git pull origin master
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Code pulled successfully${NC}"
else
    echo -e "${RED}✗ Failed to pull code${NC}"
    exit 1
fi
echo ""

# Step 2: Clear Python cache
echo -e "${YELLOW}[2/7] Clearing Python cache...${NC}"
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Python cache cleared${NC}"
echo ""

# Step 3: Check Docker status
echo -e "${YELLOW}[3/7] Checking Docker containers...${NC}"
docker-compose ps
echo ""

# Step 4: Run migrations (if needed)
echo -e "${YELLOW}[4/7] Running database migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations completed${NC}"
else
    echo -e "${YELLOW}⚠ Migrations had issues (may be expected)${NC}"
fi
echo ""

# Step 5: Collect static files
echo -e "${YELLOW}[5/7] Collecting static files...${NC}"
docker-compose exec -T web python manage.py collectstatic --noinput
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Static files collected${NC}"
else
    echo -e "${YELLOW}⚠ Static files collection had issues (may be expected)${NC}"
fi
echo ""

# Step 6: Rebuild Docker image
echo -e "${YELLOW}[6/7] Rebuilding Docker image...${NC}"
docker-compose build --no-cache web
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image rebuilt successfully${NC}"
else
    echo -e "${RED}✗ Failed to rebuild Docker image${NC}"
    exit 1
fi
echo ""

# Step 7: Restart containers
echo -e "${YELLOW}[7/7] Restarting containers...${NC}"
docker-compose down
docker-compose up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Containers restarted${NC}"
else
    echo -e "${RED}✗ Failed to restart containers${NC}"
    exit 1
fi
echo ""

# Wait for containers to be healthy
echo -e "${YELLOW}Waiting for containers to be healthy (15 seconds)...${NC}"
sleep 15
echo ""

# Health checks
echo -e "${YELLOW}Running health checks...${NC}"
echo ""

# Check container status
echo -e "${YELLOW}Container Status:${NC}"
docker-compose ps
echo ""

# Test API endpoints
echo -e "${YELLOW}API Health Checks:${NC}"
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/login/)
DASHBOARD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/categories/dashboard)

if [ "$ADMIN_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ Admin page: $ADMIN_STATUS${NC}"
else
    echo -e "${RED}✗ Admin page: $ADMIN_STATUS${NC}"
fi

if [ "$DASHBOARD_STATUS" == "200" ]; then
    echo -e "${GREEN}✓ Dashboard API: $DASHBOARD_STATUS${NC}"
else
    echo -e "${RED}✗ Dashboard API: $DASHBOARD_STATUS${NC}"
fi
echo ""

# Show recent logs
echo -e "${YELLOW}Recent application logs:${NC}"
docker-compose logs --tail=20 web
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Backend Deployment Completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Backend API is accessible at:${NC}"
echo -e "  • http://3.110.46.10:8000/"
echo -e "  • http://3.110.46.10/api/*"
echo -e "  • http://3.110.46.10/admin/"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  • View logs:        docker-compose logs -f web"
echo -e "  • Container status: docker-compose ps"
echo -e "  • Restart service:  docker-compose restart web"
echo ""
