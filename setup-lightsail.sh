#!/bin/bash

# Exit on error
set -e

# Print script usage
function usage {
  echo "Usage: $0 [OPTIONS]"
  echo "Setup Library-Lens project on AWS Lightsail"
  echo ""
  echo "Options:"
  echo "  -d, --domain DOMAIN      Domain name (default: library-lens.com)"
  echo "  -e, --email EMAIL        Email for SSL certificate (required)"
  echo "  -h, --help               Display this help message and exit"
  exit 1
}

# Parse command-line options
DOMAIN="library-lens.com"
EMAIL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -d|--domain)
      DOMAIN="$2"
      shift 2
      ;;
    -e|--email)
      EMAIL="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Check required options
if [ -z "$EMAIL" ]; then
  echo "Error: Email is required for SSL certificate"
  usage
fi

echo "Setting up Library-Lens on AWS Lightsail..."
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
echo "Installing Docker and Docker Compose..."
sudo apt install -y ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER

# Install additional tools
echo "Installing additional tools..."
sudo apt install -y nginx certbot python3-certbot-nginx git jq unzip

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /opt/docker-apps/library-lens/{nginx,data,logs,extracted_data,postgres,redis}
sudo mkdir -p /opt/docker-apps/library-lens/nginx/{conf.d,certs}
sudo mkdir -p /opt/docker-apps/library-lens/certbot/{conf,www}

# Set permissions
echo "Setting permissions..."
sudo chown -R $USER:$USER /opt/docker-apps/library-lens

# Copy configuration files
echo "Copying configuration files..."
cd /opt/docker-apps/library-lens

# Create docker-compose.yml
echo "Creating docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: library-lens-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/proxy.conf:/etc/nginx/proxy.conf:ro
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    depends_on:
      - frontend
      - backend
      - mock-services
      - landing-page
    networks:
      - library-lens-network

  # Frontend application
  frontend:
    image: ${REGISTRY:-ghcr.io/yourusername}/library-lens-frontend:${TAG:-latest}
    container_name: library-lens-frontend
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_URL=/api/v1
        - ENVIRONMENT=${ENVIRONMENT:-production}
    restart: always
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:80/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - library-lens-network

  # Backend API
  backend:
    image: ${REGISTRY:-ghcr.io/yourusername}/library-lens-backend:${TAG:-latest}
    container_name: library-lens-backend
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        - DATABASE_URL=postgresql://postgres:postgres@db:5432/library_lens
        - ENVIRONMENT=${ENVIRONMENT:-production}
    restart: always
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/library_lens
      - TEST_DATABASE_URL=postgresql://postgres:postgres@db:5432/library_lens_test
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY:-supersecretkey}
      - ENVIRONMENT=${ENVIRONMENT:-production}
      - ALLOWED_ORIGINS=http://localhost,https://${DOMAIN}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./extracted_data:/app/extracted_data
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    networks:
      - library-lens-network

  # Mock services for switch, backup, sonicwall
  mock-services:
    image: ${REGISTRY:-ghcr.io/yourusername}/library-lens-mock:${TAG:-latest}
    container_name: library-lens-mock
    build:
      context: ./mock-services
      dockerfile: Dockerfile
    restart: always
    environment:
      - NODE_ENV=${ENVIRONMENT:-production}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - library-lens-network

  # Landing page
  landing-page:
    image: ${REGISTRY:-ghcr.io/yourusername}/library-lens-landing:${TAG:-latest}
    container_name: library-lens-landing
    build:
      context: ./landing
      dockerfile: Dockerfile
    restart: always
    environment:
      - NODE_ENV=${ENVIRONMENT:-production}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    networks:
      - library-lens-network

  # Database
  db:
    image: postgres:15-alpine
    container_name: library-lens-db
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=library_lens
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - library-lens-network

  # Redis for caching and rate limiting
  redis:
    image: redis:7-alpine
    container_name: library-lens-redis
    restart: always
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - library-lens-network

  # Certbot for SSL certificates
  certbot:
    image: certbot/certbot
    container_name: library-lens-certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - nginx
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

volumes:
  postgres_data:
    name: library-lens-postgres-data
  redis_data:
    name: library-lens-redis-data

networks:
  library-lens-network:
    name: library-lens-network
    driver: bridge
EOF

# Update domain in docker-compose.yml
sed -i "s/ALLOWED_ORIGINS=http:\/\/localhost,https:\/\/\${DOMAIN}/ALLOWED_ORIGINS=http:\/\/localhost,https:\/\/$DOMAIN/g" docker-compose.yml

# Create Nginx configuration files
echo "Creating Nginx configuration files..."

# nginx.conf
cat > nginx/nginx.conf << 'EOF'
user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout  65;
    types_hash_max_size 2048;
    server_tokens off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    # Include proxy configuration
    include /etc/nginx/proxy.conf;

    # Gzip Settings
    gzip on;
    gzip_disable "msie6";
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_min_length 256;
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

    # Include all virtual host configs
    include /etc/nginx/conf.d/*.conf;
}
EOF

# proxy.conf
cat > nginx/proxy.conf << 'EOF'
proxy_http_version 1.1;
proxy_cache_bypass $http_upgrade;

# Proxy headers
proxy_set_header Upgrade           $http_upgrade;
proxy_set_header Connection        "upgrade";
proxy_set_header Host              $host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host  $host;
proxy_set_header X-Forwarded-Port  $server_port;

# Proxy timeouts
proxy_connect_timeout              60s;
proxy_send_timeout                 60s;
proxy_read_timeout                 60s;
EOF

# default.conf
cat > nginx/conf.d/default.conf << 'EOF'
# Define upstream servers
upstream frontend {
    server frontend:80;
}

upstream backend {
    server backend:8000;
}

upstream mock-services {
    server mock-services:3000;
}

upstream landing-page {
    server landing-page:3000;
}

# HTTP server block (redirects to HTTPS)
server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;
    
    # For certbot challenges
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all HTTP requests to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS server block
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/chain.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), interest-cohort=()" always;

    # Logging
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Root location serves the frontend
    location / {
        proxy_pass http://frontend;
    }

    # Backend API
    location /api/v1/ {
        proxy_pass http://backend/api/v1/;
    }

    # API Documentation
    location /docs {
        proxy_pass http://backend/docs;
    }

    location /redoc {
        proxy_pass http://backend/redoc;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://backend/health;
    }

    # Mock services
    location /app/switch/ {
        proxy_pass http://mock-services/switch/;
    }

    location /app/backup/ {
        proxy_pass http://mock-services/backup/;
    }

    location /app/sonicwall/ {
        proxy_pass http://mock-services/sonicwall/;
    }

    # Landing page
    location /landing/ {
        proxy_pass http://landing-page/;
    }

    # Static assets with caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|pdf|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://frontend;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        access_log off;
    }

    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
EOF

# Update domain in default.conf
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" nginx/conf.d/default.conf

# Create environment file
echo "Creating .env file..."
SECRET_KEY=$(openssl rand -hex 32)
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@db:5432/library_lens
SECRET_KEY=$SECRET_KEY
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF

# Create a dummy placeholder for mock services
echo "Creating mock services placeholder..."
mkdir -p mock-services
cat > mock-services/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN npm init -y && \
    npm install express cors morgan

# Copy application code
COPY . .

# Create a simple Express app
RUN echo 'const express = require("express");' > index.js && \
    echo 'const cors = require("cors");' >> index.js && \
    echo 'const morgan = require("morgan");' >> index.js && \
    echo 'const app = express();' >> index.js && \
    echo 'const port = process.env.PORT || 3000;' >> index.js && \
    echo 'app.use(cors());' >> index.js && \
    echo 'app.use(morgan("combined"));' >> index.js && \
    echo 'app.use(express.json());' >> index.js && \
    echo 'app.get("/health", (req, res) => res.json({ status: "healthy" }));' >> index.js && \
    echo 'app.get("/switch", (req, res) => res.json({ message: "Switch mock service" }));' >> index.js && \
    echo 'app.get("/backup", (req, res) => res.json({ message: "Backup mock service" }));' >> index.js && \
    echo 'app.get("/sonicwall", (req, res) => res.json({ message: "Sonicwall mock service" }));' >> index.js && \
    echo 'app.listen(port, () => console.log(`Mock services running on port ${port}`));' >> index.js

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "index.js"]
EOF

# Create a dummy placeholder for landing page
echo "Creating landing page placeholder..."
mkdir -p landing
cat > landing/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN npm init -y && \
    npm install express cors morgan

# Copy application code
COPY . .

# Create a simple Express app
RUN echo 'const express = require("express");' > index.js && \
    echo 'const cors = require("cors");' >> index.js && \
    echo 'const morgan = require("morgan");' >> index.js && \
    echo 'const app = express();' >> index.js && \
    echo 'const port = process.env.PORT || 3000;' >> index.js && \
    echo 'app.use(cors());' >> index.js && \
    echo 'app.use(morgan("combined"));' >> index.js && \
    echo 'app.use(express.json());' >> index.js && \
    echo 'app.get("/health", (req, res) => res.json({ status: "healthy" }));' >> index.js && \
    echo 'app.get("/", (req, res) => {' >> index.js && \
    echo '  res.send(`' >> index.js && \
    echo '    <!DOCTYPE html>' >> index.js && \
    echo '    <html lang="en">' >> index.js && \
    echo '    <head>' >> index.js && \
    echo '      <meta charset="UTF-8">' >> index.js && \
    echo '      <meta name="viewport" content="width=device-width, initial-scale=1.0">' >> index.js && \
    echo '      <title>Library Lens</title>' >> index.js && \
    echo '      <style>' >> index.js && \
    echo '        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }' >> index.js && \
    echo '        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }' >> index.js && \
    echo '        h1 { color: #2c3e50; }' >> index.js && \
    echo '        .card { background-color: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }' >> index.js && \
    echo '        .button { display: inline-block; background-color: #3498db; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; margin-right: 1rem; }' >> index.js && \
    echo '      </style>' >> index.js && \
    echo '    </head>' >> index.js && \
    echo '    <body>' >> index.js && \
    echo '      <div class="container">' >> index.js && \
    echo '        <h1>Welcome to Library Lens</h1>' >> index.js && \
    echo '        <div class="card">' >> index.js && \
    echo '          <h2>Library Data Analytics</h2>' >> index.js && \
    echo '          <p>Comprehensive analytics and insights for library management.</p>' >> index.js && \
    echo '          <a href="/" class="button">Dashboard</a>' >> index.js && \
    echo '        </div>' >> index.js && \
    echo '        <div class="card">' >> index.js && \
    echo '          <h2>Mock Services</h2>' >> index.js && \
    echo '          <p>Access mock services for demonstration purposes.</p>' >> index.js && \
    echo '          <a href="/app/switch" class="button">Switch</a>' >> index.js && \
    echo '          <a href="/app/backup" class="button">Backup</a>' >> index.js && \
    echo '          <a href="/app/sonicwall" class="button">Sonicwall</a>' >> index.js && \
    echo '        </div>' >> index.js && \
    echo '      </div>' >> index.js && \
    echo '    </body>' >> index.js && \
    echo '    </html>' >> index.js && \
    echo '  `);' >> index.js && \
    echo '});' >> index.js && \
    echo 'app.listen(port, () => console.log(`Landing page running on port ${port}`));' >> index.js

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "index.js"]
EOF

# Set up SSL with Certbot (if domain is configured)
echo "Setting up SSL with Certbot for $DOMAIN..."
sudo certbot certonly --standalone -d "$DOMAIN" -d "www.$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive

# Copy SSL certificates to the correct location
echo "Copying SSL certificates..."
sudo cp -L /etc/letsencrypt/live/$DOMAIN/fullchain.pem certbot/conf/fullchain.pem
sudo cp -L /etc/letsencrypt/live/$DOMAIN/privkey.pem certbot/conf/privkey.pem
sudo cp -L /etc/letsencrypt/live/$DOMAIN/chain.pem certbot/conf/chain.pem
sudo chown -R $USER:$USER certbot/conf/

# Create a cron job for certificate renewal
echo "Creating cron job for certificate renewal..."
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet") | crontab -

# Create a script to pull images from GitHub Packages
echo "Creating script to pull images from GitHub Packages..."
cat > pull-images.sh << 'EOF'
#!/bin/bash

# Set GitHub username and token
read -p "GitHub Username: " GITHUB_USERNAME
read -sp "GitHub Token: " GITHUB_TOKEN
echo

# Login to GitHub Container Registry
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin

# Pull the latest images
docker compose pull

# Start the services
docker compose up -d

# Clean up
docker system prune -f
EOF
chmod +x pull-images.sh

echo ""
echo "=========================================================="
echo "Setup complete! Library-Lens is now configured on your server."
echo ""
echo "Next steps:"
echo "1. Make sure your domain ($DOMAIN) points to this server's IP address."
echo "2. Run the following command to pull images and start the services:"
echo "   cd /opt/docker-apps/library-lens && ./pull-images.sh"
echo ""
echo "==========================================================" 