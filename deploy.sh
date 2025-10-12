#!/bin/bash

# Deployment Script for Django Application
# This script connects to the server, pulls latest code, runs migrations, and restarts services

# ===================================
# SERVER CONFIGURATION
# ===================================
SERVER_USER="ubuntu"
SERVER_HOST="3.110.46.10"
PEM_FILE="docker-server.pem"
PROJECT_PATH="/home/ubuntu/Webservices"

# ===================================
# COLORS FOR OUTPUT
# ===================================
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Django Application Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ===================================
# CHECK IF PEM FILE EXISTS
# ===================================
if [ ! -f "$PEM_FILE" ]; then
    echo -e "${RED}Error: PEM file not found: $PEM_FILE${NC}"
    exit 1
fi

# Set correct permissions for PEM file
chmod 400 "$PEM_FILE"
echo -e "${GREEN}✓ PEM file permissions set${NC}"

# ===================================
# SSH INTO SERVER AND DEPLOY
# ===================================
echo -e "${YELLOW}Connecting to server: $SERVER_USER@$SERVER_HOST${NC}"
echo ""

ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'ENDSSH'

# Set colors for remote output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Deployment Steps on Server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Navigate to project directory
cd /home/ubuntu/Webservices || exit 1

# Step 1: Pull latest code
echo -e "${YELLOW}[1/6] Pulling latest code from Git...${NC}"
git pull origin master
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Code pulled successfully${NC}"
else
    echo -e "${RED}✗ Failed to pull code${NC}"
    exit 1
fi
echo ""

# Step 2: Check if virtual environment exists
echo -e "${YELLOW}[2/6] Activating virtual environment...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${RED}✗ Virtual environment not found${NC}"
    exit 1
fi
echo ""

# Step 3: Install/Update dependencies
echo -e "${YELLOW}[3/6] Installing dependencies...${NC}"
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
fi
echo ""

# Step 4: Run migrations
echo -e "${YELLOW}[4/6] Running database migrations...${NC}"
python manage.py makemigrations
python manage.py migrate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations completed${NC}"
else
    echo -e "${RED}✗ Migrations failed${NC}"
    exit 1
fi
echo ""

# Step 5: Collect static files
echo -e "${YELLOW}[5/6] Collecting static files...${NC}"
python manage.py collectstatic --noinput
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Static files collected${NC}"
else
    echo -e "${YELLOW}⚠ Static files collection had issues (may be expected)${NC}"
fi
echo ""

# Step 6: Clear Python cache
echo -e "${YELLOW}[6/8] Clearing Python cache...${NC}"
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Python cache cleared${NC}"
echo ""

# Step 7: Rebuild and restart Docker services
echo -e "${YELLOW}[7/8] Rebuilding Docker images...${NC}"
docker-compose build --no-cache web
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image rebuilt successfully${NC}"
else
    echo -e "${RED}✗ Failed to rebuild Docker image${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Recreating Docker containers...${NC}"
docker-compose down
docker-compose up -d
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker services restarted${NC}"
else
    echo -e "${RED}✗ Failed to restart Docker services${NC}"
    exit 1
fi
echo ""

# Wait for containers to be healthy
echo -e "${YELLOW}Waiting for containers to be healthy (10 seconds)...${NC}"
sleep 10
echo ""

# Step 8: Health check
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
echo -e "${YELLOW}Test the APIs at http://3.110.46.10:${NC}"
echo -e "  • GET  /api/categories/dashboard"
echo -e "  • POST /apis/auth/send-otp/"
echo -e "  • POST /apis/auth/verify-otp/"
echo -e "  • POST /apis/auth/signup/"
echo -e "  • POST /apis/auth/login/"
echo ""

ENDSSH

# ===================================
# LOCAL COMPLETION MESSAGE
# ===================================
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Deployment Process Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. Test the authentication APIs"
    echo -e "  2. Check application logs: docker-compose logs -f web"
    echo -e "  3. Review API documentation in AUTH_API_DOCUMENTATION.md"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}   Deployment Failed!${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "${YELLOW}Check the error messages above${NC}"
    echo ""
fi
