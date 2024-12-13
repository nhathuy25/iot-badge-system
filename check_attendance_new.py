#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector
from picamera import PiCamera
from time import sleep

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="attendancesystem"
)

cursor = db.cursor()
reader = SimpleMFRC522()
camera = PiCamera()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

LED_RED = 3
LED_GREEN = 5

def turn_led_on(led):
    GPIO.setup(led, GPIO.OUT)
    GPIO.output(led, GPIO.HIGH)
    
def turn_led_off(led):
    GPIO.setup(led, GPIO.OUT)
    GPIO.output(led, GPIO.LOW)
    
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

try:
    while True:
        print("Place card to record attendance")
        rfid_id, text = reader.read()
        
        # Check if user exists
        cursor.execute("Select * FROM users WHERE rfid_uid=%s", (str(rfid_id),))
        result = cursor.fetchone()
        
        if result:
            turn_green_on()
            user_id = result[0]
            print(f"Welcome {result[1]} - ID n°{user_id}")
        else:
            turn_red_on()
            user_id = None
            print(f"TAG n°{rfid_id} - User does not exist.")

        # Tạo tên file với timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        user_prefix = f"user_{user_id if user_id else rfid_id}"
        image_path = f"/home/admin/Projet_IOT_ACAD_2024/Capture_images/{user_prefix}_{timestamp}.jpg"
        
        # Chụp ảnh
        camera.start_preview(alpha=192)
        sleep(1)
        camera.capture(image_path)
        camera.stop_preview()
        
        # Insert record với user_id (có thể null), image_path và timestamp tự động
        cursor.execute("INSERT INTO attendance (user_id, image_path, rfid_uid) VALUES (%s, %s, %s)",
                      (user_id, image_path, str(rfid_id)))
        db.commit()
        
        time.sleep(2)
        turn_both_off()

finally:
    turn_both_off()
    GPIO.cleanup()
    camera.close()