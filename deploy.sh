#!/bin/bash

# Deployment Script for Django Application
# This script connects to the server, pulls latest code, runs migrations, and restarts services

# ===================================
# SERVER CONFIGURATION
# ===================================
# UPDATE THESE VALUES WITH YOUR SERVER DETAILS
SERVER_USER="ubuntu"  # Change this to your server username
SERVER_HOST="your-server-ip-or-domain"  # Change this to your server IP or domain
PEM_FILE="docker-server.pem"
PROJECT_PATH="/home/ubuntu/Webservices"  # Change this to your project path on server

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

# Step 6: Restart Docker services
echo -e "${YELLOW}[6/6] Restarting Docker services...${NC}"
docker-compose down
docker-compose up -d --build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker services restarted${NC}"
else
    echo -e "${RED}✗ Failed to restart Docker services${NC}"
    exit 1
fi
echo ""

# Check container status
echo -e "${YELLOW}Checking container status...${NC}"
docker-compose ps
echo ""

# Show recent logs
echo -e "${YELLOW}Recent application logs:${NC}"
docker-compose logs --tail=20 web
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Deployment Completed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}New features deployed:${NC}"
echo -e "  • OTP-based phone verification"
echo -e "  • Complete signup API with encrypted passwords"
echo -e "  • Login API with authentication"
echo -e "  • JWT token generation"
echo ""
echo -e "${YELLOW}Test the APIs at:${NC}"
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
