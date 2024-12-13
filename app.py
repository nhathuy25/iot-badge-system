from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import mysql.connector
import socket
import os
import netifaces
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
app = Flask(__name__)

def get_ip_adress():
    try:
        if 'wlan0' in netifaces.interfaces():
            addrs = netifaces.ifaddresses('wlan0')
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]['addr']
        
        if 'eth0' in netifaces.interfaces():
            addrs = netifaces.ifaddresses('eth0')
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]['addr']
            
        return "No LAN found"
    except Exception as e:
        print(f"error: {e}")
        return " could not get ip"
reader=SimpleMFRC522()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

LED_RED = 3
LED_GREEN = 5

#définit la fonction permettant d'allumer une led
def turn_led_on(led):
    GPIO.setup(led, GPIO.OUT) #active le contrôle du GPIO
    GPIO.output(led, GPIO.HIGH) #allume la led
    
#définit la fonction permettant d'éteindre une led
def turn_led_off(led):
    GPIO.setup(led, GPIO.OUT) #active le contrôle du GPIO
    GPIO.output(led, GPIO.LOW) #éteind la led
    
def turn_red_on():
    turn_led_off(LED_GREEN)
    turn_led_on(LED_RED)
    
def turn_green_on():
    turn_led_on(LED_GREEN)
    turn_led_off(LED_RED)
    
def turn_both_off():
    turn_led_off(LED_GREEN)
    turn_led_off(LED_RED)


turn_both_off()
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

@app.route('/members')
def show_members():
    return render_template('members.html')

@app.route('/attendance')
def show_attendance():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Lấy tham số filter từ URL
    user_id = request.args.get('user_id')
    date = request.args.get('date')
    status = request.args.get('status')
    
    # Query cơ bản
    query = '''
        SELECT a.id, a.user_id, a.image_path, a.timestamp, u.name, u.rfid_uid
        FROM attendance a 
        LEFT JOIN users u ON a.user_id = u.id
        WHERE 1=1
    '''
    params = []
    
    # Thêm các điều kiện filter
    if user_id:
        query += " AND a.user_id = %s"
        params.append(user_id)
    if date:
        query += " AND DATE(a.timestamp) = %s"
        params.append(date)
    if status:
        if status == 'authorized':
            query += " AND u.id IS NOT NULL"
        elif status == 'unauthorized':
            query += " AND u.id IS NULL"
            
    query += " ORDER BY a.timestamp DESC"
    
    # Thực hiện query
    cursor.execute(query, params)
    attendance_records = cursor.fetchall()
    
    # Lấy danh sách users cho dropdown
    cursor.execute('SELECT id, name FROM users')
    users = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('attendance.html', 
                         records=attendance_records, 
                         users=users,
                         selected_user=user_id,
                         selected_date=date,
                         selected_status=status)

@app.route('/images/<path:image_path>')
def serve_image(image_path):
    try:
        file_path = f"/home/admin/Projet_IOT_ACAD_2024/Capture_images/{image_path}"
        if os.path.exists(file_path):
            return send_file(file_path)
        return "Image not found", 404
    except Exception as e:
        print(f"Error serving image: {e}")
        return "Error serving image", 500

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
            print(f"Error: {err}")
            
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
        print(f"Error: {err}")
        
    return redirect(url_for('show_users'))
@app.route('/register_rfid', methods=['GET'])
def register_rfid():
    try:
        print("Waiting for card...")
        id, text = reader.read()
        turn_green_on()
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Kiểm tra RFID đã tồn tại chưa
        cursor.execute("SELECT * FROM users WHERE rfid_uid = %s", (str(id),))
        existing_user = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if existing_user:
            return jsonify({
                'status': 'exists',
                'rfid': str(id),
                'user': existing_user
            })
        else:
            return jsonify({
                'status': 'new',
                'rfid': str(id)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/update_user', methods=['POST'])
def update_user():
    if request.method == 'POST':
        user_id = request.form['id']
        name = request.form['name']
        rfid_uid = request.form['rfid_uid']
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("UPDATE users SET name=%s, rfid_uid=%s WHERE id=%s", 
                         (name, rfid_uid, user_id))
            connection.commit()
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            
    return redirect(url_for('show_users'))

if __name__ == '__main__':
    ip = get_ip_adress()
    print(f"\nLocal IP Adress: http://{ip}:5000")
    print(f"\nLocalhost : http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0')