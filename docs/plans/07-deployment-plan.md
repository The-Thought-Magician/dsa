# Deployment Plan

## Overview

This plan covers deployment strategies for the A2Z DSA Learning System, from local development to production hosting.

## Deployment Options

| Option | Complexity | Cost | Recommended For |
|--------|------------|------|-----------------|
| Local Development | Low | Free | Development and testing |
| Render.com | Low | Free tier | Quick production deployment |
| Railway.app | Low | Free tier | Easy Docker deployment |
| DigitalOcean | Medium | $4-6/mo | Full control VPS |
| AWS/GCP | High | Variable | Enterprise requirements |

## Phase 1: Production Configuration

### 1.1 Environment Variables

**File**: `.env.production`

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
PRODUCTION=true

# CORS
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# API Keys (required)
GEMINI_API_KEY=your_production_api_key

# Rate Limits
CODE_EXECUTION_RATE_LIMIT=10/minute
AI_CHAT_RATE_LIMIT=20/minute

# Execution Security
EXECUTION_TIMEOUT_SECONDS=5
MAX_CODE_LENGTH=10000
ENABLE_SANDBOX=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/api.log
```

### 1.2 Production Dependencies

**File**: `pyproject.toml`

```toml
[project.optional-dependencies]
production = [
    "uvicorn[standard]>=0.24.0",
    "gunicorn>=21.2.0",
]

[tool.scripts]
start = "gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
```

## Phase 2: Docker Deployment

### 2.1 Dockerfile

**File**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install --system -e .

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run with gunicorn
CMD ["gunicorn", "api.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 2.2 Docker Compose (Local)

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PRODUCTION=false
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  # Optional: Add nginx for production
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    restart: unless-stopped
```

## Phase 3: Render.com Deployment

### 3.1 Render Configuration

**File**: `render.yaml`

```yaml
services:
  - type: web
    name: a2z-dsa-learning
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -e .
    startCommand: gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PRODUCTION
        value: true
      - key: GEMINI_API_KEY
        sync: false
    healthCheckPath: /health
```

### 3.2 Deployment Steps

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Connect Repository**
   - Authorize Render to access your repo
   - Select the DSA repository

3. **Configure Service**
   - Web Service
   - Environment: Python 3
   - Build Command: `pip install -e .`
   - Start Command: `gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

4. **Add Environment Variables**
   - `GEMINI_API_KEY`: Your API key
   - `PRODUCTION`: `true`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete
   - Access at `https://a2z-dsa-learning.onrender.com`

## Phase 4: Railway.app Deployment

### 4.1 Railway Configuration

**File**: `railway.json`

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -e .",
    "watchPatterns": ["api/**", "frontend/**"]
  },
  "deploy": {
    "startCommand": "gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### 4.2 Deployment Steps

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Initialize**
   ```bash
   railway login
   railway init
   ```

3. **Add Variables**
   ```bash
   railway variables set GEMINI_API_KEY=your_key
   railway variables set PRODUCTION=true
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Access**
   ```bash
   railway domain
   ```

## Phase 5: VPS Deployment (DigitalOcean)

### 5.1 Server Setup

**File**: `deploy/setup-server.sh`

```bash
#!/bin/bash
set -e

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3.11 python3.11-venv nginx certbot python3-certbot-nginx

# Create app directory
sudo mkdir -p /opt/a2z-dsa
sudo chown $USER:$USER /opt/a2z-dsa

# Create virtual environment
cd /opt/a2z-dsa
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e .

# Setup systemd service
sudo cp deploy/a2z-dsa.service /etc/systemd/system/
sudo systemctl enable a2z-dsa
sudo systemctl start a2z-dsa

# Setup nginx
sudo cp deploy/a2z-dsa.nginx /etc/nginx/sites-available/a2z-dsa
sudo ln -s /etc/nginx/sites-available/a2z-dsa /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# Setup SSL (replace with your domain)
sudo certbot --nginx -d your-domain.com
```

### 5.2 Systemd Service

**File**: `deploy/a2z-dsa.service`

```ini
[Unit]
Description=A2Z DSA Learning System
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/a2z-dsa
Environment="PATH=/opt/a2z-dsa/venv/bin"
EnvironmentFile=/opt/a2z-dsa/.env
ExecStart=/opt/a2z-dsa/venv/bin/gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.3 Nginx Configuration

**File**: `deploy/a2z-dsa.nginx`

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (optional, serve directly)
    location /assets/ {
        alias /opt/a2z-dsa/frontend/assets/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

## Phase 6: Post-Deployment Checklist

### 6.1 Verification Steps

```bash
# Health check
curl https://your-domain.com/health

# API availability
curl https://your-domain.com/api/stats

# Static files
curl -I https://your-domain.com/assets/css/main.css

# SSL certificate
curl -I https://your-domain.com | grep Strict-Transport-Security
```

### 6.2 Monitoring Setup

1. **Logging**
   - Configure log rotation
   - Monitor error logs
   - Set up alerts

2. **Performance**
   - Monitor response times
   - Check resource usage
   - Set up uptime monitoring

3. **Backups**
   - Database backups (if using one)
   - Progress data backups
   - Configuration backups

## Phase 7: CI/CD Integration

### 7.1 GitHub Actions for Deployment

**File**: `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: ['master']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Render
        run: |
          curl https://api.render.com/v1/services/srv-xxxxx/deploys \
            -X POST \
            -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
```

## Execution Order

| Step | Task | Priority | Dependencies |
|------|------|----------|--------------|
| 1 | Create production .env template | High | - |
| 2 | Create Dockerfile | High | - |
| 3 | Create docker-compose.yml | Medium | Step 2 |
| 4 | Setup Render.com deployment | High | Step 1 |
| 5 | Create systemd service file | Medium | - |
| 6 | Create nginx configuration | Medium | - |
| 7 | Create setup-server.sh script | Medium | Steps 5-6 |
| 8 | Setup CI/CD deployment | Low | Step 4 |
| 9 | Document deployment steps | High | All above |
| 10 | Create post-deployment checklist | Medium | All above |

## Success Criteria

- [ ] Application deploys successfully
- [ ] Health check endpoint responds
- [ ] All API endpoints work
- [ ] Static files serve correctly
- [ ] SSL certificate is valid
- [ ] Environment variables are configured
- [ ] Logs are being collected
- [ ] Auto-restart on failure works
- [ ] Zero-downtime deployments possible
- [ ] Rollback procedure documented

## Rollback Procedure

If deployment fails:

1. **Render/Railway**: Automatic rollback on failed deploy
2. **VPS**:
   ```bash
   # Revert to previous commit
   git checkout previous-commit
   sudo systemctl restart a2z-dsa
   ```
3. **Docker**:
   ```bash
   docker-compose down
   git checkout previous-commit
   docker-compose up -d
   ```
