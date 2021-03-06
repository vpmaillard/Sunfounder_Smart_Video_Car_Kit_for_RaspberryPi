#!/usr/bin/env python
import PCA9685 as servo
import time                # Import necessary modules

def Map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setup(busnum=None):
	global leftPWM, rightPWM, homePWM, pwm, error_rate, current_angle
	leftPWM = 380 #400
	homePWM = 450
	rightPWM = 520 #500
	offset =0
	try:
		for line in open('config'):
			if line[0:8] == 'offset =':
				offset = int(line[9:-1])
	except:
		print 'config error'
	leftPWM += offset
	homePWM += offset
	rightPWM += offset
	if busnum == None:
		pwm = servo.PWM()                  # Initialize the servo controller.
	else:
		pwm = servo.PWM(bus_number=busnum) # Initialize the servo controller.
	pwm.frequency = 60

	# Configuring a PDI:
	error_rate = 0.03
	current_angle = homePWM

# ==========================================================================================
# Control the servo connected to channel 0 of the servo control board, so as to make the 
# car turn left.
# ==========================================================================================
def turn_left():
	global leftPWM, error_rate, current_angle
	current_angle = current_angle + error_rate * (leftPWM - current_angle)
	print(current_angle)
	pwm.write(0, 0, int(current_angle))  # CH0leftPWM

# ==========================================================================================
# Make the car turn right.
# ==========================================================================================
def turn_right():
	global rightPWM, error_rate, current_angle
	current_angle = current_angle + error_rate * (rightPWM - current_angle)
	print(current_angle)
	pwm.write(0, 0, int(current_angle))

# ==========================================================================================
# Make the car turn back.
# ==========================================================================================

def turn(angle):
	angle = Map(angle, 0, 255, leftPWM, rightPWM)
	pwm.write(0, 0, angle)

def home():
	global homePWM, error_rate, current_angle
	current_angle = current_angle + error_rate * (homePWM - current_angle)
	print(current_angle)
	pwm.write(0, 0, homePWM)

def calibrate(x):
	pwm.write(0, 0, 450+x)

def test():
	while True:
		turn_left()
		time.sleep(1)
		home()
		time.sleep(1)
		turn_right()
		time.sleep(1)
		home()

if __name__ == '__main__':
	setup()
	home()


