from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="attendancesystem"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def show_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        user_id = request.form['id']
        name = request.form['name']
        rfid_uid = request.form['rfid_uid']
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (id, name, rfid_uid) VALUES (%s, %s, %s)", 
                         (user_id, name, rfid_uid))
            connection.commit()
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            print(f"Lỗi: {err}")
            
    return redirect(url_for('show_users'))

@app.route('/delete_user/<int:id>')
def delete_user(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Lỗi: {err}")
        
    return redirect(url_for('show_users'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')