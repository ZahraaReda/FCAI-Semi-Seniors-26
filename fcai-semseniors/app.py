"""
FCAI Semi Seniors 26' - Flask Backend
Database: PostgreSQL (via psycopg2)
Run locally: python app.py
Deploy:      gunicorn app:app
"""

import os, json
from datetime import datetime
from functools import wraps
import psycopg2
import psycopg2.extras
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify, flash, send_from_directory)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fcai-dev-secret-change-me")

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── PostgreSQL Connection ─────────────────────────────────────────────────────
# Railway / any host gives you a DATABASE_URL environment variable
# For local: install PostgreSQL, create a DB, fill in below
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:zahraa592006@localhost:5432/fcai_semseniors"
)

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# ── Departments ───────────────────────────────────────────────────────────────
DEPARTMENTS = {
    "CS": {"name": "Cyber Security",          "color": "#6C63FF", "icon": "💻"},
    "AI": {"name": "Artificial Intelligence", "color": "#FF6584", "icon": "🤖"},
    "MP": {"name": "Mobile Programming",      "color": "#43B89C", "icon": "📱"},
    "MI": {"name": "Medical Informatics",     "color": "#F9A825", "icon": "🏥"},
}

def allowed_file(fn):
    return "." in fn and fn.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

app.jinja_env.globals["enumerate"] = enumerate

# ── Quiz Questions ────────────────────────────────────────────────────────────
QUIZ_QUESTIONS = [
    {"id":1,"question":"What excites you the most?","options":[
        {"text":"Building algorithms and solving complex problems","scores":{"CS":3,"AI":2}},
        {"text":"Making machines think and learn like humans",     "scores":{"AI":3,"MI":1}},
        {"text":"Building mobile apps that people use every day", "scores":{"MP":3,"MI":2}},
        {"text":"Using tech to solve real healthcare problems",   "scores":{"MI":3,"AI":1}},
    ]},
    {"id":2,"question":"Your dream project would be:","options":[
        {"text":"Writing an OS kernel or compiler",                    "scores":{"CS":3}},
        {"text":"Training a model that beats humans at chess",         "scores":{"AI":3,"MI":1}},
        {"text":"A mobile app used by millions of people",             "scores":{"MP":3}},
        {"text":"A medical system that helps doctors diagnose faster", "scores":{"MI":3,"MP":1}},
    ]},
    {"id":3,"question":"Which course sounds most fun?","options":[
        {"text":"Algorithms & Data Structures",      "scores":{"CS":3,"AI":1}},
        {"text":"Deep Learning & Neural Networks",   "scores":{"AI":3,"MI":1}},
        {"text":"Mobile App Development",            "scores":{"MP":3,"MI":1}},
        {"text":"Health Informatics & Medical Data", "scores":{"MI":3,"MP":1}},
    ]},
    {"id":4,"question":"How do you prefer to work?","options":[
        {"text":"Alone, deep in low-level code",               "scores":{"CS":3}},
        {"text":"Experimenting with models and research",      "scores":{"AI":3,"MI":1}},
        {"text":"Designing smooth user experiences on mobile", "scores":{"MP":3}},
        {"text":"Analyzing patient data to improve care",      "scores":{"MI":3,"MP":1}},
    ]},
    {"id":5,"question":"Which word resonates most with you?","options":[
        {"text":"Performance",  "scores":{"CS":3}},
        {"text":"Intelligence", "scores":{"AI":3}},
        {"text":"Mobility",     "scores":{"MP":3}},
        {"text":"Health",       "scores":{"MI":3}},
    ]},
]

def calculate_department(answers):
    scores = {"CS":0,"AI":0,"MP":0,"MI":0}
    for q_id, opt_idx in answers.items():
        q = next((q for q in QUIZ_QUESTIONS if str(q["id"])==str(q_id)), None)
        if q and 0 <= opt_idx < len(q["options"]):
            for dept, pts in q["options"][opt_idx]["scores"].items():
                scores[dept] += pts
    return max(scores, key=scores.get), scores

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/gallery")
def gallery():
    conn = get_db()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT p.full_name, p.photo_filename, p.senior_quote, p.department, u.username
        FROM profiles p JOIN users u ON p.user_id = u.id
        WHERE p.photo_filename IS NOT NULL
        ORDER BY p.created_at ASC
    """)
    profiles = cur.fetchall()
    conn.close()
    return render_template("gallery.html", profiles=profiles, departments=DEPARTMENTS,
                           current_user=session.get("username"))

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        email    = request.form.get("email","").strip()
        password = request.form.get("password","")
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("auth.html", mode="register")
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
        if cur.fetchone():
            flash("Username or email already taken.", "error")
            conn.close()
            return render_template("auth.html", mode="register")
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (username, email, generate_password_hash(password))
        )
        new_id = cur.fetchone()["id"]
        conn.commit(); conn.close()
        session["user_id"]  = new_id
        session["username"] = username
        flash("Account created! Set up your profile.", "success")
        return redirect(url_for("profile_setup"))
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier","").strip()
        password   = request.form.get("password","")
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE username=%s OR email=%s", (identifier, identifier))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            flash("Welcome back!", "success")
            return redirect(url_for("gallery"))
        flash("Invalid credentials.", "error")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))

@app.route("/profile/setup", methods=["GET","POST"])
@login_required
def profile_setup():
    conn = get_db()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if request.method == "POST":
        full_name    = request.form.get("full_name","").strip()
        senior_quote = request.form.get("senior_quote","").strip()
        chosen_dept  = request.form.get("department","").strip() or None
        photo_file   = request.files.get("photo")
        photo_filename = None
        if photo_file and allowed_file(photo_file.filename):
            fname = secure_filename(f"user_{session['user_id']}_{photo_file.filename}")
            photo_file.save(os.path.join(UPLOAD_DIR, fname))
            photo_filename = fname
        cur.execute("SELECT id, photo_filename FROM profiles WHERE user_id=%s", (session["user_id"],))
        existing = cur.fetchone()
        if existing:
            if not photo_filename:
                photo_filename = existing["photo_filename"]
            if chosen_dept:
                cur.execute("""UPDATE profiles SET full_name=%s, photo_filename=%s, senior_quote=%s,
                               department=%s, quiz_completed=true, updated_at=%s WHERE user_id=%s""",
                            (full_name, photo_filename, senior_quote,
                             chosen_dept, datetime.utcnow(), session["user_id"]))
            else:
                cur.execute("""UPDATE profiles SET full_name=%s, photo_filename=%s,
                               senior_quote=%s, updated_at=%s WHERE user_id=%s""",
                            (full_name, photo_filename, senior_quote,
                             datetime.utcnow(), session["user_id"]))
        else:
            cur.execute("""INSERT INTO profiles
                           (user_id, full_name, photo_filename, senior_quote, department)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (session["user_id"], full_name, photo_filename, senior_quote, chosen_dept))
        conn.commit()
        cur.execute("SELECT quiz_completed, department FROM profiles WHERE user_id=%s",
                    (session["user_id"],))
        prof = cur.fetchone()
        conn.close()
        flash("Profile saved!", "success")
        if not prof or (not prof["quiz_completed"] and not prof["department"]):
            return redirect(url_for("quiz"))
        return redirect(url_for("gallery"))
    cur.execute("SELECT * FROM profiles WHERE user_id=%s", (session["user_id"],))
    profile = cur.fetchone()
    conn.close()
    return render_template("profile_setup.html", profile=profile)

@app.route("/quiz", methods=["GET","POST"])
@login_required
def quiz():
    if request.method == "POST":
        answers_raw = request.json or {}
        answers = {str(k): int(v) for k, v in answers_raw.items()}
        dept, scores = calculate_department(answers)
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # PostgreSQL upsert using INSERT ... ON CONFLICT
        cur.execute("""
            INSERT INTO quiz_results (user_id, cs_score, ai_score, mp_score, mi_score, answers, suggested_dept)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                cs_score=EXCLUDED.cs_score, ai_score=EXCLUDED.ai_score,
                mp_score=EXCLUDED.mp_score, mi_score=EXCLUDED.mi_score,
                answers=EXCLUDED.answers, suggested_dept=EXCLUDED.suggested_dept,
                taken_at=NOW()
        """, (session["user_id"], scores["CS"], scores["AI"],
              scores["MP"], scores["MI"], json.dumps(answers), dept))
        cur.execute("""UPDATE profiles SET department=%s, quiz_completed=true, updated_at=%s
                       WHERE user_id=%s""", (dept, datetime.utcnow(), session["user_id"]))
        conn.commit(); conn.close()
        return jsonify({"department": dept, "info": DEPARTMENTS[dept], "scores": scores})
    return render_template("quiz.html", questions=QUIZ_QUESTIONS)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/api/gallery")
def api_gallery():
    conn = get_db()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT p.full_name, p.photo_filename, p.senior_quote, p.department, u.username
        FROM profiles p JOIN users u ON p.user_id = u.id
        WHERE p.photo_filename IS NOT NULL ORDER BY p.created_at ASC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True, port=5000)