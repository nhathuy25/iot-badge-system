from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Kết nối với cơ sở dữ liệu SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Tạo bảng dữ liệu người dùng nếu chưa tồn tại
def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        badge_id TEXT NOT NULL,
        full_name TEXT NOT NULL,
        login_time TEXT NOT NULL,
        photo TEXT NOT NULL
    );
    ''')
    conn.commit()
    conn.close()

# Trang chủ
@app.route("/")
def home():
    return render_template("index.html")

# Trang thành viên
@app.route("/members")
def members():
    return render_template("members.html")

# Trang dữ liệu người dùng
@app.route("/users", methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        # Nhận thông tin từ form
        badge_id = request.form['badge_id']
        full_name = request.form['full_name']
        login_time = request.form['login_time']
        photo = request.files['photo']
        
        # Lưu ảnh
        photo_filename = f"{badge_id}_{photo.filename}"
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))
        
        # Lưu dữ liệu vào cơ sở dữ liệu
        conn = get_db_connection()
        conn.execute('''
        INSERT INTO user_data (badge_id, full_name, login_time, photo) 
        VALUES (?, ?, ?, ?)
        ''', (badge_id, full_name, login_time, photo_filename))
        conn.commit()
        conn.close()
        
        return redirect(url_for('users'))
    
    # Lấy dữ liệu người dùng từ cơ sở dữ liệu
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM user_data').fetchall()
    conn.close()
    
    return render_template("users.html", users=users)

if __name__ == "__main__":
    init_db()  # Khởi tạo cơ sở dữ liệu
    app.run(debug=True)
