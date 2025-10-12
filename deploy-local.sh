#!/bin/bash

###############################################################################
# Server-Side Deployment Script for Django Application
#
# Run this script directly on the server (not from local machine)
# Usage: ./deploy-local.sh
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Django Application Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running on server
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found. Are you in the project directory?${NC}"
    exit 1
fi

# Step 1: Pull latest code
echo -e "${YELLOW}[1/8] Pulling latest code from Git...${NC}"
git pull origin master
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Code pulled successfully${NC}"
else
    echo -e "${RED}✗ Failed to pull code${NC}"
    exit 1
fi
echo ""

# Step 2: Clear Python cache
echo -e "${YELLOW}[2/8] Clearing Python cache...${NC}"
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Python cache cleared${NC}"
echo ""

# Step 3: Check Docker status
echo -e "${YELLOW}[3/8] Checking Docker containers...${NC}"
docker-compose ps
echo ""

# Step 4: Rebuild Docker image
echo -e "${YELLOW}[4/8] Rebuilding Docker image...${NC}"
docker-compose build --no-cache web
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image rebuilt successfully${NC}"
else
    echo -e "${RED}✗ Failed to rebuild Docker image${NC}"
    exit 1
fi
echo ""

# Step 5: Stop containers
echo -e "${YELLOW}[5/8] Stopping containers...${NC}"
docker-compose down
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

# Step 6: Start containers
echo -e "${YELLOW}[6/8] Starting containers...${NC}"
docker-compose up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Containers started${NC}"
else
    echo -e "${RED}✗ Failed to start containers${NC}"
    exit 1
fi
echo ""

# Step 7: Wait for containers to be healthy
echo -e "${YELLOW}[7/8] Waiting for containers to be healthy (10 seconds)...${NC}"
sleep 10
echo ""

# Step 8: Health checks
echo -e "${YELLOW}[8/8] Running health checks...${NC}"
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
docker-compose logs --tail=30 web
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Deployment Completed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Latest features deployed:${NC}"
echo -e "  • Dashboard API with top 3 products from subcategories"
echo -e "  • Fixed SubCategoriesModel .id attribute error"
echo -e "  • Improved serializers for better ForeignKey handling"
echo -e "  • Authentication APIs (OTP, Signup, Login)"
echo ""
echo -e "${YELLOW}Test the APIs at:${NC}"
echo -e "  • GET  http://3.110.46.10/api/categories/dashboard"
echo -e "  • POST http://3.110.46.10/apis/auth/send-otp/"
echo -e "  • POST http://3.110.46.10/apis/auth/verify-otp/"
echo -e "  • POST http://3.110.46.10/apis/auth/signup/"
echo -e "  • POST http://3.110.46.10/apis/auth/login/"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "  • View logs:        docker-compose logs -f web"
echo -e "  • Container status: docker-compose ps"
echo -e "  • Restart service:  docker-compose restart web"
echo -e "  • Stop all:         docker-compose down"
echo -e "  • Start all:        docker-compose up -d"
echo ""
