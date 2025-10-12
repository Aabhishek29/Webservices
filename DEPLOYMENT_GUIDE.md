# Django Application Deployment Guide

## Overview

This guide explains how to deploy your Django application running in Docker containers to your production server.

## Prerequisites

- SSH access to the server (ubuntu@3.110.46.10)
- PEM key file (`docker-server.pem`) in the project directory
- Git repository access
- Docker and Docker Compose installed on the server

## Deployment Script

The `deploy.sh` script automates the entire deployment process.

### What the Script Does

1. **Connects to Server**: SSH into your production server using the PEM key
2. **Pulls Latest Code**: Fetches the latest changes from the master branch
3. **Installs Dependencies**: Updates Python packages from requirements.txt
4. **Runs Migrations**: Applies database schema changes
5. **Collects Static Files**: Gathers static assets
6. **Clears Python Cache**: Removes .pyc files and __pycache__ directories
7. **Rebuilds Docker Images**: Creates fresh Docker images with new code
8. **Restarts Containers**: Recreates and starts all Docker containers
9. **Health Checks**: Verifies that the application is running correctly

### How to Use

#### Option 1: Run from Local Machine (Recommended)

```bash
cd /path/to/Webservices
./deploy.sh
```

The script will:
- SSH into the server automatically
- Execute all deployment steps
- Show you real-time progress
- Verify deployment success

#### Option 2: Run on Server Manually

If you prefer to deploy manually:

```bash
# SSH into the server
ssh -i docker-server.pem ubuntu@3.110.46.10

# Navigate to project
cd /home/ubuntu/Webservices

# Pull latest code
git pull origin master

# Clear Python cache
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Rebuild and restart containers
docker-compose build --no-cache web
docker-compose down
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs --tail=50 web
```

## Deployment Workflow

### For New Features

```bash
# 1. Make changes locally
git add .
git commit -m "Your commit message"
git push origin master

# 2. Deploy to server
./deploy.sh
```

### For Hotfixes

```bash
# Same process as above
git add .
git commit -m "Hotfix: description"
git push origin master
./deploy.sh
```

## Post-Deployment Verification

After deployment, verify:

1. **Container Status**
   ```bash
   docker-compose ps
   ```
   All containers should show "Up" status

2. **API Health**
   - Admin: http://3.110.46.10/admin/login/ (should return 200)
   - Dashboard: http://3.110.46.10/api/categories/dashboard (should return 200)

3. **Application Logs**
   ```bash
   docker-compose logs -f web
   ```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Issues

```bash
# Run migrations manually
docker-compose exec web python manage.py migrate

# Check database connection
docker-compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB
```

### Permission Issues

```bash
# Fix PEM file permissions
chmod 400 docker-server.pem

# Fix directory permissions on server
sudo chown -R ubuntu:ubuntu /home/ubuntu/Webservices
```

### Code Not Updating

```bash
# On server, force pull
cd /home/ubuntu/Webservices
git fetch --all
git reset --hard origin/master

# Then rebuild
docker-compose build --no-cache web
docker-compose up -d
```

## Docker Commands Reference

### Container Management

```bash
# View running containers
docker-compose ps

# Stop all containers
docker-compose down

# Start containers
docker-compose up -d

# Restart a specific service
docker-compose restart web

# View logs
docker-compose logs -f web

# Execute commands in container
docker-compose exec web python manage.py shell
```

### Database Management

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Database backup
docker-compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql

# Database restore
docker-compose exec -T postgres psql -U $POSTGRES_USER $POSTGRES_DB < backup.sql
```

### Image Management

```bash
# Build specific service
docker-compose build web

# Build without cache
docker-compose build --no-cache

# Remove unused images
docker image prune -a

# View images
docker images
```

## Environment Variables

The application uses the following environment variables (configured in `.env` file):

- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `DJANGO_SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (should be False in production)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Security Best Practices

1. **Never commit sensitive data**
   - Keep `.env` file out of version control
   - Use `.gitignore` to exclude sensitive files

2. **Keep secrets secure**
   - Store PEM files with proper permissions (chmod 400)
   - Use environment variables for sensitive configuration

3. **Regular updates**
   - Keep Docker images updated
   - Update Python packages regularly
   - Apply security patches promptly

4. **Monitor logs**
   - Check application logs regularly
   - Set up log rotation
   - Monitor for suspicious activity

## Rollback Procedure

If deployment fails or introduces bugs:

```bash
# On server
cd /home/ubuntu/Webservices

# Revert to previous commit
git log --oneline  # Find the commit hash
git reset --hard <previous-commit-hash>

# Rebuild and restart
docker-compose build --no-cache web
docker-compose down
docker-compose up -d
```

## Monitoring

### Check Application Health

```bash
# API endpoints
curl http://3.110.46.10/admin/login/
curl http://3.110.46.10/api/categories/dashboard

# Container health
docker-compose ps

# Resource usage
docker stats
```

### Log Management

```bash
# View recent logs
docker-compose logs --tail=100 web

# Follow logs in real-time
docker-compose logs -f web

# Filter logs
docker-compose logs web | grep ERROR
```

## Support

For issues or questions:

1. Check the logs: `docker-compose logs web`
2. Review this guide
3. Check the application documentation
4. Contact the development team

## Latest Features Deployed

- ✅ Dashboard API with top 3 products from different subcategories
- ✅ Fixed SubCategoriesModel .id attribute error
- ✅ Improved serializers for better ForeignKey handling
- ✅ Authentication APIs (OTP, Signup, Login)
- ✅ JWT token-based authentication
- ✅ Phone verification with OTP

## API Endpoints

Test the following endpoints after deployment:

- `GET  /api/categories/dashboard` - Get dashboard products
- `POST /apis/auth/send-otp/` - Send OTP to phone
- `POST /apis/auth/verify-otp/` - Verify OTP code
- `POST /apis/auth/signup/` - Complete user signup
- `POST /apis/auth/login/` - User login

---

**Last Updated**: October 12, 2025
**Version**: 1.0
**Maintained by**: Development Team
