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
        print("Place Card to register")
        id, text = reader.read()
        print(id)
        cursor.execute("SELECT id FROM users WHERE rfid_uid="+str(id))
        cursor.fetchone()

        if cursor.rowcount >=1:
            print("Overwrite existing user?")
            overwrite=input("Overwrite (Y/N)?")

            if overwrite[0]=='Y' or overwrite[0]=='y':
                turn_green_on()
                print("Overwritting user.")
                time.sleep(1)
                sql_insert="UPDATE users SET name=%s WHERE rfid_uid=%s"
            else:
                continue;
        else:
            sql_insert="INSERT INTO users (name, rfid_uid) VALUES (%s, %s)"

        print("Enter new name")
        new_name=input("Name: ")
        cursor.execute(sql_insert, (new_name,id))
        db.commit()
        turn_green_on()
        print("User "+new_name+"\tSaved")
        time.sleep(2)
        turn_both_off()
finally:
    turn_both_off()
    GPIO.cleanup()

