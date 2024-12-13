#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
from datetime import datetime

address = 'http://192.168.170.52:5000/'

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

def get_passage(id_card):
	response = requests.get(f'{address}/get_passage?ID_CARD={id_card}')
	if response.status_code == 200:
		if response.json():
			print("Passage autorisé !")
		else:
			print("Passage interdit !")
	else:
		print('Erreur lors de la récupération de données')
		
	return response.json()

def send_user(data_user):
	response = requests.post(f'{address}/add_user', data = data_user)


def send_passage(id_card, autorise):
	data_passage = {'ID_CARD': id_card,
		'TIME': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
		"AUTORISE": autorise 
	}
	response = requests.post(f'{address}/add_passage', data = data_passage)

data_user = {'ID_CARD' : 0,
			"NOM":"",
			"PRENOM":""} 	

turn_both_off()

while True:
	turn_both_off()
	writeMode = False
	if (input() == "write"):
		writeMode = True
	if (writeMode == False):
		#Lecture du badge
		try:
			print("Place card to record attendance")
			id, text = reader.read()
			print(id, text)
			autorisation = get_passage(id)
			if autorisation:
				turn_green_on()
			else:
				turn_red_on()
			send_passage(id, autorisation) 
			time.sleep(2)
			turn_both_off()
		finally:
			turn_both_off()

	elif (writeMode == True):
		#Ecriture du badge
		try:
			turn_red_on()
			print("Place Card to register")
			data_user["ID_CARD"], text = reader.read()
			print(id, text)
			time.sleep(2)
			turn_both_off()
			print("Enter new name")
			data_user["NOM"]=input("Name: ")
			print("Enter new firstname")
			data_user["PRENOM"]=input("First name: ")
			turn_green_on()
			print("User "+data_user["NOM"]+" "+data_user["PRENOM"]+" Saved")
			send_user(data_user)
			time.sleep(2)
			turn_both_off()
			writeMode = False
		finally:
			turn_both_off()
