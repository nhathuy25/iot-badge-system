import requests

address = 'http://192.168.170.52:5000/'
data_to_send = {
	'temperature':22.3,
	'humidity':48.9
}

response = requests.post(f'{address}/send_to_database', data = data_to_send)

print(response.text)
