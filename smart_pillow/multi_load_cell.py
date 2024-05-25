#! /usr/bin/python2

import time
import sys
import RPi.GPIO as g


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



# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
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


# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

def val_center_print():
	val_center = hx_center.get_weight(5)
	print("Center: ", val_center)
	if val_center >= 100000:
		center_detect = True
	else:
		center_detect = False	
	hx_center.power_down()
	hx_center.power_up()

def val_right_print():
	val_right = hx_right.get_weight(5)
	print("Right: ", val_right)
	if val_right >= 100000:
		right_detect = True
	else:
		right_detect = False
	hx_right.power_down()
	hx_right.power_up()

def val_left_print():
	val_left = hx_left.get_weight(5)
	print("Left: ", val_left)
	if val_left >= 100000:
		left_detect = True
	else:
		left_detect = False
	hx_left.power_down()
	hx_left.power_up()

while True:
	try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
        
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string
        
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
		#val_center_print()
		time.sleep(0.1)
		#val_right_print()
		time.sleep(0.1)
		val_left_print()
		time.sleep(0.1)


	except (KeyboardInterrupt, SystemExit):
		cleanAndExit()

# try load cell test

