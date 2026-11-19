import os
import math
import re
import sqlite3
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "shamcash.sqlite3"))

app = Flask(__name__, static_folder="static")
secret_key = os.environ.get("SECRET_KEY")
if not secret_key:
    secret_key = os.environ.get("FLASK_SECRET_KEY")
if not secret_key:
    secret_key = os.urandom(32)
app.config.update(
    SECRET_KEY=secret_key,
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
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL DEFAULT '',
            balance REAL NOT NULL DEFAULT 500,
            role TEXT NOT NULL DEFAULT 'user'
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            direction TEXT NOT NULL CHECK(direction IN ('in', 'out')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(username) REFERENCES users(username)
        )""")
        db.execute("CREATE INDEX IF NOT EXISTS transactions_username_id ON transactions(username, id DESC)")


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
        "balance": round(float(row["balance"]), 2),
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
    if "username" in session:
        return send_from_directory(app.static_folder, "index.html")
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

    username = str(data.get("username", "")).strip()
    password = data.get("password", "")
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", username):
        return jsonify({"success": False, "error": "اسم المستخدم يجب أن يكون 3-32 حرفاً أو رقماً أو _"}), 400
    if not isinstance(password, str) or len(password) < 10 or len(password) > 1024:
        return jsonify({"success": False, "error": "كلمة المرور يجب ألا تقل عن 10 أحرف"}), 400
    if not name or len(name) > 100:
        return jsonify({"success": False, "error": "الاسم غير صالح"}), 400
    if len(email) > 254:
        return jsonify({"success": False, "error": "البريد الإلكتروني غير صالح"}), 400
    if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return jsonify({"success": False, "error": "البريد الإلكتروني غير صالح"}), 400

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
    return jsonify({"success": True, "user": {"username": username, "name": name, "email": email, "balance": 500, "role": "user"}}), 201


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


@app.get("/api/transactions")
@authenticated
def transactions():
    with get_db() as db:
        rows = db.execute(
            "SELECT id, name, amount, direction, created_at FROM transactions WHERE username = ? ORDER BY id DESC LIMIT 100",
            (session["username"],),
        ).fetchall()
    return jsonify({"success": True, "transactions": [dict(row) for row in rows]})


@app.post("/api/transactions")
@authenticated
def create_transaction():
    data = json_body()
    if data is None:
        return jsonify({"success": False, "error": "طلب غير صالح"}), 400
    name = str(data.get("name", "")).strip()
    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "المبلغ غير صالح"}), 400
    if not math.isfinite(amount):
        return jsonify({"success": False, "error": "المبلغ غير صالح"}), 400
    if not name or len(name) > 100:
        return jsonify({"success": False, "error": "اسم المستلم غير صالح"}), 400
    if amount <= 0 or amount > 100000:
        return jsonify({"success": False, "error": "المبلغ يجب أن يكون أكبر من صفر وأقل من 100000"}), 400

    amount = round(amount, 2)
    username = session["username"]
    with get_db() as db:
        db.execute("BEGIN IMMEDIATE")
        user = db.execute("SELECT balance FROM users WHERE username = ?", (username,)).fetchone()
        if user is None:
            db.rollback()
            return jsonify({"success": False, "error": "المستخدم غير موجود"}), 401
        balance = round(float(user["balance"]), 2)
        if balance < amount:
            db.rollback()
            return jsonify({"success": False, "error": "الرصيد غير كاف"}), 400
        updated_balance = round(balance - amount, 2)
        db.execute("UPDATE users SET balance = ? WHERE username = ?", (updated_balance, username))
        db.execute(
            "INSERT INTO transactions (username, name, amount, direction) VALUES (?, ?, ?, 'out')",
            (username, name, amount),
        )
    return jsonify({"success": True, "balance": updated_balance})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
