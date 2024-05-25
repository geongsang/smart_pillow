import smbus
import time
import datetime
import RPi.GPIO as g

# ----------------------Linear Actuator----------------------#

center_forward_pin = 17
center_reverse_pin = 18

right_forward_pin = 27
right_reverse_pin = 22

left_forward_pin = 23
left_reverse_pin = 24

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



# ----------------------Linear Actuator----------------------#

# ----------------------Switch----------------------#

reset_sw = 21
up_sw    = 20
down_sw  = 16
auto_sw  = 12


g.setmode(g.BCM)
g.setwarnings(False)

g.setup(reset_sw, g.OUT)
g.setup(up_sw   , g.OUT)
g.setup(down_sw , g.OUT)
g.setup(auto_sw , g.OUT)



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
  reset_value = 1.5
  
  while True:
    
    key_region = input("Insert Key(C, R, L): ")       # load cell
    
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
      else:
        auto_detect, up_detect, down_detect = False, False, False
        lcd_msg_auto(auto_finish_msg)
        time.sleep(1)
        print("Auto Mode Finished")
    else:  
      up_detect, down_detect, reset_detect = False, False, False
    
    if auto_detect != True:
      if center_detect == True:
        if up_detect == True:
          #------------------LCD----------------#
          if center_height < 15:
            center_height += 1
          else:
            center_height = 15
          lcd_msg(center_msg, center_height)
          #------------------LCD----------------#
          
          #------------------------Linear Actuator------------------#
          extend_actuator(center_forward_pin, center_reverse_pin, default_value)
          print("Center Actuator extended")        
          #------------------------Linear Actuator------------------#
          
        elif down_detect == True:

          #------------------LCD----------------#
          if center_height > 0:
            center_height -= 1
          else:
            center_height = 0          
          lcd_msg(center_msg, center_height)
          #------------------LCD----------------#
          
          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, default_value)
          print("Center Actuator retracted")
          #------------------------Linear Actuator------------------#
        
        elif reset_detect == True:
          #------------------LCD----------------#
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        
          time.sleep(1)
          lcd_msg_total(center_height, right_height, left_height)
          #------------------LCD----------------#

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #------------------------Linear Actuator------------------#          

      elif right_detect == True:
        if up_detect == True:

          #------------------LCD----------------#
          if right_height < 15:
            right_height += 1
          else:
            right_height = 15
          lcd_msg(right_msg, right_height)
          #------------------LCD----------------#

          #------------------------Linear Actuator------------------#
          extend_actuator(right_forward_pin, right_reverse_pin, default_value)
          print("Right Actuator extended")
          #------------------------Linear Actuator------------------#

        elif down_detect == True:
        
          #------------------LCD----------------#
          if right_height > 0:
            right_height -= 1
          else:
            right_height = 0
          lcd_msg(right_msg, right_height)
          #------------------LCD----------------#

          #------------------------Linear Actuator------------------#
          retract_actuator(right_forward_pin, right_reverse_pin, default_value)
          print("Right Actuator retracted")
          #------------------------Linear Actuator------------------#
          
        elif reset_detect == True:
          #------------------LCD----------------#
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        
          time.sleep(1)
          lcd_msg_total(center_height, right_height, left_height)
          #------------------LCD----------------#

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #------------------------Linear Actuator------------------#            

      elif left_detect == True:
        if up_detect == True:
          #------------------LCD----------------#
          if left_height < 15:
            left_height += 1
          else:
            left_height = 15
          lcd_msg(left_msg, left_height)
          #------------------LCD----------------#        
        
          #------------------------Linear Actuator------------------#
          extend_actuator(left_forward_pin, left_reverse_pin, default_value)
          print("Left Actuator extended")
          #------------------------Linear Actuator------------------#
        
        elif down_detect == True:
          #------------------LCD----------------#        
          if left_height > 0:
            left_height -= 1
          else:
            left_height = 0
          lcd_msg(left_msg, left_height)
          #------------------LCD----------------#        

          #------------------------Linear Actuator------------------#
          retract_actuator(left_forward_pin, left_reverse_pin, default_value)
          print("Left Actuator retracted")
          #------------------------Linear Actuator------------------#

        elif reset_detect == True:
          #------------------LCD----------------#
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        
          time.sleep(1)
          lcd_msg_total(center_height, right_height, left_height)
          #------------------LCD----------------#

          #------------------------Linear Actuator------------------#          
          retract_actuator(center_forward_pin, center_reverse_pin, reset_value)
          retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
          retract_actuator(left_forward_pin, left_reverse_pin, reset_value)          
          print("Reset Actuator")
          #------------------------Linear Actuator------------------#                
    elif auto_detect == True:
      if center_detect == True:
        #------------------LCD----------------#
        lcd_msg_total(center_height, default_height, default_height)
        #------------------LCD----------------#

        #------------------------Linear Actuator------------------#          
        extend_actuator(center_forward_pin, center_reverse_pin, default_value * center_height)
        retract_actuator(right_forward_pin, right_reverse_pin, reset_value)        
        retract_actuator(left_forward_pin, left_reverse_pin, reset_value)
        #------------------------Linear Actuator------------------#          
                
      elif right_detect == True:
        #------------------LCD----------------#      
        lcd_msg_total(default_height, right_height, default_height)
        #------------------LCD----------------#

        #------------------------Linear Actuator------------------#          
        retract_actuator(center_forward_pin, center_reverse_pin, reset_value)        
        extend_actuator(right_forward_pin, right_reverse_pin, default_value * right_height)
        retract_actuator(left_forward_pin, left_reverse_pin, reset_value)
        #------------------------Linear Actuator------------------#          
        
      elif left_detect == True:
        #------------------LCD----------------#
        lcd_msg_total(default_height, default_height, left_height)
        #------------------LCD----------------#

        #------------------------Linear Actuator------------------#          
        retract_actuator(center_forward_pin, center_reverse_pin, reset_value)        
        retract_actuator(right_forward_pin, right_reverse_pin, reset_value)
        extend_actuator(left_forward_pin, left_reverse_pin, default_value * left_height)
        #------------------------Linear Actuator------------------#          

        
    else:
      lcd_string("ERROR!!        <", LCD_LINE_1)
      lcd_string("ERROR!!        <", LCD_LINE_2)
      time.sleep(1)
      
    reset_detect = False
    key_direction = False
    
if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    

