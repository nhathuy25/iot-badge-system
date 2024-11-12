#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="attendancesystem"
)

cursor=db.cursor()
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

try:
    while True:
        turn_red_on()
        print("Place Card to delete user")
        id, text = reader.read()
        cursor.execute("SELECT id FROM users WHERE rfid_uid="+str(id))
        idu=cursor.fetchone()
        print(idu)
        
        print("Delete existing user?")
        delete=input("Delete (Y/N)?")

        if delete[0]=='Y' or delete[0]=='y':
            turn_green_on()
            print("Deleting user.")
            time.sleep(1)
            sql_delete="DELETE FROM attendance WHERE user_id="+str(idu[0])
            cursor.execute(sql_delete)
            cursor.fetchone()
            sql_delete="DELETE FROM users WHERE id="+str(idu[0])
            cursor.execute(sql_delete)
            cursor.fetchone()
            db.commit()
            turn_green_on()
            print("User deleted")
            time.sleep(2)               
            turn_both_off()
        else:
            continue;

finally:
    turn_both_off()
    GPIO.cleanup()


