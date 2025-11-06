# 🌐 Hướng dẫn Deploy Dashboard lên VPS

## 🎯 Tổng quan

Deploy Enhanced Hallucination Detection Dashboard lên VPS để chia sẻ với bạn bè và collaborate research.

## 🚀 Option 1: Deploy với Streamlit Cloud (Dễ nhất - Miễn phí)

### Bước 1: Chuẩn bị Repository
```bash
# Push code lên GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Bước 2: Deploy trên Streamlit Cloud
1. Truy cập: https://share.streamlit.io/
2. Connect GitHub account
3. Select repository: `benx3/hallucination`
4. Main file path: `ui/app.py`
5. Deploy!

### Bước 3: Environment Secrets
Trong Streamlit Cloud settings, thêm secrets:
```toml
[secrets]
OPENAI_API_KEY = "sk-your-key"
DEEPSEEK_API_KEY = "sk-your-key"
GOOGLE_API_KEY = "your-google-key"
```

## 🖥️ Option 2: VPS Manual Deploy (Ubuntu/CentOS)

### Bước 1: Setup VPS
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3 python3-pip python3-venv git -y

# Clone repository
git clone https://github.com/benx3/hallucination.git
cd hallucination
```

### Bước 2: Setup Environment
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create config file
cp configs/config.example.json configs/config.json
# Edit với nano/vim để thêm API keys
nano configs/config.json
```

### Bước 3: Setup Systemd Service
Tạo file `/etc/systemd/system/hallucination-dashboard.service`:
```ini
[Unit]
Description=Hallucination Detection Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/hallucination
Environment=PATH=/home/ubuntu/hallucination/.venv/bin
ExecStart=/home/ubuntu/hallucination/.venv/bin/streamlit run ui/app.py --server.port 8502 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Bước 4: Start Service
```bash
# Enable và start service
sudo systemctl enable hallucination-dashboard
sudo systemctl start hallucination-dashboard
sudo systemctl status hallucination-dashboard
```

### Bước 5: Setup Nginx Reverse Proxy
```bash
# Install Nginx
sudo apt install nginx -y

# Create site config
sudo nano /etc/nginx/sites-available/hallucination
```

Nội dung Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Thay bằng domain/IP của bạn

    location / {
        proxy_pass http://localhost:8502;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/hallucination /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🐳 Option 3: Docker Deploy (Recommended)

### Bước 1: Tạo Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create configs directory
RUN mkdir -p configs

# Expose port
EXPOSE 8502

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8502/_stcore/health || exit 1

# Command to run
CMD ["streamlit", "run", "ui/app.py", "--server.port=8502", "--server.address=0.0.0.0"]
```

### Bước 2: Docker Compose Setup
Tạo `docker-compose.yml`:
```yaml
version: '3.8'

services:
  hallucination-dashboard:
    build: .
    ports:
      - "8502:8502"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./configs:/app/configs
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - hallucination-dashboard
    restart: unless-stopped
```

### Bước 3: Deploy với Docker
```bash
# Build và run
docker-compose up -d

# Check logs
docker-compose logs -f

# Update deployment
git pull
docker-compose down
docker-compose up -d --build
```

## 🔒 Option 4: Security & HTTPS Setup

### SSL với Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Basic Authentication (Optional)
Thêm vào Nginx config:
```nginx
location / {
    auth_basic "Hallucination Research Dashboard";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    proxy_pass http://localhost:8502;
    # ... rest of proxy config
}
```

Tạo user/password:
```bash
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd username
```

## 🌍 Option 5: Cloud Platform Deploy

### A. Railway.app (Đơn giản)
1. Connect GitHub repo tại https://railway.app
2. Add environment variables
3. Deploy tự động!

### B. Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: streamlit run ui/app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create your-app-name
heroku config:set OPENAI_API_KEY="your-key"
git push heroku main
```

### C. DigitalOcean App Platform
1. Connect GitHub repo
2. Configure environment variables
3. Auto-deploy on push

## 📱 Access & Sharing

### URLs để share:
```
# VPS:
http://your-server-ip:8502
https://your-domain.com

# Cloud platforms:
https://your-app.streamlit.app
https://your-app.railway.app
https://your-app.herokuapp.com
```

### Demo Mode (Không cần API keys)
Để bạn bè xem demo mà không cần API keys, modify `ui/app.py`:

```python
# Thêm demo mode
if st.sidebar.checkbox("Demo Mode (No API calls)"):
    st.info("🎯 Demo mode: Showing pre-computed results only")
    # Load existing results instead of running new experiments
    load_demo_data()
```

## 🔧 Monitoring & Maintenance

### Log Monitoring
```bash
# Service logs
sudo journalctl -u hallucination-dashboard -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Docker logs
docker-compose logs -f
```

### Resource Monitoring
```bash
# Install htop
sudo apt install htop -y

# Monitor resources
htop
df -h
free -h
```

### Auto-Updates
Script tự động update:
```bash
#!/bin/bash
# update-dashboard.sh
cd /home/ubuntu/hallucination
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart hallucination-dashboard
```

## 💡 Khuyến nghị

### Cho Demo/Sharing:
1. **Streamlit Cloud**: Miễn phí, dễ setup
2. **Railway.app**: Free tier, good performance

### Cho Production:
1. **VPS + Docker**: Full control, scalable
2. **DigitalOcean App Platform**: Managed, reliable

### Security Checklist:
- ✅ Use HTTPS
- ✅ Hide API keys trong environment variables
- ✅ Optional: Add basic auth
- ✅ Monitor resource usage
- ✅ Regular backups of data/

### Cost Estimates:
- **Streamlit Cloud**: Free
- **Railway.app**: Free tier available
- **VPS (DigitalOcean)**: $5-10/month
- **Heroku**: $7/month (Hobby dyno)

**Recommendation**: Bắt đầu với **Streamlit Cloud** cho demo, sau đó scale lên VPS nếu cần more control! 🚀