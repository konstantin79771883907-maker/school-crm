# School Support CRM - Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/konstantin79771883907-maker/school-crm.git
cd school-crm
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Open in browser:**
```
http://localhost:8000
```

## Default Credentials

| Username | Password   | Role    |
|----------|------------|---------|
| admin    | admin123   | Admin   |
| support  | support123 | Support |
| user     | user123    | User    |

## Production Deployment (Linux with systemd)

### 1. Prepare the Server

```bash
# Install Python and dependencies
sudo dnf install python3 python3-pip python3-virtualenv git -y

# Clone repository
cd /opt
sudo git clone https://github.com/konstantin79771883907-maker/school-crm.git
sudo chown -R $USER:$USER school-crm
cd school-crm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Create systemd Service

Copy `school-crm.service` to `/etc/systemd/system/`:

```bash
sudo cp school-crm.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable school-crm
sudo systemctl start school-crm
```

### 3. Configure Nginx (Optional)

Use `nginx.conf.example` as a reference for Nginx configuration.

### 4. Setup Auto-Deploy from GitHub

1. Copy webhook service:
```bash
sudo cp school-crm-hook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable school-crm-hook
sudo systemctl start school-crm-hook
```

2. In GitHub repository settings:
   - Go to Settings → Webhooks
   - Add webhook with URL: `http://YOUR_SERVER_IP/deploy-hook`
   - Set secret matching your `deploy_hook.py` configuration
   - Select "Push events"

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

### Check service status:
```bash
sudo systemctl status school-crm
```

### View logs:
```bash
sudo journalctl -u school-crm -f
```

### Restart service:
```bash
sudo systemctl restart school-crm
```

## Database Location

SQLite database is stored at: `/opt/school-crm/school_crm.db`

Backup regularly in production!
