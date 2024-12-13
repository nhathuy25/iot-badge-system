#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector
import logging

#importation pour la Camera
from picamera import PiCamera
from time import sleep
from datetime import datetime

camera = PiCamera()
camera.resolution = (1280, 720)
camera.framerate = 30
camera.vflip = True #Inverser la camera

db=mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="attendancesystem"
)

cursor = db.cursor()
reader = SimpleMFRC522()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# GPIO.cleanup()

LED_RED = 3
LED_GREEN = 5

#définit la fonction permettant d'allumer une led
def turn_led_on(led):
    GPIO.setup(led, GPIO.OUT) #active le contrôle du GPIO
    GPIO.output(led, GPIO.HIGH) #allume la led("/home/admin/Projet_IOT_ACAD_2024/Capture_images")

    
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

def take_photo_and_save(user_id):
    try:
        #Generate a filename using current timestamp to save differents images
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'/home/admin/Projet_IOT_ACAD_2024/Capture_images/user_{user_id}_{timestamp}.jpg'
        camera.start_preview()
        time.sleep(1)
        #Capture image
        print("Smile!!! Let's take a photo for security")
        camera.capture(filename)
        return filename
        
    except Exception as e:
        print(f"error: {str(e)}")
        return None
    finally:
        camera.stop_preview()

# Function to save the last access of the user    
def save_last_attendance(user_id):
    try:
        # Fetch the last attendance record for the user
        cursor.execute("SELECT * FROM attendance WHERE user_id=%s ORDER BY id DESC LIMIT 1", (user_id,))
        result = cursor.fetchone()
        
        if cursor.rowcount >= 1:
            # Update the last_access in the attendance table
            cursor.execute("UPDATE attendance SET last_access=NOW() WHERE id=%s", (result[0],))
            
            # Update the last_attendance in the users table
            cursor.execute("UPDATE users SET last_attendance=NOW() WHERE id=%s", (user_id,))
            
            # Commit the transaction
            db.commit()
    except Exception as e:
        logging.error(f"Error updating last attendance: {str(e)}")
        db.rollback()


try:
    while True:
        print("Place card to record attendance")
        id, text = reader.read()
        cursor.execute("Select * FROM users WHERE rfid_uid="+str(id))
        # Assign the badge readed to variable 'result'
        result=cursor.fetchone()
        if cursor.rowcount >= 1:
            turn_green_on()
            print("Welcome "+result[1]+" - ID n°"+str(result[0]))
            # Open the camera and save the access information
            image_path = take_photo_and_save(result[0])
            cursor.execute("INSERT INTO attendance (user_id, image_path) VALUES (%s, %s)",(result[0], image_path))
            
            db.commit()
        else:
            turn_red_on()
            print("TAG n°"+str(id)+" - User does not exist.")
        time.sleep(2)
        turn_both_off()
finally:
    turn_both_off()
    GPIO.cleanup()

