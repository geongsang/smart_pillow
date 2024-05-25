import smbus
import time
import datetime
import RPi.GPIO as g
import paho.mqtt.client as mqtt
import sys
import uuid

# ------------------MQTT Publish to Server----------------------#

# MQTT broker information
broker_address = "44.205.81.15"
broker_port = 1883
pub_topic = "id/sleep/user_length_pillow_height"
sub_command_topic = "id/sleep/commands"
sub_user_data_topic = "id/sleep/linear/request_height"
sub_return_height_topic = "id/sleep/linear/return_height_count"

sub_text = None
sub_user_data_text = None
sub_return_height_count_text = None
recommend_height_flag = None

def on_connect(client, userdata, flags, rc):
  if rc == 0:
    print("Connected to MQTT brocker")
    client.subscribe(sub_command_topic, qos = 0)
    client.subscribe(sub_user_data_topic, qos = 0)
    client.subscribe(sub_return_height_topic, qos = 0)
    
  else:
    print(f"Connection failed with result code {rc}")
		

def on_publish(client, userdata, mid):
  print("Message sended successful")

def on_subscribe(client, userdata, mid, granted_qos):
  print(f"Subscribed to topic {sub_command_topic}")
  print(f"Subscribed to topic {sub_user_data_topic}")
  print(f"Subscribed to topic {sub_return_height_topic}")


def on_message(client, userdata, msg):
  global sub_text
  global sub_user_data_text
  global sub_return_height_count_text
  global recommend_height_flag
  
  if sub_command_topic == msg.topic:
    sub_text = msg.payload.decode('utf-8')
    print(f"Received message: {sub_text}")
    
  elif sub_user_data_topic == msg.topic:
    sub_user_data_text = msg.payload.decode('utf-8')
    recommend_height_flag = 1
    print(f"Received message: {sub_user_data_text}")
  
  elif sub_return_height_topic == msg.topic:
    sub_return_height_count_text = msg.payload.decode('utf-8')
    
    print(f"Received message: {sub_return_height_count_text}")
  
  else:
    print("error")
  
def initialize():
  global sub_text
  sub_text = None

# MQTT client generation
client = mqtt.Client(client_id=str(uuid.uuid4()))
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_connect = on_connect

# Connect broker
client.connect(broker_address, broker_port, keepalive = 60)


# --------------------------------------------------------------#



# ---------------------------Load Cell--------------------------#

EMULATE_HX711=False

referenceUnit = 1

if not EMULATE_HX711:
	import RPi.GPIO as GPIO
	from hx711 import HX711
else:
	from emulated_hx711 import HX711

def cleanAndExit():
	print("Cleaning...")

	if not EMULATE_HX711:
		GPIO.cleanup()
        
		print("Bye!")
		sys.exit()

GPIO.setwarnings(False)

hx_center = HX711(17, 18)
hx_right = HX711(23, 24)
hx_left = HX711(19, 26)


hx_center.set_reading_format("MSB", "MSB")
hx_right.set_reading_format("MSB", "MSB")
hx_left.set_reading_format("MSB", "MSB")

hx_center.set_reference_unit(113)
hx_center.set_reference_unit(referenceUnit)

hx_right.set_reference_unit(113)
hx_right.set_reference_unit(referenceUnit)

hx_left.set_reference_unit(113)
hx_left.set_reference_unit(referenceUnit)

hx_center.reset()
hx_center.tare()

print("Center Tare done! Add weight now...")

hx_right.reset()
hx_right.tare()

print("Right Tare done! Add weight now...")

hx_left.reset()
hx_left.tare()

print("Left Tare done! Add weight now...")

def val_center():
	val_center = hx_center.get_weight(5)
	hx_center.power_down()
	hx_center.power_up()
	
	return val_center
	
def val_right():
	val_right = hx_right.get_weight(5)
	hx_right.power_down()
	hx_right.power_up()

	return val_right

def val_left():
	val_left = hx_left.get_weight(5)
	hx_left.power_down()
	hx_left.power_up()
	
	return val_left
	
# ------------------------------------------------------------- #

# ----------------------Linear Actuator----------------------#

center_forward_pin = 5
center_reverse_pin = 25

right_forward_pin = 27
right_reverse_pin = 22

left_forward_pin = 6
left_reverse_pin = 13

g.setmode(g.BCM)
g.setwarnings(False)

g.setup(center_forward_pin, g.OUT)
g.setup(center_reverse_pin, g.OUT)
g.setup(right_forward_pin, g.OUT)
g.setup(right_reverse_pin, g.OUT)
g.setup(left_forward_pin, g.OUT)
g.setup(left_reverse_pin, g.OUT)

# time.sleep(0.1) 0.1s per 2mm


def extend_actuator(forward_pin, reverse_pin, value):
	g.output(forward_pin, g.HIGH)
	g.output(reverse_pin, g.LOW)
	time.sleep(value)
	g.output(forward_pin, g.LOW)

def retract_actuator(forward_pin, reverse_pin, value):
	g.output(reverse_pin, g.HIGH)
	g.output(forward_pin, g.LOW)
	time.sleep(value)
	g.output(reverse_pin, g.LOW)


# -----------------------------------------------------------#




# value

center_msg      = "Center detected<"
right_msg       = "Right  detected<"
left_msg        = "Left   detected<"
height_msg      = "Height: "
reset_msg       = "Reset"
auto_start_msg  = "    Started     "
auto_finish_msg = "    Finished    "

def main():
  # Main program block
  global recommend_height_flag
  
  center_height, right_height, left_height, default_height = 0, 0, 0, 0
  center_detect = False
  right_detect  = False
  left_detect   = False
  up_detect     = False
  down_detect   = False
  reset_detect  = False
  auto_detect   = False
  key_direction = False
  default_value = 0.1
  reset_value = 4
  temp_value = 0
  key_region = 0
  user_data = []
  
  while True:
    client.loop_start()
    print(sub_text)
    center_val = val_center()
    right_val = val_right()
    left_val = val_left()
    total_val = [center_val, right_val, left_val]
    print(str(center_val) + " | " + str(right_val) + " | " + str(left_val))
    

    #----------------------------------Init-------------------------------------#
    if (recommend_height_flag) and (sub_return_height_count_text):
      
      temp_data_set = str(sub_return_height_count_text).split(":")
      center_height = int(temp_data_set[0])
      right_height = int(temp_data_set[1])
      left_height = int(temp_data_set[2])
      
      extend_actuator(center_forward_pin, center_reverse_pin, default_value * center_height)
      extend_actuator(right_forward_pin, right_reverse_pin, default_value * right_height)
      extend_actuator(left_forward_pin, left_reverse_pin, default_value * left_height)          
      print("Init Actuator")
      recommend_height_flag = 0

    #----------------------------------Detect-------------------------------------#
    
    if (max(total_val) == center_val) and (center_val > 100000):
      key_region = "C"
      print("Center detected")
    elif (max(total_val) == right_val) and (right_val > 100000):
      key_region = "R"
      print("Right detected")
    elif max(total_val) == left_val and (left_val > 100000):
      key_region = "L"
      print("Left detected")
    else:
      pass
    #----------------------------------Switch-------------------------------------#
    start_time = datetime.datetime.now()
    seconds_to_run = 2
    while (datetime.datetime.now() - start_time).seconds < seconds_to_run:
      if sub_text == "reset":
        print("Actuator reset Key")
        key_direction = "Reset"
        initialize()
        break
      elif sub_text == "up":
        print("Actuator up Key")
        key_direction = "U"
        initialize() 
        break
      elif sub_text == "down":
        print("Actuator down Key")
        key_direction = "D"
        initialize()
        break
      elif sub_text == "modified_confirm":
        print("Actuator modified auto Key")
        key_direction = "M_A"
        initialize()
        break
      elif sub_text == "auto_confirm":
        print("Actuator auto Key")
        key_direction = "A"
        initialize()
        break
      
    if key_region == "C":
      center_detect, right_detect, left_detect = True, False, False
      
    elif key_region == "R":
      center_detect, right_detect, left_detect = False, True, False
      
    elif key_region == "L":
      center_detect, right_detect, left_detect = False, False, True
      
    else:
      center_detect, right_detect, left_detect = False, False, False
    
    if key_direction == "U":
      up_detect, down_detect = True, False
      
    elif key_direction == "D":
      up_detect, down_detect = False, True
    
    elif key_direction == "Reset":
      reset_detect, up_detect, down_detect = True, False, False
    
    
    
    elif key_direction == "A":
      if auto_detect == False:
        auto_detect, up_detect, down_detect = True, False, False
        temp_data_set = str(sub_return_height_count_text).split(":")
        center_height = int(temp_data_set[1])
        left_height = int(temp_data_set[0])
        right_height = int(temp_data_set[2])    
        print(center_height)
        print(right_height)
        print(left_height)
        init_flag = True
      
      else:
        auto_detect, up_detect, down_detect = False, False, False
        center_height, right_height, left_height = 0, 0, 0


        retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
        retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
        retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
        print("Reset Actuator")


        temp_value = 0
        print("Auto Mode Finished")

    elif key_direction == "M_A":
      if auto_detect == False:
        auto_detect, up_detect, down_detect = True, False, False
        print("Modified Auto Mode Started")
        # Initial Flag
        init_flag = True
        
        # Data to send
        data_to_send = str(center_height) + ":" + str(right_height) + ":" + str(left_height) + ":" + str(sub_user_data_text)
        
        # Message send
        result = client.publish(pub_topic, payload = data_to_send, qos = 0)
        
        print(sub_return_height_count_text)

	
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
          print("MQTT Message sended successful")
        else:
          print("MQTT Message send was failed. Error Code:", result.rc)
        
        # Connection end
        client.disconnect()
        
      else:
        auto_detect, up_detect, down_detect = False, False, False
        
        #------------------------Linear Actuator------------------#          
        retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
        retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
        retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
        print("Reset Actuator")
        #---------------------------------------------------------#       
    
        # Connect broker
        client.connect(broker_address, broker_port, keepalive = 60)
        
        
        temp_value = 0
        print("Auto Mode Finished")
    else:  
      up_detect, down_detect, reset_detect = False, False, False
    #-----------------------------------------------------------------------------#

    if auto_detect != True:
      if center_detect == True:
        if up_detect == True:

          #------------------------Linear Actuator------------------#
          extend_actuator(center_forward_pin, center_reverse_pin, default_value)
          print("Center Actuator extended")        
          #---------------------------------------------------------#
          if center_height < 15:
            center_height += 1
          else:
            center_height = 15
        
        elif down_detect == True:

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, default_value)
          print("Center Actuator retracted")
          #---------------------------------------------------------#
          if center_height > 0:
            center_height -= 1
          else:
            center_height = 0


        elif reset_detect == True:

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #---------------------------------------------------------#          
          center_height, right_height, left_height = 0, 0, 0

      elif right_detect == True:
        if up_detect == True:

          #------------------------Linear Actuator------------------#
          extend_actuator(right_forward_pin, right_reverse_pin, default_value)
          print("Right Actuator extended")
          #---------------------------------------------------------#
          if right_height < 15:
            right_height += 1
          else:
            right_height = 15

        elif down_detect == True:

          #------------------------Linear Actuator------------------#
          retract_actuator(right_forward_pin, right_reverse_pin, default_value)
          print("Right Actuator retracted")
          #---------------------------------------------------------#
          if right_height > 0:
            right_height -= 1
          else:
            right_height = 0


        elif reset_detect == True:

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #---------------------------------------------------------#            
          center_height, right_height, left_height = 0, 0, 0

      elif left_detect == True:
        if up_detect == True:
        
          #------------------------Linear Actuator------------------#
          extend_actuator(left_forward_pin, left_reverse_pin, default_value)
          print("Left Actuator extended")
          #---------------------------------------------------------#
          if left_height < 15:
            left_height += 1
          else:
            left_height = 15

        elif down_detect == True:

          #------------------------Linear Actuator------------------#
          retract_actuator(left_forward_pin, left_reverse_pin, default_value)
          print("Left Actuator retracted")
          #---------------------------------------------------------#
          if left_height > 0:
            left_height -= 1
          else:
            left_height = 0

        elif reset_detect == True:

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #---------------------------------------------------------#                
          center_height, right_height, left_height = 0, 0, 0

    elif auto_detect == True:
      if center_detect == True:

        # initial flag work at first time
        if init_flag:
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)        
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)
          init_flag = False

        else:  
          # Compare temp value message
          if temp_value != "Temp Center":
            #------------------------Linear Actuator------------------#          
            extend_actuator(center_forward_pin, center_reverse_pin, default_value * center_height)
            retract_actuator(right_forward_pin, right_reverse_pin, reset_value)        
            retract_actuator(left_forward_pin, left_reverse_pin, reset_value)
            #---------------------------------------------------------#          
          
        temp_value = "Temp Center"
              
      elif right_detect == True:
        
        # initial flag work at first time
        if init_flag:
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)        
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)
          init_flag = False
        else:
          # Compare temp value message
          if temp_value != "Temp Right":
            #------------------------Linear Actuator------------------#          
            retract_actuator(center_forward_pin, center_reverse_pin, reset_value)        
            extend_actuator(right_forward_pin, right_reverse_pin, default_value * right_height)
            retract_actuator(left_forward_pin, left_reverse_pin, reset_value)
            #---------------------------------------------------------#          
          
        temp_value = "Temp Right"

      elif left_detect == True:

        # initial flag work at first time        
        if init_flag:
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)        
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          init_flag = False
        else:
          # Compare temp value message
          if temp_value != "Temp Left":
            #------------------------Linear Actuator------------------#          
            retract_actuator(center_forward_pin, center_reverse_pin, reset_value)        
            retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
            extend_actuator(left_forward_pin, left_reverse_pin, default_value * left_height)
            #---------------------------------------------------------#          

        temp_value = "Temp Left"
        
    else:
      print("error")
      
    reset_detect = False
    key_direction = False
    
if __name__ == '__main__':

  try:
    main()
  except (KeyboardInterrupt, SystemExit):
    # Connection end
    client.disconnect()
    cleanAndExit()
    pass
    
