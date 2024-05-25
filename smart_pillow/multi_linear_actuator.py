import RPi.GPIO as g
import time

center_forward_pin = 5
center_reverse_pin = 25

right_forward_pin = 27
right_reverse_pin = 22

left_forward_pin = 6
left_reverse_pin = 13


height = float(input())

g.setmode(g.BCM)
g.setwarnings(False)

g.setup(center_forward_pin, g.OUT)
g.setup(center_reverse_pin, g.OUT)
g.setup(right_forward_pin, g.OUT)
g.setup(right_reverse_pin, g.OUT)
g.setup(left_forward_pin, g.OUT)
g.setup(left_reverse_pin, g.OUT)


def extend_actuator(forward_pin, reverse_pin):
	g.output(forward_pin, g.HIGH)
	g.output(reverse_pin, g.LOW)
	time.sleep(height)
	g.output(forward_pin, g.LOW)

def retract_actuator(forward_pin, reverse_pin):
	g.output(reverse_pin, g.HIGH)
	g.output(forward_pin, g.LOW)
	time.sleep(height)
	g.output(reverse_pin, g.LOW)

def stop_actuator(forward_pin, reverse_pin):
	g.output(forward_pin, g.LOW)
	g.output(reverse_pin, g.LOW)

# 0.1s per 2mm linear actuator extend
try:
	while True:
		msg_location = input("location: ")
		msg_direction = input("direction: ")
		if msg_location == "C":
			if msg_direction == "U":
				extend_actuator(center_forward_pin, center_reverse_pin)
				print("Center Actuator extended")
			elif msg_direction == "D":
				retract_actuator(center_forward_pin, center_reverse_pin)
				print("Center Actuator retracted")
		
		elif msg_location == "R":
			if msg_direction == "U":
				extend_actuator(right_forward_pin, right_reverse_pin)
				print("Right Actuator extended")
			elif msg_direction == "D":
				retract_actuator(right_forward_pin, right_reverse_pin)
				print("Right Actuator retracted")
		
		elif msg_location == "L":
			if msg_direction == "U":
				extend_actuator(left_forward_pin, left_reverse_pin)
				print("Left Actuator extended")
			elif msg_direction == "D":
				retract_actuator(left_forward_pin, left_reverse_pin)
				print("Left Actuator retracted")
		
except KeyboardInterrupt:
	print("Program terminated by user")
	g.cleanup()
