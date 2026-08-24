"""
ComplaintDesk - Flask Backend
For Nepali College System (TU, PU, etc.)

Database: MySQL (via PyMySQL)
"""

import os
import hashlib
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, g

import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

# Add parent dir to path for classifier module
import sys
sys.path.insert(0, os.path.dirname(__file__))
from classifier.classifier import classifier

app = Flask(__name__)
app.secret_key = "nepal_college_complaint_2024_secret"

# ─── MySQL Configuration ──────────────────────────────────────────────────────
# Override these via environment variables if your MySQL setup differs.
# -------- MySQL Configuration --------
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DB = os.environ.get("MYSQL_DB", "complaintdesk")

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "database", "schema.sql")


# ─── DB Helpers ──────────────────────────────────────────────────────────────
def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    """Create the database (if missing), tables, and seed demo accounts."""
    # Step 1: make sure the database itself exists
    conn = pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
    )
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` "
                    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    conn.close()

    # Step 2: run schema.sql against that database
    conn = pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DB,
    )
    with open(SCHEMA_PATH) as f:
        sql_text = f.read()

    with conn.cursor() as cur:
        for statement in sql_text.split(";"):
            statement = statement.strip()
            if statement:
                cur.execute(statement)

        # Seed demo admin account
        pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cur.execute(
            "INSERT IGNORE INTO users (name, email, password_hash, role, department) "
            "VALUES (%s,%s,%s,%s,%s)",
            ("Admin", "admin@college.edu.np", pw_hash, "admin", "Administration")
        )
        # Seed demo student
        pw_hash2 = hashlib.sha256("student123".encode()).hexdigest()
        cur.execute(
            "INSERT IGNORE INTO users (name, email, password_hash, role, department, semester) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            ("Ram Shrestha", "ram@student.edu.np", pw_hash2, "student", "Computer Science", 4)
        )
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ─── Auth Decorators ─────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


# ─── Pages ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("student_dashboard"))
    return redirect(url_for("login_page"))

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/dashboard")
@login_required
def student_dashboard():
    return render_template("dashboard.html")

@app.route("/admin")
@login_required
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("student_dashboard"))
    return render_template("admin.html")

@app.route("/submit")
@login_required
def submit_page():
    return render_template("submit.html")


# ─── Auth APIs ───────────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM users WHERE email = %s AND password_hash = %s",
            (data["email"], hash_password(data["password"]))
        )
        user = cur.fetchone()

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user["id"]
    session["name"] = user["name"]
    session["role"] = user["role"]
    session["email"] = user["email"]

    return jsonify({
        "success": True,
        "role": user["role"],
        "name": user["name"],
        "redirect": "/admin" if user["role"] == "admin" else "/dashboard"
    })

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    db = get_db()

    with db.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE email = %s", (data["email"],))
        existing = cur.fetchone()
        if existing:
            return jsonify({"error": "Email already registered"}), 400

        cur.execute(
            "INSERT INTO users (name, email, password_hash, role, department, semester, college) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (data["name"], data["email"], hash_password(data["password"]),
             "student", data.get("department", ""), data.get("semester", 1),
             data.get("college", "Tribhuvan University"))
        )
    db.commit()
    return jsonify({"success": True})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/me")
@login_required
def me():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT id, name, email, role, department, semester, college FROM users WHERE id = %s",
            (session["user_id"],)
        )
        user = cur.fetchone()
    return jsonify(user)


# ─── Complaint APIs ───────────────────────────────────────────────────────────
@app.route("/api/classify", methods=["POST"])
@login_required
def classify_preview():
    """Preview AI classification before submitting"""
    data = request.json
    result = classifier.classify(data.get("title", ""), data.get("description", ""))
    return jsonify(result)

@app.route("/api/complaints", methods=["POST"])
@login_required
def submit_complaint():
    data = request.json
    db = get_db()

    # Run AI classification
    ai_result = classifier.classify(data["title"], data["description"])

    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO complaints
               (user_id, title, description, category, priority, sentiment, sentiment_score, is_anonymous)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (session["user_id"], data["title"], data["description"],
             ai_result["category"], ai_result["priority"],
             ai_result["sentiment"], ai_result["sentiment_score"],
             1 if data.get("anonymous") else 0)
        )
        complaint_id = cur.lastrowid

        # Save tags
        for tag in ai_result["tags"]:
            cur.execute("INSERT INTO complaint_tags (complaint_id, tag) VALUES (%s,%s)",
                        (complaint_id, tag))

        # Log activity
        cur.execute(
            "INSERT INTO activity_log (complaint_id, action, performed_by, note) VALUES (%s,%s,%s,%s)",
            (complaint_id, "Submitted", session["name"], "Complaint submitted and auto-classified")
        )

    db.commit()
    return jsonify({"success": True, "id": complaint_id, "ai": ai_result})

@app.route("/api/complaints")
@login_required
def get_complaints():
    db = get_db()
    role = session.get("role")
    user_id = session["user_id"]

    with db.cursor() as cur:
        if role == "admin":
            # Admins see everything, including anonymous complaints and who filed them,
            # so sensitive cases (harassment/bullying/abuse) can be handled directly.
            cur.execute("""
                SELECT c.*, u.name as student_name, u.department, u.semester
                FROM complaints c
                LEFT JOIN users u ON c.user_id = u.id
                ORDER BY c.created_at DESC
            """)
        else:
            # Students see all non-anonymous complaints plus their own anonymous
            # complaints. Anonymous complaints from other students stay hidden.
            cur.execute("""
                SELECT c.*, u.name as student_name, u.department
                FROM complaints c
                LEFT JOIN users u ON c.user_id = u.id
                WHERE c.is_anonymous = 0 OR c.user_id = %s
                ORDER BY c.created_at DESC
            """, (user_id,))
        rows = cur.fetchall()

        complaints = []
        for row in rows:
            c = dict(row)
            # Keep the submitter's identity private even in their own feed.
            if c["is_anonymous"] and role != "admin":
                c["student_name"] = "Anonymous (You)"

            cur.execute("SELECT tag FROM complaint_tags WHERE complaint_id = %s", (c["id"],))
            tags = cur.fetchall()
            c["tags"] = [t["tag"] for t in tags]
            complaints.append(c)

    return jsonify(complaints)

@app.route("/api/complaints/<int:cid>", methods=["PATCH"])
@admin_required
def update_complaint(cid):
    data = request.json
    db = get_db()

    updates = []
    values = []

    if "status" in data:
        updates.append("status = %s")
        values.append(data["status"])
        if data["status"] == "Resolved":
            updates.append("resolved_at = CURRENT_TIMESTAMP")

    if "admin_response" in data:
        updates.append("admin_response = %s")
        values.append(data["admin_response"])

    if "assigned_to" in data:
        updates.append("assigned_to = %s")
        values.append(data["assigned_to"])

    if updates:
        values.append(cid)
        with db.cursor() as cur:
            cur.execute(f"UPDATE complaints SET {', '.join(updates)} WHERE id = %s", values)

            # Log
            action = data.get("status", "Updated")
            cur.execute(
                "INSERT INTO activity_log (complaint_id, action, performed_by, note) VALUES (%s,%s,%s,%s)",
                (cid, action, session["name"], data.get("admin_response", ""))
            )
        db.commit()

    return jsonify({"success": True})

@app.route("/api/complaints/<int:cid>/upvote", methods=["POST"])
@login_required
def upvote(cid):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO upvotes (complaint_id, user_id) VALUES (%s,%s)",
                        (cid, session["user_id"]))
            cur.execute("UPDATE complaints SET upvotes = upvotes + 1 WHERE id = %s", (cid,))
        db.commit()
        return jsonify({"success": True, "voted": True})
    except pymysql.err.IntegrityError:
        # Already voted — remove upvote
        db.rollback()
        with db.cursor() as cur:
            cur.execute("DELETE FROM upvotes WHERE complaint_id = %s AND user_id = %s",
                        (cid, session["user_id"]))
            cur.execute("UPDATE complaints SET upvotes = GREATEST(0, upvotes - 1) WHERE id = %s", (cid,))
        db.commit()
        return jsonify({"success": True, "voted": False})

@app.route("/api/complaints/<int:cid>/activity")
@login_required
def get_activity(cid):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT * FROM activity_log WHERE complaint_id = %s ORDER BY created_at ASC", (cid,)
        )
        logs = cur.fetchall()
    return jsonify(logs)


# ─── Stats / Analytics ────────────────────────────────────────────────────────
@app.route("/api/stats")
@login_required
def get_stats():
    db = get_db()

    if session.get("role") == "admin":
        base_filter = ""
        params = []
    else:
        base_filter = "WHERE user_id = %s"
        params = [session["user_id"]]

    with db.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) as c FROM complaints {base_filter}", params)
        total = cur.fetchone()["c"]

        cur.execute(
            f"SELECT COUNT(*) as c FROM complaints {base_filter} {'AND' if base_filter else 'WHERE'} status='Pending'",
            params)
        pending = cur.fetchone()["c"]

        cur.execute(
            f"SELECT COUNT(*) as c FROM complaints {base_filter} {'AND' if base_filter else 'WHERE'} status='Resolved'",
            params)
        resolved = cur.fetchone()["c"]

        # Category breakdown
        cur.execute(f"SELECT category, COUNT(*) as count FROM complaints {base_filter} GROUP BY category", params)
        cats = cur.fetchall()

        # Priority breakdown
        cur.execute(f"SELECT priority, COUNT(*) as count FROM complaints {base_filter} GROUP BY priority", params)
        prios = cur.fetchall()

        # Sentiment breakdown
        cur.execute(f"SELECT sentiment, COUNT(*) as count FROM complaints {base_filter} GROUP BY sentiment", params)
        sents = cur.fetchall()

        # Recent trend (last 7 days)
        cur.execute(
            f"""SELECT DATE(created_at) as date, COUNT(*) as count
                FROM complaints {base_filter}
                {'AND' if base_filter else 'WHERE'} created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at) ORDER BY date""",
            params
        )
        trend = cur.fetchall()

    return jsonify({
        "total": total,
        "pending": pending,
        "resolved": resolved,
        "in_review": total - pending - resolved,
        "categories": cats,
        "priorities": prios,
        "sentiments": sents,
        "trend": trend
    })


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("\n🎓 ComplaintDesk - College Complaint System (MySQL)")
    print("=" * 50)
    print(f"🗄️  MySQL DB:      {MYSQL_DB} @ {MYSQL_HOST}:{MYSQL_PORT}")
    print("🌐 Open: http://localhost:5000")
    print("👤 Admin Login:   admin@college.edu.np / admin123")
    print("👤 Student Login: ram@student.edu.np  / student123")
    print("=" * 50)
    app.run(debug=True, port=5000)
