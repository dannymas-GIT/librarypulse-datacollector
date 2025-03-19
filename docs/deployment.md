# LibraryPulse Deployment Guide (2024)

This guide outlines how to deploy LibraryPulse to AWS Lightsail using modern container practices.

## Prerequisites

- AWS account with Lightsail access
- GitHub repository with the LibraryPulse codebase
- GitHub Personal Access Token with repo and packages scopes

## Step 1: Set up AWS Lightsail Instance

1. Log in to the AWS Management Console
2. Navigate to Lightsail
3. Create a new instance with the following specifications:
   - Linux/Unix
   - OS Only (Ubuntu 24.04 LTS)
   - Instance Plan: At least 4GB RAM (recommended $20/mo plan for production)
   - Add key-value tags if needed
   - Create instance

## Step 2: Configure Security

1. Navigate to the Networking tab of your instance
2. Add the following firewall rules:
   - Allow HTTP (port 80)
   - Allow HTTPS (port 443)
   - Keep SSH (port 22) for administration

## Step 3: Assign Static IP

1. Navigate to the Networking tab
2. Create a static IP and attach it to your instance
3. Note the static IP for DNS configuration

## Step 4: Set up DNS (Optional but recommended)

1. Register a domain or use an existing one
2. Create an A record pointing to your static IP
3. Set up additional records as needed (www, api, etc.)

## Step 5: Connect to the Instance

```bash
ssh -i your-key.pem ubuntu@your-static-ip
```

## Step 6: Install Docker and Docker Compose Plugin

```bash
# Update the system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Set up the Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker and Docker Compose plugin
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installations
docker --version
docker compose version
```

## Step 7: Set up Project Directory

```bash
# Create project directory
sudo mkdir -p /opt/librarypulse
sudo chown -R $USER:$USER /opt/librarypulse
cd /opt/librarypulse
```

## Step 8: Configure GitHub Secrets for CI/CD

In your GitHub repository:

1. Go to Settings > Secrets and variables > Actions
2. Add the following secrets:
   - `LIGHTSAIL_HOST`: Your static IP
   - `LIGHTSAIL_USERNAME`: `ubuntu` (or your instance username)
   - `LIGHTSAIL_SSH_KEY`: The content of your private key
   - `AWS_ROLE_TO_ASSUME`: (If using OIDC)
   - `AWS_REGION`: Your AWS region

## Step 9: Set up Environment Variables

Create a `.env` file in the project directory:

```bash
cat > /opt/librarypulse/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/librarypulse
TEST_DATABASE_URL=postgresql://postgres:postgres@db:5432/librarypulse_test

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS
CORS_ORIGINS=https://yourdomain.com

# Email Configuration (if applicable)
EMAILS_ENABLED=true
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
EMAILS_FROM_EMAIL=noreply@yourdomain.com
EMAILS_FROM_NAME=Library Pulse
EOF
```

## Step 10: Create docker-compose.yml

```bash
cat > /opt/librarypulse/docker-compose.yml << EOF
version: '3.9'

name: librarypulse-production

services:
  backend:
    image: ghcr.io/yourusername/librarypulse/backend:latest
    restart: always
    depends_on:
      - db
      - redis
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - librarypulse-network

  db:
    image: postgres:16-alpine
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=librarypulse
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - librarypulse-network

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - librarypulse-network

  nginx:
    image: nginx:mainline-alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
    networks:
      - librarypulse-network
    command: "/bin/sh -c 'while :; do sleep 6h & wait \$\${!}; nginx -s reload; done & nginx -g \"daemon off;\"'"

  certbot:
    image: certbot/certbot:latest
    restart: unless-stopped
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait \$\${!}; done;'"
    depends_on:
      - nginx

volumes:
  postgres_data:
    name: librarypulse-postgres-data
  redis_data:
    name: librarypulse-redis-data

networks:
  librarypulse-network:
    name: librarypulse-network
    driver: bridge
EOF
```

### Port Conflicts

If you encounter port conflicts during deployment:

1. For the backend service, you can change port `8000:8000` to another port like `8001:8000`. 
   Remember to update your Nginx configuration to proxy to the correct port.

2. For database and Redis services, in production environments:
   - Consider removing direct port exposures for security
   - If you need direct access, use non-default ports (e.g., 5433 for PostgreSQL, 6380 for Redis)
   - Update connection strings in environment variables accordingly

## Step 11: Set up Nginx Configuration

```bash
mkdir -p /opt/librarypulse/nginx
mkdir -p /opt/librarypulse/logs/nginx

cat > /opt/librarypulse/nginx/default.conf << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    server_tokens off;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;
    server_tokens off;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    client_max_body_size 100M;
    
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location / {
        root /usr/share/nginx/html;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Enable gzip compression
    gzip on;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_proxied any;
    gzip_vary on;
    gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rss+xml
        application/vnd.geo+json
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/bmp
        image/svg+xml
        image/x-icon
        text/cache-manifest
        text/css
        text/plain
        text/vcard
        text/vnd.rim.location.xloc
        text/vtt
        text/x-component
        text/x-cross-domain-policy;
}
EOF
```

## Step 12: Set up SSL with Certbot

```bash
mkdir -p /opt/librarypulse/certbot/conf
mkdir -p /opt/librarypulse/certbot/www

# Create SSL configuration files
mkdir -p /opt/librarypulse/certbot/conf
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > /opt/librarypulse/certbot/conf/options-ssl-nginx.conf
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > /opt/librarypulse/certbot/conf/ssl-dhparams.pem

# Start Nginx to serve the ACME challenge
docker compose up -d nginx

# Get SSL certificate
docker compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
  --email your-email@example.com --agree-tos --no-eff-email \
  -d yourdomain.com -d www.yourdomain.com
  
# Reload Nginx to apply SSL configuration
docker compose exec nginx nginx -s reload
```

## Step 13: Set up Container Registry Authentication

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u your-github-username --password-stdin
```

## Step 14: Deploy the Application

```bash
# Pull images and start containers
docker compose pull
docker compose up -d
```

## Step 15: Application Monitoring

Set up monitoring for your application:

```bash
# Install Prometheus and Grafana (optional but recommended)
cat > /opt/librarypulse/monitoring.yml << EOF
version: '3.9'

name: librarypulse-monitoring

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    networks:
      - librarypulse-network

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin_password
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3000:3000"
    networks:
      - librarypulse-network
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:

networks:
  librarypulse-network:
    external: true
EOF

mkdir -p /opt/librarypulse/prometheus
cat > /opt/librarypulse/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    metrics_path: /metrics
    static_configs:
      - targets: ['backend:8000']
EOF

# Start monitoring
docker compose -f monitoring.yml up -d
```

## Step 16: Backup Strategy

Set up a backup strategy for your database:

```bash
mkdir -p /opt/librarypulse/backup
cat > /opt/librarypulse/backup.sh << EOF
#!/bin/bash
set -e

# Create backup directory
BACKUP_DIR="/opt/librarypulse/backup"
BACKUP_FILE="\${BACKUP_DIR}/postgres_backup_\$(date +%Y%m%d_%H%M%S).sql.gz"

# Backup PostgreSQL database
docker compose exec -T db pg_dump -U postgres librarypulse | gzip > "\${BACKUP_FILE}"

# Delete backups older than 7 days
find "\${BACKUP_DIR}" -name "postgres_backup_*.sql.gz" -mtime +7 -delete

# Log backup completion
echo "Backup completed: \${BACKUP_FILE}"
EOF

chmod +x /opt/librarypulse/backup.sh

# Add to crontab to run daily
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/librarypulse/backup.sh >> /opt/librarypulse/backup/backup.log 2>&1") | crontab -
```

## Step 17: System Monitoring

Set up system monitoring:

```bash
cat > /opt/librarypulse/node-exporter.yml << EOF
version: '3.9'

services:
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    networks:
      - librarypulse-network

networks:
  librarypulse-network:
    external: true
EOF

docker compose -f node-exporter.yml up -d
```

## Step 18: Automatic Updates (Optional)

Set up automatic security updates:

```bash
sudo apt install -y unattended-upgrades apt-listchanges
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Additional Resources

- [AWS Lightsail Documentation](https://docs.aws.amazon.com/lightsail)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [Grafana Documentation](https://grafana.com/docs/) 