# Docker Deployment Guide

This guide covers deploying the Venusa Web Services application using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Git (for cloning the repository)

## Project Structure

```
Webservices/
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Django application container
├── nginx.conf              # Nginx reverse proxy configuration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Environment variables template
└── gunicorn.config.py      # Gunicorn WSGI server configuration
```

## Quick Start

### 1. Clone and Setup

```bash
cd Webservices
cp .env.example .env
# Edit .env with your actual credentials
```

### 2. Configure Environment Variables

Edit the `.env` file with your configuration:

**For Local Development (with Docker PostgreSQL):**
```env
DB_HOST=db
DB_NAME=webservices
DB_USER=postgres
DB_PASSWORD=your-secure-password
```

**For Production (with AWS RDS):**
```env
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-rds-password
```

### 3. Deploy

**Option A: With Local PostgreSQL Database**
```bash
docker-compose up -d
```

**Option B: With External Database (AWS RDS)**
```bash
# Comment out the 'db' service in docker-compose.yml
# Update DB_HOST in .env to your RDS endpoint
docker-compose up -d web nginx
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files (if needed)
docker-compose exec web python manage.py collectstatic --noinput
```

## Service Details

### Services Included

1. **db** (PostgreSQL) - Database server
   - Port: 5432
   - Volume: `postgres_data` (persistent storage)

2. **web** (Django + Gunicorn) - Application server
   - Port: 8000 (exposed for debugging)
   - Workers: 3 Gunicorn workers
   - Volumes: `static_volume`, `media_volume`

3. **nginx** - Reverse proxy and static file server
   - Ports: 80 (HTTP), 443 (HTTPS)
   - Serves static files and proxies API requests

### Container Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f web

# Restart a service
docker-compose restart web

# Rebuild and restart
docker-compose up -d --build

# Stop and remove all containers, networks, and volumes
docker-compose down -v
```

## Accessing the Application

- **Application**: http://localhost
- **Admin Panel**: http://localhost/admin/
- **API Documentation**: http://localhost/api/schema/swagger-ui/
- **Direct Django (Debug)**: http://localhost:8000

## Database Management

### Backup Database

```bash
# For Docker PostgreSQL
docker-compose exec db pg_dump -U postgres webservices > backup.sql

# For RDS
pg_dump -h your-rds-endpoint.rds.amazonaws.com -U postgres -d webservices > backup.sql
```

### Restore Database

```bash
# For Docker PostgreSQL
docker-compose exec -T db psql -U postgres webservices < backup.sql

# For RDS
psql -h your-rds-endpoint.rds.amazonaws.com -U postgres -d webservices < backup.sql
```

## Production Deployment

### 1. Security Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use a strong, unique `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use strong database passwords
- [ ] Secure API keys (Twilio, Razorpay, AWS)
- [ ] Enable HTTPS with SSL certificates

### 2. SSL/HTTPS Setup

#### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com

# Update nginx.conf to enable HTTPS section
# Restart nginx
docker-compose restart nginx
```

#### Update nginx.conf
Uncomment the HTTPS server block in `nginx.conf` and update `your-domain.com` with your actual domain.

### 3. Environment-Specific Configuration

**Production .env example:**
```env
DEBUG=False
SECRET_KEY='generate-a-secure-random-key-here'
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=secure-production-password

# Production credentials
MAIL_USER=admin@your-domain.com
MAIL_PASS=secure-email-password
# ... other production keys
```

### 4. Performance Optimization

**Adjust Gunicorn workers** in `docker-compose.yml`:
```yaml
command: gunicorn webservices.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2
```

**Worker calculation**: `(2 x CPU cores) + 1`

## Monitoring and Maintenance

### Health Checks

All services have health checks configured:
- Django: Checks admin login page
- Nginx: Checks /health endpoint
- PostgreSQL: Checks database readiness

```bash
# Check service health
docker-compose ps
```

### View Resource Usage

```bash
# Container stats
docker stats

# Specific container
docker stats django_web
```

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 80
sudo lsof -i :80

# Use different port in docker-compose.yml
ports:
  - "8080:80"
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Verify database is healthy
docker-compose exec db psql -U postgres -d webservices -c "SELECT 1;"
```

#### Permission Issues
```bash
# Fix static/media permissions
docker-compose exec web chown -R appuser:appuser /app/staticfiles /app/media
```

## Scaling

### Horizontal Scaling

```bash
# Scale web service to 3 instances
docker-compose up -d --scale web=3

# Nginx will load balance automatically
```

### Using Docker Swarm (Advanced)

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml venusa

# Scale service
docker service scale venusa_web=3
```

## Development vs Production

**Development** (docker-compose.yml):
```yaml
volumes:
  - .:/app  # Hot reload enabled
environment:
  - DEBUG=True
```

**Production** (docker-compose.yml):
```yaml
volumes:
  - static_volume:/app/staticfiles
  - media_volume:/app/media
environment:
  - DEBUG=False
```

## Troubleshooting

### Reset Everything
```bash
# Stop and remove all containers, volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Access Container Shell
```bash
# Django container
docker-compose exec web bash

# Database container
docker-compose exec db bash

# Nginx container
docker-compose exec nginx sh
```

### Django Management Commands
```bash
# Any Django command
docker-compose exec web python manage.py <command>

# Examples:
docker-compose exec web python manage.py showmigrations
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py dbshell
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

## Support

For issues specific to this deployment, check:
1. Container logs: `docker-compose logs -f`
2. Django logs: Check application logging configuration
3. Nginx logs: `docker-compose exec nginx cat /var/log/nginx/error.log`
