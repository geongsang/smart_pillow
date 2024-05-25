import RPi.GPIO as g
import time

forward_pin = 17
reverse_pin = 18

height = float(input())

g.setmode(g.BCM)
g.setwarnings(False)

g.setup(forward_pin, g.OUT)
g.setup(reverse_pin, g.OUT)


def extend_actuator():
	g.output(forward_pin, g.HIGH)
	g.output(reverse_pin, g.LOW)
	time.sleep(height)
	g.output(forward_pin, g.LOW)

def retract_actuator():
	g.output(reverse_pin, g.HIGH)
	g.output(forward_pin, g.LOW)
	time.sleep(height)
	g.output(reverse_pin, g.LOW)

def stop_actuator():
	g.output(forward_pin, g.LOW)
	g.output(reverse_pin, g.LOW)

# 0.1s per 2mm linear actuator extend
try:
	while True:
		msg = input()
		if msg == "U":
			extend_actuator()
			print("Actuator extended")
		elif msg == "D":
			retract_actuator()
			print("Actuator retracted")
		
		
except KeyboardInterrupt:
	print("Program terminated by user")
	g.cleanup()
