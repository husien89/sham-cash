# مثال لطرق أساسية يجب إضافة إلى main.py
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sham-cash-secret-key')

# قاعدة بيانات مؤقتة (يجب استبدالها بـ Firebase/Datastore)
users = {
    "admin": {
        "password": generate_password_hash("admin123"),
        "name": "المدير العام",
        "email": "admin@shamcash.com",
        "role": "admin"
    }
}

# طريق تسجيل الدخول
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = users.get(username)
    if user and check_password_hash(user['password'], password):
        session['user'] = username
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "error": "بيانات غير صحيحة"}), 401

# طريق تسجيل الخروج
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True})

# طريق الحصول على بيانات المستخدم
@app.route('/api/me', methods=['GET'])
def get_current_user():
    if 'user' not in session:
        return jsonify({"error": "غير مصادق"}), 401
    return jsonify(users[session['user']])
