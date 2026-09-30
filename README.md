# 🛡️ CyberSafe – Cybercrime Reporting and Awareness Portal

> ⚠️ **Educational Prototype Notice** – CyberSafe is an educational web application built for learning purposes.
> It does **not** replace official cybercrime reporting channels.
> For real incidents please visit your national cybercrime authority (e.g. [Cyber Crime Portal India](https://www.cybercrimeportal.gov.in), [FBI IC3](https://www.ic3.gov), [Action Fraud UK](https://www.actionfraud.police.uk)).

---

## 📂 Project Structure

```
cybersafe/
├── app.py              # Flask application – all routes & logic
├── db.py               # MySQL helpers (parameterized queries)
├── config.py           # App settings & DB credentials
├── schema.sql          # Database schema + seed data
├── init_db.py          # One-shot DB initialiser (run once)
├── static/
│   ├── css/style.css   # Dark navy/cyan theme
│   ├── js/main.js      # Client-side interactivity
│   └── uploads/        # Evidence file uploads (auto-created)
└── templates/
    ├── base.html                   # Public site layout
    ├── admin_base.html             # Admin panel layout
    ├── home.html                   # Landing page
    ├── register.html               # User registration
    ├── login.html                  # Login
    ├── dashboard.html              # User dashboard
    ├── report.html                 # Complaint filing form
    ├── track.html                  # Complaint tracking
    ├── awareness.html              # Articles hub
    ├── article.html                # Full article view
    ├── admin_dashboard.html        # Admin overview
    ├── admin_complaints.html       # Complaints list (filter/search)
    ├── admin_complaint_detail.html # Individual complaint + status update
    ├── admin_articles.html         # Articles CRUD list
    ├── admin_article_form.html     # Create / Edit article
    └── error.html                  # 403, 404, 500 pages
```

---

## 🚀 Running the Project Locally

### Prerequisites

| Tool | Version | Notes |
|---|---|---|
| XAMPP | Latest | For MySQL (MariaDB) |
| Python | 3.9+ | |
| pip packages | – | flask, mysql-connector-python, werkzeug |

### Step 1 – Start XAMPP MySQL

1. Open the **XAMPP Control Panel**.
2. Click **Start** next to **MySQL**.
3. Confirm MySQL is running on **port 3306**.

> Or from the command line:
> ```
> C:\xampp\mysql_start.bat
> ```

### Step 2 – Install Python Dependencies

```powershell
pip install flask mysql-connector-python werkzeug
```

### Step 3 – Configure Database Credentials (if needed)

Open `config.py` and update if your XAMPP MySQL uses a different user/password:

```python
MYSQL_HOST     = '127.0.0.1'
MYSQL_PORT     = 3306
MYSQL_USER     = 'root'
MYSQL_PASSWORD = ''          # blank by default in XAMPP
MYSQL_DB       = 'cybersafe_db'
```

### Step 4 – Initialise the Database *(run once)*

```powershell
cd C:\path\to\cybersafe
python init_db.py
```

This will:
- Create the `cybersafe_db` database
- Create all tables (users, complaints, complaint_history, articles)
- Seed 6 awareness articles
- Create default accounts

### Step 5 – Start the Flask Server

```powershell
python app.py
```

The app starts on **http://127.0.0.1:5001**

---

## 🔑 Default Accounts

| Role | Username | Password |
|---|---|---|
| **Administrator** | `admin` | `Admin@123` |
| **Demo User** | `user1` | `User@1234` |

---

## 🌐 Pages & URLs

| Page | URL | Access |
|---|---|---|
| Home | `/` | Public |
| Register | `/register` | Public |
| Login | `/login` | Public |
| Complaint Tracking | `/track` | Public |
| Cyber Awareness Hub | `/awareness` | Public |
| Article Detail | `/awareness/<id>` | Public |
| User Dashboard | `/dashboard` | Logged-in users |
| File Complaint | `/report` | Logged-in users |
| Admin Dashboard | `/admin` | Admin only |
| Admin – Complaints | `/admin/complaints` | Admin only |
| Admin – Articles | `/admin/articles` | Admin only |

---

## 🔒 Security Features

- **Password hashing** – Werkzeug `scrypt` (not plain-text storage)
- **Password policy** – Min 8 chars, uppercase, lowercase, digit, symbol
- **Parameterized SQL** – All queries use `%s` placeholders (prevents SQL injection)
- **Flask sessions** – Secure signed-cookie sessions with a secret key
- **File upload validation** – Only PNG, JPG, GIF, PDF, TXT allowed (max 5 MB)
- **Admin guard** – `@admin_required` decorator on every admin route
- **Input sanitisation** – Server-side validation on all forms

---

## 🗄️ Database Schema

```
users               – id, username, email, password_hash, full_name, phone, is_admin
complaints          – id, complaint_id (CS-YEAR-XXXX), user_id, incident_type,
                      incident_date, description, contact info, evidence_file, status, admin_notes
complaint_history   – id, complaint_id, old_status, new_status, notes, changed_by, changed_at
articles            – id, title, category, summary, content, icon, is_published, author_id
```

---

## 🛠️ Stopping the Server

Press `Ctrl + C` in the terminal window where Flask is running.

To stop MySQL:
```
C:\xampp\mysql_stop.bat
```
