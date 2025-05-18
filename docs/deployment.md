# Production Deployment Guide

This guide provides instructions for deploying the E-Learning Platform to a production environment.

## Prerequisites

- Ubuntu 20.04 LTS or similar Linux server
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Let's Encrypt for SSL
- Domain name pointed to your server

## Server Setup

### Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Packages

```bash
sudo apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```

### Create a PostgreSQL Database

```bash
sudo -u postgres psql

CREATE DATABASE e_learning;
CREATE USER e_learning_user WITH PASSWORD 'secure_password';
ALTER ROLE e_learning_user SET client_encoding TO 'utf8';
ALTER ROLE e_learning_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE e_learning_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE e_learning TO e_learning_user;
\q
```

## Application Setup

### Create Application User

```bash
sudo adduser e_learning
sudo usermod -aG sudo e_learning
su - e_learning
```

### Clone the Repository

```bash
git clone https://github.com/yourusername/e-learning.git
cd e-learning
```

### Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
nano .env
```

Update the following variables:

```
DEBUG=False
SECRET_KEY=your_secure_generated_key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# PostgreSQL
DATABASE_URL=postgres://e_learning_user:secure_password@localhost:5432/e_learning

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@provider.com
EMAIL_HOST_PASSWORD=your-email-password

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### Prepare Static and Media Files

```bash
python manage.py collectstatic --noinput
mkdir -p media/profile_pics media/courses
chmod -R 755 media
```

### Run Migrations and Create Superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Configure Gunicorn

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/e_learning.service
```

Add the following content:

```ini
[Unit]
Description=E-Learning Platform Gunicorn daemon
After=network.target

[Service]
User=e_learning
Group=www-data
WorkingDirectory=/home/e_learning/e-learning
ExecStart=/home/e_learning/e-learning/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/e_learning/e-learning/e_learning.sock \
          e_learning.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl start e_learning
sudo systemctl enable e_learning
```

## Configure Nginx

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/e_learning
```

Add the following content:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/e_learning/e-learning;
    }
    
    location /media/ {
        root /home/e_learning/e-learning;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/e_learning/e-learning/e_learning.sock;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/e_learning /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### Set Up SSL with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Maintenance Tasks

### Database Backups

Create a backup script:

```bash
sudo nano /home/e_learning/backup.sh
```

Add the following:

```bash
#!/bin/bash
BACKUP_DIR="/home/e_learning/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/e_learning_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR
pg_dump -U e_learning_user -h localhost e_learning > $BACKUP_FILE
gzip $BACKUP_FILE

# Rotate backups - keep only last 7
ls -tp $BACKUP_DIR/*.sql.gz | grep -v '/$' | tail -n +8 | xargs -I {} rm -- {}
```

Make it executable:

```bash
sudo chmod +x /home/e_learning/backup.sh
```

Add to crontab:

```bash
sudo crontab -e
```

```
0 2 * * * /home/e_learning/backup.sh
```

### Log Rotation

```bash
sudo nano /etc/logrotate.d/e_learning
```

Add:

```
/home/e_learning/e-learning/logs/*.log {
    weekly
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 640 e_learning www-data
}
```

## Monitoring

Consider setting up monitoring with tools like:

- Prometheus + Grafana
- Datadog
- New Relic
- Sentry for error tracking

## Scaling Considerations

As your platform grows, consider:

1. Moving static/media files to a CDN
2. Setting up load balancing
3. Database read replicas
4. Implementing caching with Redis or Memcached
