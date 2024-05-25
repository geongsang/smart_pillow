import smbus
import time
import datetime
import RPi.GPIO as g
import paho.mqtt.client as mqtt
import sys
# ------------------MQTT Publish to Server----------------------#

# MQTT broker information
broker_address = "44.205.81.15"
broker_port = 1883
topic = "id/sleep/linear/height"

def on_publish(client, userdata, mid):
  print("Message sended successful")

# MQTT client generation
client = mqtt.Client()
client.on_publish = on_publish

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


# ----------------------Switch----------------------#

reset_sw = 21 #red
up_sw    = 20 #yellow
down_sw  = 16 #green
auto_sw  = 12 #blue


g.setmode(g.BCM)
g.setwarnings(False)

g.setup(reset_sw, g.OUT)
g.setup(up_sw   , g.OUT)
g.setup(down_sw , g.OUT)
g.setup(auto_sw , g.OUT)

# --------------------------------------------------#


# ----------------------I2C-------------------------#
# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_msg(region_msg, height_value):
    lcd_string(region_msg, LCD_LINE_1)
    lcd_string(height_msg + str(height_value), LCD_LINE_2)
    
def lcd_msg_total(a, b, c):    
    lcd_string("Total Height", LCD_LINE_1)
    lcd_string("C: " + str(a) + "R: " + str(b) + "L: " + str(c), LCD_LINE_2)

def lcd_msg_auto(msg):
    lcd_string("    Auto Mode   ", LCD_LINE_1)
    lcd_string(msg, LCD_LINE_2)
# --------------------------------------------------#


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
  
  # Initialise display
  lcd_init()
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
  reset_value = 2
  temp_value = 0
  key_region = 0
  while True:
    
    center_val = val_center()
    right_val = val_right()
    #right_val = 0
    left_val = val_left()
    
    total_val = [center_val, right_val, left_val]
    print(str(center_val) + " | " + str(right_val) + " | " + str(left_val))
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
      if g.input(reset_sw) == 1:
        print("Actuator reset Key")
        key_direction = "Reset"
        break
      elif g.input(up_sw) == 1:
        print("Actuator up Key")
        key_direction = "U"
        break
      elif g.input(down_sw) == 1:
        print("Actuator down Key")
        key_direction = "D"
        break
      elif g.input(auto_sw) == 1:
        print("Actuator auto Key")
        key_direction = "A"
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
        lcd_msg_auto(auto_start_msg)
        time.sleep(1)
        print("Auto Mode Started")
        # Initial Flag
        init_flag = True
        
        # Data to send
        data_to_send = str(center_height) + ":" + str(right_height) + ":" + str(left_height)
        
        # Message send
        result = client.publish(topic, payload = data_to_send, qos = 0)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
          print("MQTT Message sended successful")
        else:
          print("MQTT Message send was failed. Error Code:", result.rc)
        
        # Connection end
        client.disconnect()
        
      else:
        auto_detect, up_detect, down_detect = False, False, False
        
        #------------------LCD----------------#
        center_height, right_height, left_height = 0, 0, 0
        lcd_msg(reset_msg, default_height)        
        time.sleep(1)
        lcd_msg_total(center_height, right_height, left_height)
        #-------------------------------------#

        #------------------------Linear Actuator------------------#          
        retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
        retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
        retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
        print("Reset Actuator")
        #---------------------------------------------------------#       
    
        # Connect broker
        client.connect(broker_address, broker_port, keepalive = 60)
        
        lcd_msg_auto(auto_finish_msg)
        time.sleep(1)
        
        temp_value = 0
        print("Auto Mode Finished")
    else:  
      up_detect, down_detect, reset_detect = False, False, False
    #-----------------------------------------------------------------------------#

    if auto_detect != True:
      if center_detect == True:
        if up_detect == True:
          #------------------LCD----------------#
          if center_height < 6:
            center_height += 1
          else:
            center_height = 6
          lcd_msg(center_msg, center_height)
          #-------------------------------------#
          
          #------------------------Linear Actuator------------------#
          extend_actuator(center_forward_pin, center_reverse_pin, default_value)
          print("Center Actuator extended")        
          #---------------------------------------------------------#
          
        elif down_detect == True:

          #------------------LCD----------------#
          if center_height > 0:
            center_height -= 1
          else:
            center_height = 0          
          lcd_msg(center_msg, center_height)
          #-------------------------------------#
          
          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, default_value)
          print("Center Actuator retracted")
          #---------------------------------------------------------#
        
        elif reset_detect == True:
          #------------------LCD----------------#
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        
          time.sleep(1)
          lcd_msg_total(center_height, right_height, left_height)
          #-------------------------------------#

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #---------------------------------------------------------#          

      elif right_detect == True:
        if up_detect == True:

          #------------------LCD----------------#
          if right_height < 19:
            right_height += 1
          else:
            right_height = 19
          lcd_msg(right_msg, right_height)
          #-------------------------------------#

          #------------------------Linear Actuator------------------#
          extend_actuator(right_forward_pin, right_reverse_pin, default_value)
          print("Right Actuator extended")
          #---------------------------------------------------------#

        elif down_detect == True:
        
          #------------------LCD----------------#
          if right_height > 0:
            right_height -= 1
          else:
            right_height = 0
          lcd_msg(right_msg, right_height)
          #-------------------------------------#

          #------------------------Linear Actuator------------------#
          retract_actuator(right_forward_pin, right_reverse_pin, default_value)
          print("Right Actuator retracted")
          #---------------------------------------------------------#
          
        elif reset_detect == True:
          #------------------LCD----------------#
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        
          time.sleep(1)
          lcd_msg_total(center_height, right_height, left_height)
          #-------------------------------------#

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #---------------------------------------------------------#            

      elif left_detect == True:
        if up_detect == True:
          #------------------LCD----------------#
          if left_height < 19:
            left_height += 1
          else:
            left_height = 19
          lcd_msg(left_msg, left_height)
          #-------------------------------------#        
        
          #------------------------Linear Actuator------------------#
          extend_actuator(left_forward_pin, left_reverse_pin, default_value)
          print("Left Actuator extended")
          #---------------------------------------------------------#
        
        elif down_detect == True:
          #------------------LCD----------------#        
          if left_height > 0:
            left_height -= 1
          else:
            left_height = 0
          lcd_msg(left_msg, left_height)
          #-------------------------------------#        

          #------------------------Linear Actuator------------------#
          retract_actuator(left_forward_pin, left_reverse_pin, default_value)
          print("Left Actuator retracted")
          #---------------------------------------------------------#

        elif reset_detect == True:
          #------------------LCD----------------#
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        
          time.sleep(1)
          lcd_msg_total(center_height, right_height, left_height)
          #-------------------------------------#

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #---------------------------------------------------------#                
    elif auto_detect == True:
      if center_detect == True:
        #------------------LCD----------------#
        lcd_msg_total(center_height, default_height, default_height)
        #-------------------------------------#
        
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
        #------------------LCD----------------#      
        lcd_msg_total(default_height, right_height, default_height)
        #-------------------------------------#
        
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
        #------------------LCD----------------#
        lcd_msg_total(default_height, default_height, left_height)
        #-------------------------------------#

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
      lcd_string("ERROR!!        <", LCD_LINE_1)
      lcd_string("ERROR!!        <", LCD_LINE_2)
      time.sleep(1)
      
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
  finally:
    lcd_byte(0x01, LCD_CMD)

