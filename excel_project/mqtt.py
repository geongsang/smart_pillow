import paho.mqtt.client as mqtt

# MQTT broker information
broker_address = "54.211.29.133"
broker_port = 1883
topic = "your/mqtt/topic"

# data to send
data_to_send = "Hello, MQTT!"

def on_publish(client, userdata, mid):
  print("Message sended successful")


  
# MQTT client generation
client = mqtt.Client()
client.on_publish = on_publish

# Connect broker
client.connect(broker_address, broker_port, keepalive = 60)

# Message send
result = client.publish(topic, payload = data_to_send, qos = 1)



if result.rc == mqtt.MQTT_ERR_SUCCESS:
  print("MQTT Message sended successful")
else:
  print("MQTT Message send was failed. Error Code:", result.rc)
  
# Connection end
client.disconnect()

