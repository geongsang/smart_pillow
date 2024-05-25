import smbus
import time
import datetime
import RPi.GPIO as g
import paho.mqtt.client as mqtt
import sys
import uuid

server = "44.205.81.15"
topic = "id/sleep/commands"

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected to MQTT brocker")
		client.subscribe(topic, qos = 0)
	else:
		print(f"Connection failed with result code {rc}")
		
def on_subscribe(client, userdata, mid, granted_qos):
	print(f"Subscribed to topic {topic}")
	
def on_message(client, userdata, msg):
	print("message went")
	if topic == msg.topic:
		test = msg.payload.decode('utf-8')
		print(f"Received message: {test}")
	else:
		print("error")

client = mqtt.Client(client_id=str(uuid.uuid4()))

client.on_connect = on_connect
client.on_subscribe = on_subscribe

client.on_message = on_message
client.connect(server, 1883, 60)

client.loop_forever()
