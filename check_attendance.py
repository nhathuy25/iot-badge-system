#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector

#importation pour la Camera
from picamera import PiCamera
from time import sleep

'''
#Fonction test capture d'image du camera
camera = PiCamera()
camera.start_preview(alpha=192)
sleep(1)
camera.capture("/home/admin/Projet_IOT_ACAD_2024/Capture_images")
camera.stop_preview()
'''
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

try:
    while True:
        print("Place card to record attendance")
        id, text = reader.read()
        cursor.execute("Select * FROM users WHERE rfid_uid="+str(id))
        result=cursor.fetchone()
        if cursor.rowcount >= 1:
            turn_green_on()
            print("Welcome "+result[1]+" - ID n°"+str(result[0]))
            cursor.execute("INSERT INTO attendance (user_id) VALUES (%s)",(result[0],))
            db.commit()
        else:
            turn_red_on()
            print("TAG n°"+str(id)+" - User does not exist.")
        time.sleep(2)
        turn_both_off()
finally:
    turn_both_off()
    GPIO.cleanup()

