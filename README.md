# 🐘 Vinayaka Chavithi Celebrations — Full-Stack Web Application

A complete, production-ready festival website with a public-facing frontend and a secure admin panel, built with **Flask + MySQL**.

---

## ✨ Features

### Public Website
| Feature | Details |
|---|---|
| 🏠 Homepage | Hero section, countdown timer, live updates ticker, announcements, event timeline, gallery strip |
| 📅 Events Page | Full event schedule with timeline and category filters |
| 👥 Committee | Member cards with photos, roles, and contact info |
| ❤️ Donors | Grouped donor recognition table by category and year |
| 🖼️ Gallery | Masonry photo/video gallery with album filters and lightbox |
| 🙌 Volunteer | Registration form with validation |
| 📞 Contact | Contact details and social links |

### Admin Panel (`/admin`)
| Feature | Details |
|---|---|
| 🔐 Login | Secure authentication with hashed passwords |
| 📊 Dashboard | Stats overview + quick actions |
| 📢 Announcements | Add/edit/delete with priority levels and banner toggle |
| 📡 Live Updates | Real-time ticker messages |
| 📅 Events | Full CRUD with categories and timeline |
| 👥 Committee | Photo uploads, roles, ordering |
| ❤️ Donors | Category-based donor list management |
| 🖼️ Gallery | Multi-file upload (images + videos) |
| 🙌 Volunteers | View, approve/reject registrations |
| ⚙️ Settings | Site title, about text, contact info, social links |
| 🔑 Change Password | Secure password update |

---

## 📁 Project Structure

```
vinayaka_chavithi/
├── app.py                  # Flask app factory + entry point
├── config.py               # Dev / Production / Testing configs
├── extensions.py           # db, login_manager, migrate instances
├── models.py               # All SQLAlchemy models
├── utils.py                # File upload, validation, sanitization
├── wsgi.py                 # Production WSGI entry point
├── requirements.txt        # Python dependencies
├── setup_database.sql      # MySQL database setup script
├── .env.example            # Environment variable template
├── .gitignore
├── routes/
│   ├── __init__.py
│   ├── public.py           # All public-facing routes
│   └── admin.py            # All admin routes (login-protected)
├── templates/
│   ├── public/
│   │   ├── base.html       # Public base template
│   │   ├── index.html      # Homepage
│   │   ├── events.html
│   │   ├── committee.html
│   │   ├── donors.html
│   │   ├── gallery.html
│   │   ├── volunteer.html
│   │   └── contact.html
│   └── admin/
│       ├── base.html       # Admin base template
│       ├── login.html
│       ├── dashboard.html
│       ├── announcements.html
│       ├── announcement_form.html
│       ├── live_updates.html
│       ├── events.html
│       ├── event_form.html
│       ├── committee.html
│       ├── committee_form.html
│       ├── donors.html
│       ├── donor_form.html
│       ├── gallery.html
│       ├── gallery_upload.html
│       ├── volunteers.html
│       ├── settings.html
│       └── change_password.html
└── static/
    ├── css/
    ├── js/
    └── images/
        └── uploads/        # Auto-created, holds uploaded media
```

---

## 🚀 Setup from Scratch (Step-by-Step)

### Prerequisites
- Python 3.10 or higher
- MySQL 8.0 or higher
- pip
- Git (optional)

---

### Step 1 — Clone / Download the Project

```bash
# Option A: Git clone
git clone https://github.com/yourname/vinayaka-chavithi.git
cd vinayaka-chavithi

# Option B: Download ZIP and extract, then navigate into folder
cd vinayaka_chavithi
```

---

### Step 2 — Create a Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

> ✅ You should see `(venv)` at the start of your terminal prompt.

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Set Up MySQL Database

**Option A — Using MySQL Workbench or phpMyAdmin:**
1. Open your MySQL client
2. Copy and paste the contents of `setup_database.sql` and run it

**Option B — Using MySQL command line:**
```bash
mysql -u root -p < setup_database.sql
```

This creates:
- Database: `vinayaka_chavithi_db`
- Optional dedicated user: `appuser` (you can skip this and use root)

---

### Step 5 — Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env    # macOS/Linux
copy .env.example .env  # Windows
```

Now open `.env` in a text editor and fill in your values:

```env
# Generate a strong secret key (run this in Python):
# import secrets; print(secrets.token_hex(32))
SECRET_KEY=your-generated-secret-key-here

FLASK_ENV=development
FLASK_DEBUG=0

DB_HOST=localhost
DB_PORT=3306
DB_NAME=vinayaka_chavithi_db
DB_USER=root           # or 'appuser' if you created one
DB_PASSWORD=your_mysql_password

ADMIN_USERNAME=admin
ADMIN_PASSWORD=Admin@12345   # Change this!
ADMIN_EMAIL=admin@yoursite.com

FESTIVAL_DATE=2025-08-27 06:00:00   # Update to this year's date
```

> ⚠️ **Never commit `.env` to Git.** It is already in `.gitignore`.

---

### Step 6 — Run the Application

```bash
python app.py
```

You should see output like:
```
[INFO] Default admin created: admin
 * Running on http://0.0.0.0:5000
```

Open your browser and go to:
- **Public website:** `http://localhost:5000`
- **Admin panel:** `http://localhost:5000/admin`

Login with the credentials you set in `.env`:
- Username: `admin`
- Password: `Admin@12345` (or whatever you set)

---

## 🌐 Production Deployment

### Option A — Deploy on a VPS (Ubuntu/Debian) with Gunicorn + Nginx

#### 1. Install system packages
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx mysql-server -y
```

#### 2. Upload your project
```bash
scp -r vinayaka_chavithi/ user@your-server-ip:/home/user/
```

#### 3. Set up virtual environment and install
```bash
cd /home/user/vinayaka_chavithi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 4. Set environment variables on the server
```bash
cp .env.example .env
nano .env   # fill in production values
# Set FLASK_ENV=production, FLASK_DEBUG=0
```

#### 5. Test Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

#### 6. Create a Systemd service
```bash
sudo nano /etc/systemd/system/vinayaka.service
```

Paste:
```ini
[Unit]
Description=Vinayaka Chavithi Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/user/vinayaka_chavithi
Environment="PATH=/home/user/vinayaka_chavithi/venv/bin"
ExecStart=/home/user/vinayaka_chavithi/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable vinayaka
sudo systemctl start vinayaka
sudo systemctl status vinayaka  # should show "active (running)"
```

#### 7. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/vinayaka
```

Paste:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 20M;

    location /static {
        alias /home/user/vinayaka_chavithi/static;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/vinayaka /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. Add HTTPS with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

### Option B — Deploy on PythonAnywhere (Easy, Free Tier Available)

1. Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Open a Bash console
3. Clone/upload your project
4. Create a virtual environment and install requirements
5. Set up a MySQL database in the **Databases** tab
6. Add environment variables in the **Files** tab by creating a `.env`
7. In **Web** tab → Add a new web app → Manual configuration → Python 3.11
8. Set the WSGI config file to point to your `wsgi.py`
9. Set static files: URL `/static/` → Directory `/home/yourusername/vinayaka_chavithi/static`
10. Reload the app

---

### Option C — Deploy on Render.com (Free Tier)

1. Push your project to GitHub (without `.env`)
2. Go to [render.com](https://render.com) and create a **Web Service**
3. Connect your GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn wsgi:app`
6. Add environment variables in the **Environment** section
7. Add a **MySQL** database (or use Render's PostgreSQL — requires changing the URI)

---

## 🔒 Security Features

| Security Feature | Implementation |
|---|---|
| Password hashing | Werkzeug `generate_password_hash` (PBKDF2+SHA256) |
| Admin authentication | Flask-Login with `@login_required` on all admin routes |
| Input sanitization | `sanitize_input()` strips XSS/script tags from all form inputs |
| Phone/email validation | Regex-based validation before saving |
| File upload safety | Extension whitelist, `secure_filename`, UUID-based names |
| SQL injection | SQLAlchemy ORM — no raw SQL queries |
| CSRF protection | Flask-WTF (WTF_CSRF_ENABLED=True in config) |
| Secure cookies (prod) | SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY in ProductionConfig |
| Input length limits | maxlength on all form fields and model columns |
| File size limit | MAX_CONTENT_LENGTH = 16MB |

---

## 🗄️ Database Models

| Model | Table | Description |
|---|---|---|
| Admin | admins | Admin user accounts |
| Announcement | announcements | Festival announcements + ticker banners |
| Event | events | Festival events with timeline |
| CommitteeMember | committee_members | Committee member profiles |
| Donor | donors | Donation records grouped by category/year |
| MediaGallery | media_gallery | Photos and videos |
| Volunteer | volunteers | Volunteer registrations |
| SiteSettings | site_settings | Key-value site configuration |
| LiveUpdate | live_updates | Real-time festival updates |

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ Yes | Flask secret key (use `secrets.token_hex(32)`) |
| `FLASK_ENV` | ✅ Yes | `development` or `production` |
| `FLASK_DEBUG` | No | `1` for debug mode, `0` for production |
| `DB_HOST` | ✅ Yes | MySQL host (usually `localhost`) |
| `DB_PORT` | No | MySQL port (default `3306`) |
| `DB_NAME` | ✅ Yes | Database name |
| `DB_USER` | ✅ Yes | MySQL username |
| `DB_PASSWORD` | ✅ Yes | MySQL password |
| `ADMIN_USERNAME` | No | Default admin username (used on first run) |
| `ADMIN_PASSWORD` | No | Default admin password (used on first run) |
| `ADMIN_EMAIL` | No | Default admin email |
| `FESTIVAL_DATE` | No | Date for countdown timer (YYYY-MM-DD HH:MM:SS) |

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'pymysql'"
```bash
pip install PyMySQL
```

### "Access denied for user 'root'@'localhost'"
- Check your `DB_USER` and `DB_PASSWORD` in `.env`
- Ensure MySQL service is running: `sudo systemctl start mysql`

### "Table doesn't exist" error
- The app creates tables automatically on first run via `db.create_all()`
- If tables are missing, run: `python -c "from app import app; from extensions import db; app.app_context().push(); db.create_all()"`

### Uploaded images not showing
- Ensure `static/images/uploads/` directory is writable
- Run: `chmod -R 755 static/images/uploads/`

### "CSRF token missing" on forms
- Ensure you have `SECRET_KEY` set in `.env`
- If using form without WTForms, add `{{ csrf_token() }}` to the form or disable for that route

### App crashes on startup
- Check `.env` file exists and has correct values
- Verify MySQL is running and credentials are correct
- Check Python version: `python --version` (needs 3.10+)

---

## 📅 Updating the Festival Year

Each year, update these values:

1. In `.env`:
   ```env
   FESTIVAL_DATE=2026-08-17 06:00:00
   ```

2. In Admin Panel → Settings:
   - Update "Festival Year" to the current year
   - Update "Welcome Message" as needed

---

## 📝 First-Time Admin Setup

After running the app for the first time:

1. Go to `http://localhost:5000/admin`
2. Login with credentials from `.env`
3. Go to **Settings** → fill in site title, about text, contact info
4. Add **Committee Members** with roles and photos
5. Add **Events** for the upcoming festival
6. Post **Announcements** for the community
7. Upload **Gallery** photos from previous years
8. Start posting **Live Updates** during the festival!

---

## 📞 Support

For any issues, please check the Troubleshooting section above. If the problem persists:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify MySQL is running and the database exists
- Check Python version compatibility (3.10+)

---

*Built with ❤️ for the Vinayaka Chavithi community. Jai Ganesh! 🐘*
