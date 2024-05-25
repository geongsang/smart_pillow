import RPi.GPIO as g
import time
import sys

# load cell

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


hx = HX711(20, 16)


hx.set_reading_format("MSB", "MSB")

hx.set_reference_unit(113)
hx.set_reference_unit(referenceUnit)

hx.reset()

hx.tare()

print("Tare done! Add weight now...")



# linear actuator

forward_pin = 17
reverse_pin = 18

g.setmode(g.BCM)
g.setwarnings(False)

g.setup(forward_pin, g.OUT)
g.setup(reverse_pin, g.OUT)


def extend_actuator():
	g.output(forward_pin, g.HIGH)
	g.output(reverse_pin, g.LOW)
	time.sleep(1)
	g.output(forward_pin, g.LOW)

def retract_actuator():
	g.output(reverse_pin, g.HIGH)
	g.output(forward_pin, g.LOW)
	time.sleep(1)
	g.output(reverse_pin, g.LOW)

		
		
while True:
    try:
        val = hx.get_weight(5)
        print(val)
	
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)
        
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
        
    if(val >= 5000):
    	extend_actuator()
    	print("Actuator extended")
    	time.sleep(2)
    else:
    	retract_actuator()
    	print("Actuator retracted")
    	time.sleep(2)
    	
   
