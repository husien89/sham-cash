import os
import re
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "shamcash.sqlite3"))

app = Flask(__name__, static_folder="static")
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or os.urandom(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
    PERMANENT_SESSION_LIFETIME=60 * 60 * 12,
)


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                balance REAL NOT NULL DEFAULT 0,
                role TEXT NOT NULL DEFAULT 'user'
            )"""
        )


initialize_database()


def json_body():
    if not request.is_json:
        return None
    body = request.get_json(silent=True)
    return body if isinstance(body, dict) else None


def public_user(row):
    return {
        "username": row["username"],
        "name": row["name"],
        "email": row["email"],
        "balance": row["balance"],
        "role": row["role"],
    }


def authenticated(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return jsonify({"success": False, "error": "غير مصادق"}), 401
        return view(*args, **kwargs)

    return wrapped


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "login.html")


@app.get("/wallet")
@authenticated
def wallet():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/register")
def register():
    data = json_body()
    if data is None:
        return jsonify({"success": False, "error": "طلب غير صالح"}), 400

    username = data.get("username", "")
    password = data.get("password", "")
    name = data.get("name", "")
    email = data.get("email", "")
    if not all(isinstance(value, str) for value in (username, password, name, email)):
        return jsonify({"success": False, "error": "البيانات غير صالحة"}), 400
    username = username.strip()
    name = name.strip()
    email = email.strip()
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", username):
        return jsonify({"success": False, "error": "اسم المستخدم يجب أن يكون 3-32 حرفاً أو رقماً أو _"}), 400
    if len(password) < 10 or len(password) > 1024:
        return jsonify({"success": False, "error": "كلمة المرور يجب ألا تقل عن 10 أحرف"}), 400
    if not name or len(name) > 100 or len(email) > 254:
        return jsonify({"success": False, "error": "الاسم أو البريد الإلكتروني غير صالح"}), 400

    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO users (username, password_hash, name, email) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password), name, email),
            )
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "اسم المستخدم مستخدم بالفعل"}), 409

    session.clear()
    session["username"] = username
    session.permanent = True
    return jsonify({"success": True, "user": {"username": username, "name": name, "email": email, "balance": 0, "role": "user"}}), 201


@app.post("/api/login")
def login():
    data = json_body()
    if data is None:
        return jsonify({"success": False, "error": "طلب غير صالح"}), 400
    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"success": False, "error": "اسم المستخدم وكلمة المرور مطلوبان"}), 400

    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "error": "بيانات الدخول غير صحيحة"}), 401

    session.clear()
    session["username"] = user["username"]
    session.permanent = True
    return jsonify({"success": True, "user": public_user(user)})


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"success": True})


@app.get("/api/me")
@authenticated
def current_user():
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username = ?", (session["username"],)).fetchone()
    if user is None:
        session.clear()
        return jsonify({"success": False, "error": "المستخدم غير موجود"}), 401
    return jsonify({"success": True, "user": public_user(user)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
