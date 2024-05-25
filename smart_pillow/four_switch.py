import RPi.GPIO as g
import time

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


try:
	print("start")
	while True:
		if g.input(reset_sw) == 1:
			print("Actuator reset")
			time.sleep(0.3)
		elif g.input(up_sw) == 1:
			print("Actuator up")
			time.sleep(0.3)
		elif g.input(down_sw) == 1:
			print("Actuator down")
			time.sleep(0.3)
		elif g.input(auto_sw) == 1:
			print("Actuator auto")
			time.sleep(0.3)
		
	
except KeyboardInterrupt:
	print("Program terminated by user")
	g.cleanup()
