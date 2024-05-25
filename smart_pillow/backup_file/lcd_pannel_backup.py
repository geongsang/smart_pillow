import smbus
import time

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
    #time.sleep(3)

# value

center_msg    = "Center detected<"
right_msg     = "Right  detected<"
left_msg      = "Left   detected<"
height_msg    = "Height: "
reset_msg     = "Reset"
auto_msg      = "Auto Mode"

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
  
  while True:
    key_region = input("Insert Key(C, R, L): ")       # load cell
    key_direction = input("Insert Key(U, D, R, A): ") # switch
    
    
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
    
    elif key_direction == "R":
      print("R")
      reset_detect, up_detect, down_detect = True, False, False
    
    elif key_direction == "A":
      if auto_detect == False:
        auto_detect, up_detect, down_detect = True, False, False
      else:
        auto_detect = False
        
    else:  
      up_detect, down_detect, reset_detect, auto_detect = False, False, False, False
    
    if auto_detect != True:
      if center_detect == True:
        if up_detect == True:
          center_height += 1
          lcd_msg(center_msg, center_height)
        
        elif down_detect == True:
          if center_height > 0:
            center_height -= 1
          else
            center_height = 0  
          lcd_msg(center_msg, center_height)
        
        elif reset_detect == True:
          print("reset")
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        
    
      elif right_detect == True:
        if up_detect == True:
          right_height += 1
          lcd_msg(right_msg, right_height)
        
        elif down_detect == True:
          if right_height > 0:
            right_height -= 1
          else
            right_height = 0
          lcd_msg(right_msg, right_height)

        elif reset_detect == True:
          print("reset")
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        

      elif left_detect == True:
        if up_detect == True:
          left_height += 1
          lcd_msg(left_msg, left_height)
        
        elif down_detect == True:
          if left_height > 0:
            left_height -= 1
          else
            left_height = 0
          lcd_msg(left_msg, left_height)
        
        elif reset_detect == True:
          print("reset")
          center_height, right_height, left_height = 0, 0, 0
          lcd_msg(reset_msg, default_height)        
        
    elif auto_detect == True:
      if center_detect == True:
        
        lcd_msg(center_msg, center_height)
        time.sleep(2)
        lcd_msg(right_msg, default_height)
        time.sleep(2)
        lcd_msg(left_msg, default_height)
                
      elif right_detect == True:
        lcd_msg(center_msg, default_height)
        time.sleep(2)
        lcd_msg(right_msg, right_height)
        time.sleep(2)
        lcd_msg(left_msg, default_height)
        
      elif left_detect == True:
        lcd_msg(center_msg, default_height)
        time.sleep(2)
        lcd_msg(right_msg, default_height)
        time.sleep(2)
        lcd_msg(left_msg, left_height)
        
    else:
      lcd_string("Nothing        <", LCD_LINE_1)
      lcd_string("Nothing        <", LCD_LINE_2)
      time.sleep(3)
      
    reset_detect = False
    
if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    

