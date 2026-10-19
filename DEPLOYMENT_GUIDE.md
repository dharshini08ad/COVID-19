# Deployment Guide: COVID-19 Hospital Management System with Big Data Essentials

This guide covers 5 flexible ways to deploy this Django application, from instant 1-click cloud hosting to Docker containers and local network presentations.

---

## Pre-Configured Deployment Assets Included

The repository now contains all necessary production configuration files:
- `requirements.txt`: Python package specifications with WhiteNoise, Gunicorn, and Django.
- `Procfile`: WSGI server entrypoint for PaaS platforms (Render, Railway, Heroku).
- `render.yaml`: Infrastructure-as-code for Render.com automatic builds.
- `Dockerfile` & `docker-compose.yml`: Production container specifications.
- `staticfiles/`: Pre-collected, compressed production static assets served via WhiteNoise.

---

## Option 1: Deploy to Render.com (Recommended — Free & Easiest)

Render provides free hosting with automatic HTTPS and direct GitHub integration.

### Steps:
1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "COVID-19 HMS with Big Data (HDFS & Hive)"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Create Web Service on Render**:
   - Go to [https://render.com](https://render.com) and log in.
   - Click **New +** → **Web Service**.
   - Select your GitHub repository.
   - Fill in the following details:
     - **Name**: `covid19-hospital-management`
     - **Environment**: `Python 3`
     - **Region**: Any (e.g., Singapore / Frankfurt / Oregon)
     - **Branch**: `main`
     - **Build Command**:
       ```bash
       pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_data
       ```
     - **Start Command**:
       ```bash
       gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
       ```
     - **Plan**: `Free`

3. **Set Environment Variables**:
   Under the **Environment Variables** tab, add:
   - `DJANGO_DEBUG` = `false`
   - `DJANGO_SECRET_KEY` = *(click "Generate" or enter a random 50-character string)*
   - `ALLOWED_HOSTS` = `.onrender.com,localhost,127.0.0.1`
   - `CSRF_TRUSTED_ORIGINS` = `https://*.onrender.com`

4. Click **Create Web Service**. Within 2–3 minutes, your application will be live at `https://your-service.onrender.com`!

---

## Option 2: Deploy to Railway.app

Railway detects the `Procfile` and `requirements.txt` automatically.

1. Sign in to [https://railway.app](https://railway.app).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select this repository.
4. Add environment variables:
   - `DJANGO_DEBUG` = `false`
   - `DJANGO_SECRET_KEY` = `your-secure-secret-key`
   - `ALLOWED_HOSTS` = `.railway.app,localhost,127.0.0.1`
   - `CSRF_TRUSTED_ORIGINS` = `https://*.railway.app`
5. Railway will automatically build and assign a public domain.

---

## Option 3: Deploy to PythonAnywhere (Free Python Hosting)

PythonAnywhere is tailored specifically for Python and Django applications.

1. Create a free account at [https://www.pythonanywhere.com](https://www.pythonanywhere.com).
2. Go to **Consoles** → Start a **Bash** console.
3. Clone your GitHub repository:
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   mkvirtualenv --python=/usr/bin/python3.10 covid-env
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_data
   python manage.py collectstatic --noinput
   ```
4. Go to the **Web** tab on PythonAnywhere:
   - Click **Add a new web app** → Choose **Manual configuration** → **Python 3.10**.
   - Set **Virtualenv path**: `/home/<username>/.virtualenvs/covid-env`.
   - Set **Source code directory**: `/home/<username>/<your-repo-name>`.
   - In **WSGI configuration file**, edit it to load Django:
     ```python
     import os
     import sys
     path = '/home/<username>/<your-repo-name>'
     if path not in sys.path:
         sys.path.append(path)
     os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
   - In **Static Files**:
     - URL: `/static/`
     - Directory: `/home/<username>/<your-repo-name>/staticfiles`
5. Click **Reload <username>.pythonanywhere.com**. Your app is live!

---

## Option 4: Deploy using Docker & Docker Compose (Any VPS / Cloud Server)

For deployment on AWS EC2, DigitalOcean, Linode, or Google Cloud VM:

1. Connect to your VPS:
   ```bash
   ssh user@your-server-ip
   ```
2. Install Docker and Docker Compose:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   ```
3. Clone your repository:
   ```bash
   git clone https://github.com/<your-username>/<your-repo-name>.git
   cd <your-repo-name>
   ```
4. Start the container in detached mode:
   ```bash
   docker-compose up -d --build
   ```
5. Check status:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```
Your application will be live at `http://your-server-ip:8000/`.

---

## Option 5: Local Network / Presentation Deployment (LAN / Wi-Fi)

To demonstrate the system live to evaluators, professors, or team members across the same Wi-Fi network without cloud hosting:

1. Find your computer's local IP address:
   - **Windows PowerShell**:
     ```powershell
     Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like "*Wi-Fi*" -or $_.InterfaceAlias -like "*Ethernet*" } | Select-Object IPAddress
     ```
   - *Example Output: `192.168.1.45`*

2. Run the Django server binding to `0.0.0.0`:
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```

3. Open Windows Defender Firewall for port 8000 (if prompted or via PowerShell):
   ```powershell
   New-NetFirewallRule -DisplayName "Django COVID-19 HMS" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

4. Anyone connected to the same Wi-Fi can now open the app on their phone or laptop:
   ```
   http://192.168.1.45:8000/
   ```

---

## Default Administrator Credentials
- **Username**: `admin`
- **Password**: `admin123`
- **Admin Panel URL**: `/admin/`
