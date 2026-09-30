"""
app.py – CyberSafe Flask Application
Cybercrime Reporting and Awareness Portal
"""
import os, uuid, re
from datetime import datetime
from functools import wraps

from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, abort, jsonify)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from db import query, execute

# ─────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in app.config['ALLOWED_EXTENSIONS']


def generate_complaint_id():
    """Generate a unique human-readable complaint ID like CS-2026-ABCD1234."""
    year = datetime.now().year
    uid  = uuid.uuid4().hex[:8].upper()
    return f"CS-{year}-{uid}"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access that page.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


def validate_password(pwd):
    """Ensure password is >= 8 chars with uppercase, lowercase, digit, and symbol."""
    if len(pwd) < 8:
        return "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', pwd):
        return "Password must include at least one uppercase letter."
    if not re.search(r'[a-z]', pwd):
        return "Password must include at least one lowercase letter."
    if not re.search(r'\d', pwd):
        return "Password must include at least one number."
    if not re.search(r'[^A-Za-z0-9]', pwd):
        return "Password must include at least one special character."
    return None


# ─────────────────────────────────────────────
# Context processor – inject current user info
# ─────────────────────────────────────────────

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = query("SELECT id, username, full_name, is_admin FROM users WHERE id=%s",
                     (session['user_id'],), one=True)
    return dict(current_user=user)


# ─────────────────────────────────────────────
# Public Routes
# ─────────────────────────────────────────────

@app.route('/')
def home():
    articles = query(
        "SELECT id, title, category, summary, icon FROM articles "
        "WHERE is_published=1 ORDER BY created_at DESC LIMIT 3"
    ) or []
    stats = query(
        "SELECT COUNT(*) AS total, "
        "SUM(status='Submitted') AS submitted, "
        "SUM(status='Under Review') AS under_review, "
        "SUM(status='Resolved') AS resolved "
        "FROM complaints"
    , one=True) or {}
    return render_template('home.html', articles=articles, stats=stats)


# ─────────────────────────────────────────────
# Auth Routes
# ─────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        email     = request.form.get('email', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        phone     = request.form.get('phone', '').strip()
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append("Username may only contain letters, numbers, and underscores.")
        if not email or not re.match(r'^[\w.+-]+@[\w-]+\.[a-z]{2,}$', email, re.I):
            errors.append("A valid email address is required.")
        if not full_name:
            errors.append("Full name is required.")
        pwd_err = validate_password(password)
        if pwd_err:
            errors.append(pwd_err)
        if password != confirm:
            errors.append("Passwords do not match.")

        if not errors:
            existing = query("SELECT id FROM users WHERE username=%s OR email=%s",
                             (username, email), one=True)
            if existing:
                errors.append("That username or email is already registered.")

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html',
                                   form=request.form.to_dict())

        pw_hash = generate_password_hash(password)
        execute(
            "INSERT INTO users (username, email, password_hash, full_name, phone) "
            "VALUES (%s, %s, %s, %s, %s)",
            (username, email, pw_hash, full_name, phone)
        )
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form={})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password', '')

        user = query(
            "SELECT * FROM users WHERE username=%s OR email=%s",
            (identifier, identifier), one=True
        )
        if user and check_password_hash(user['password_hash'], password):
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            flash(f"Welcome back, {user['full_name'] or user['username']}!", 'success')
            next_url = request.args.get('next') or (
                url_for('admin_dashboard') if user['is_admin'] else url_for('dashboard')
            )
            return redirect(next_url)
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ─────────────────────────────────────────────
# User Dashboard
# ─────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    complaints = query(
        "SELECT complaint_id, incident_type, status, created_at "
        "FROM complaints WHERE user_id=%s ORDER BY created_at DESC",
        (uid,)
    ) or []
    counts = query(
        "SELECT "
        "COUNT(*) AS total, "
        "SUM(status='Submitted') AS submitted, "
        "SUM(status='Under Review') AS under_review, "
        "SUM(status='Resolved') AS resolved "
        "FROM complaints WHERE user_id=%s",
        (uid,), one=True
    ) or {}
    return render_template('dashboard.html', complaints=complaints, counts=counts)


# ─────────────────────────────────────────────
# Complaint Routes
# ─────────────────────────────────────────────

INCIDENT_TYPES = [
    'Phishing / Email Fraud',
    'Online Financial Fraud',
    'Identity Theft',
    'Cyberbullying / Online Harassment',
    'Ransomware / Malware Attack',
    'Hacking / Unauthorised Access',
    'Online Scam (Job, Romance, Investment)',
    'Social Media Account Compromise',
    'Data Breach / Privacy Violation',
    'Child Online Safety / CSAM',
    'Other Cybercrime',
]


@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_complaint():
    if request.method == 'POST':
        incident_type  = request.form.get('incident_type', '').strip()
        incident_date  = request.form.get('incident_date', '').strip()
        description    = request.form.get('description', '').strip()
        contact_name   = request.form.get('contact_name', '').strip()
        contact_email  = request.form.get('contact_email', '').strip()
        contact_phone  = request.form.get('contact_phone', '').strip()

        errors = []
        if not incident_type:
            errors.append("Please select an incident type.")
        if not incident_date:
            errors.append("Incident date is required.")
        if not description or len(description) < 30:
            errors.append("Please provide a description of at least 30 characters.")

        evidence_filename = None
        if 'evidence' in request.files:
            f = request.files['evidence']
            if f and f.filename:
                if allowed_file(f.filename):
                    safe  = secure_filename(f.filename)
                    fname = f"{uuid.uuid4().hex}_{safe}"
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                    evidence_filename = fname
                else:
                    errors.append("Evidence file type not allowed. Use PNG, JPG, GIF, PDF, or TXT.")

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('report.html',
                                   incident_types=INCIDENT_TYPES,
                                   form=request.form.to_dict())

        cid = generate_complaint_id()
        execute(
            "INSERT INTO complaints "
            "(complaint_id, user_id, incident_type, incident_date, description, "
            " contact_name, contact_email, contact_phone, evidence_file) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (cid, session['user_id'], incident_type, incident_date,
             description, contact_name, contact_email, contact_phone, evidence_filename)
        )
        # Record initial history entry
        execute(
            "INSERT INTO complaint_history (complaint_id, new_status, notes, changed_by) "
            "VALUES (%s,'Submitted','Complaint submitted by user.',%s)",
            (cid, session['user_id'])
        )
        flash(f'Complaint submitted! Your Complaint ID is <strong>{cid}</strong>. '
              f'Save it to track your report.', 'success')
        return redirect(url_for('track_complaint', cid=cid))

    return render_template('report.html',
                           incident_types=INCIDENT_TYPES,
                           form={})


@app.route('/track', methods=['GET', 'POST'])
def track():
    complaint = None
    history   = []
    searched  = False
    cid       = request.args.get('cid', '').strip().upper()

    if not cid and request.method == 'POST':
        cid = request.form.get('complaint_id', '').strip().upper()

    if cid:
        searched = True
        complaint = query(
            "SELECT c.*, u.username FROM complaints c "
            "JOIN users u ON c.user_id=u.id "
            "WHERE c.complaint_id=%s",
            (cid,), one=True
        )
        if complaint:
            history = query(
                "SELECT ch.*, u.username AS changed_by_name "
                "FROM complaint_history ch "
                "LEFT JOIN users u ON ch.changed_by=u.id "
                "WHERE ch.complaint_id=%s ORDER BY ch.changed_at ASC",
                (cid,)
            ) or []

    return render_template('track.html',
                           complaint=complaint,
                           history=history,
                           searched=searched,
                           cid=cid)


@app.route('/track/<cid>')
def track_complaint(cid):
    return redirect(url_for('track', cid=cid))


# ─────────────────────────────────────────────
# Awareness Articles
# ─────────────────────────────────────────────

@app.route('/awareness')
def awareness():
    category = request.args.get('category', '')
    if category:
        articles = query(
            "SELECT * FROM articles WHERE is_published=1 AND category=%s "
            "ORDER BY created_at DESC", (category,)
        ) or []
    else:
        articles = query(
            "SELECT * FROM articles WHERE is_published=1 ORDER BY created_at DESC"
        ) or []

    categories = query(
        "SELECT DISTINCT category FROM articles WHERE is_published=1 ORDER BY category"
    ) or []
    return render_template('awareness.html', articles=articles,
                           categories=categories, active_cat=category)


@app.route('/awareness/<int:article_id>')
def article_detail(article_id):
    article = query("SELECT * FROM articles WHERE id=%s AND is_published=1",
                    (article_id,), one=True)
    if not article:
        abort(404)
    related = query(
        "SELECT id, title, category, icon FROM articles "
        "WHERE is_published=1 AND id!=%s AND category=%s LIMIT 3",
        (article_id, article['category'])
    ) or []
    return render_template('article.html', article=article, related=related)


# ─────────────────────────────────────────────
# Admin Dashboard
# ─────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = query(
        "SELECT COUNT(*) AS total, "
        "SUM(status='Submitted') AS submitted, "
        "SUM(status='Under Review') AS under_review, "
        "SUM(status='Resolved') AS resolved, "
        "SUM(status='Rejected') AS rejected "
        "FROM complaints", one=True
    ) or {}
    complaints = query(
        "SELECT c.complaint_id, c.incident_type, c.status, c.created_at, "
        "u.username, u.full_name "
        "FROM complaints c JOIN users u ON c.user_id=u.id "
        "ORDER BY c.created_at DESC LIMIT 50"
    ) or []
    user_count = query("SELECT COUNT(*) AS cnt FROM users WHERE is_admin=0",
                       one=True) or {}
    article_count = query("SELECT COUNT(*) AS cnt FROM articles", one=True) or {}
    return render_template('admin_dashboard.html',
                           stats=stats,
                           complaints=complaints,
                           user_count=user_count.get('cnt', 0),
                           article_count=article_count.get('cnt', 0))


@app.route('/admin/complaints')
@admin_required
def admin_complaints():
    status_filter = request.args.get('status', '')
    search        = request.args.get('search', '').strip()
    sql = ("SELECT c.complaint_id, c.incident_type, c.status, c.created_at, "
           "c.updated_at, u.username, u.full_name "
           "FROM complaints c JOIN users u ON c.user_id=u.id WHERE 1=1 ")
    params = []
    if status_filter:
        sql += " AND c.status=%s"; params.append(status_filter)
    if search:
        sql += " AND (c.complaint_id LIKE %s OR u.username LIKE %s OR c.incident_type LIKE %s)"
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    sql += " ORDER BY c.created_at DESC"
    complaints = query(sql, params) or []
    return render_template('admin_complaints.html',
                           complaints=complaints,
                           status_filter=status_filter,
                           search=search)


@app.route('/admin/complaints/<cid>', methods=['GET', 'POST'])
@admin_required
def admin_complaint_detail(cid):
    complaint = query(
        "SELECT c.*, u.username, u.full_name, u.email AS user_email "
        "FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.complaint_id=%s",
        (cid,), one=True
    )
    if not complaint:
        abort(404)

    if request.method == 'POST':
        new_status = request.form.get('status', '')
        notes      = request.form.get('admin_notes', '').strip()
        valid_statuses = ['Submitted', 'Under Review', 'Resolved', 'Rejected']
        if new_status not in valid_statuses:
            flash('Invalid status value.', 'danger')
        else:
            old_status = complaint['status']
            execute(
                "UPDATE complaints SET status=%s, admin_notes=%s WHERE complaint_id=%s",
                (new_status, notes, cid)
            )
            if new_status != old_status:
                execute(
                    "INSERT INTO complaint_history "
                    "(complaint_id, old_status, new_status, notes, changed_by) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (cid, old_status, new_status, notes, session['user_id'])
                )
            flash('Complaint updated successfully.', 'success')
            return redirect(url_for('admin_complaint_detail', cid=cid))

    history = query(
        "SELECT ch.*, u.username AS changed_by_name "
        "FROM complaint_history ch LEFT JOIN users u ON ch.changed_by=u.id "
        "WHERE ch.complaint_id=%s ORDER BY ch.changed_at ASC",
        (cid,)
    ) or []
    return render_template('admin_complaint_detail.html',
                           complaint=complaint, history=history)


# Admin – Article Management

@app.route('/admin/articles')
@admin_required
def admin_articles():
    articles = query("SELECT * FROM articles ORDER BY created_at DESC") or []
    return render_template('admin_articles.html', articles=articles)


@app.route('/admin/articles/new', methods=['GET', 'POST'])
@admin_required
def admin_article_new():
    CATEGORIES = ['Phishing', 'Password Security', 'Malware', 'Online Scams',
                  'Cyberbullying', 'Identity Theft', 'General Safety']
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        summary  = request.form.get('summary', '').strip()
        content  = request.form.get('content', '').strip()
        icon     = request.form.get('icon', 'shield').strip()
        published = 1 if request.form.get('is_published') else 0
        errors = []
        if not title:   errors.append("Title is required.")
        if not category: errors.append("Category is required.")
        if not summary: errors.append("Summary is required.")
        if not content: errors.append("Content is required.")
        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('admin_article_form.html',
                                   form=request.form.to_dict(),
                                   categories=CATEGORIES, action='new')
        execute(
            "INSERT INTO articles (title, category, summary, content, icon, is_published, author_id) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (title, category, summary, content, icon, published, session['user_id'])
        )
        flash('Article created.', 'success')
        return redirect(url_for('admin_articles'))
    return render_template('admin_article_form.html',
                           form={}, categories=CATEGORIES, action='new')


@app.route('/admin/articles/<int:aid>/edit', methods=['GET', 'POST'])
@admin_required
def admin_article_edit(aid):
    CATEGORIES = ['Phishing', 'Password Security', 'Malware', 'Online Scams',
                  'Cyberbullying', 'Identity Theft', 'General Safety']
    article = query("SELECT * FROM articles WHERE id=%s", (aid,), one=True)
    if not article:
        abort(404)
    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        summary  = request.form.get('summary', '').strip()
        content  = request.form.get('content', '').strip()
        icon     = request.form.get('icon', 'shield').strip()
        published = 1 if request.form.get('is_published') else 0
        execute(
            "UPDATE articles SET title=%s, category=%s, summary=%s, content=%s, "
            "icon=%s, is_published=%s WHERE id=%s",
            (title, category, summary, content, icon, published, aid)
        )
        flash('Article updated.', 'success')
        return redirect(url_for('admin_articles'))
    return render_template('admin_article_form.html',
                           form=article, categories=CATEGORIES, action='edit', aid=aid)


@app.route('/admin/articles/<int:aid>/delete', methods=['POST'])
@admin_required
def admin_article_delete(aid):
    execute("DELETE FROM articles WHERE id=%s", (aid,))
    flash('Article deleted.', 'info')
    return redirect(url_for('admin_articles'))


# ─────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403,
                           msg="You do not have permission to access this page."), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404,
                           msg="The page you are looking for could not be found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500,
                           msg="An internal server error occurred."), 500


# ─────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5001)
