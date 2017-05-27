#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Tkinter import *
from socket import *      # Import necessary modules
import urllib
import cv2
import numpy as np
import time
from keras.models import model_from_json

# urllib.urlretrieve("http://192.168.1.117:8080/?action=snapshot", "test.jpg")
# How it is going to work:
#-------------------------

# Status variable is used: status = -1,0,1 for left, forward, right respectively.
# Status is update on each key press and key release.
# The loop function in the TK loop function, we take a screenshot at a given frequency.

# Important key release setting
#   xset r off	Turn off automatic key releases.
#	xset r on	Turn on automatic key releases.
# This is useful to train the model and monitor the supervised model (On state, going forward left or right.)


ctrl_cmd = ['forward', 'backward', 'left', 'right', 'stop', 'read cpu_temp', 'home', 'distance', 'x+', 'x-', 'y+', 'y-', 'xy_home']

top = Tk()   # Create a top window
top.title('Control Center')

# Variables for monitoring screenshots and status of car:
#--------------------------------------------------------
status = 0 # 0=forward, -1=left, +1=right
is_it_on = False
file_iteration = '../screenshots/iteration.txt'
iteration = 1
f = open(file_iteration, 'r')
iteration = f.readlines()
iteration = int(iteration[0]) + 1
f.close()

# Loading the Neural Network:
#----------------------------
json_file = open('../neural_network/model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("../neural_network/model.h5")
loaded_model.compile(loss='sparse_categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])


# Connecting to the car:
#-----------------------
HOST = '192.168.1.117'    # Server(Raspberry Pi) IP address
PORT = 21567
BUFSIZ = 1024             # buffer si#Rather read in a file the number ?ze
ADDR = (HOST, PORT)

tcpCliSock = socket(AF_INET, SOCK_STREAM)   # Create a socket
tcpCliSock.connect(ADDR)                    # Connect with the server


# =============================================================================
# Taking screenshots with the car on a regular basis.
#==============================================================================
def image_resize(image, size=(32,32)):
	return cv2.resize(image, size).flatten()

def taking_screenshot():
	global status, is_it_on, iteration
	if is_it_on:
		if status == -1:
			urllib.urlretrieve("http://192.168.1.117:8080/?action=snapshot", '../screenshots/left_' + str(iteration) + '.jpg')
		if status == 1:
			urllib.urlretrieve("http://192.168.1.117:8080/?action=snapshot", '../screenshots/right_' + str(iteration) + '.jpg')
		else:
			urllib.urlretrieve("http://192.168.1.117:8080/?action=snapshot", '../screenshots/normal_' + str(iteration) + '.jpg')
		iteration = iteration + 1
		print 'Screenshot taken bro'
	top.after(200, taking_screenshot)

def driving():
	# Driving the car:
	image = urllib.urlopen('http://192.168.1.117:8080/?action=snapshot')
	image = np.asarray(bytearray(image.read()), dtype=np.uint8)
	image = cv2.imdecode(image, -1)
	image = np.array(image_resize(image)) / 255

	# Use the neural network to get directions:
	global loaded_model
	direction = loaded_model.predict(image)

	# Turn whichever direction you need:
	if direction == 0:
		# Turn left:
		tcpCliSock.send('left')
	elif direction == 1:
		tcpCliSock.send('forward')
	elif direction == 2:
		tcpCliSock.send('right')
	else:
		tcpCliSock.send('stop')
	top.after(200, driving)

# =============================================================================
# The function is to send the command forward to the server, so as to make the 
# car move forward.
# ============================================================================= 
def forward_fun(event):
	print 'forward'
	global is_it_on
	is_it_on = True
	tcpCliSock.send('forward')

def backward_fun(event):
	print 'backward'
	tcpCliSock.send('backward')

def left_fun(event):
	print 'left'
	global status
	status = -1
	tcpCliSock.send('left')

def right_fun(event):
	print 'right'
	global status
	status = 1
	tcpCliSock.send('right')

def stop_fun(event):
	print 'stop'
	global is_it_on
	is_it_on = False
	tcpCliSock.send('stop')

def home_fun(event):
	print 'home'
	global status
	status = 0
	tcpCliSock.send('home')

def x_increase(event):
	print 'x+'
	tcpCliSock.send('x+')

def x_decrease(event):
	print 'x-'
	tcpCliSock.send('x-')

def y_increase(event):
	print 'y+'
	tcpCliSock.send('y+')

def y_decrease(event):
	print 'y-'
	tcpCliSock.send('y-')

def xy_home(event):
	print 'xy_home'
	tcpCliSock.send('xy_home')

# =============================================================================
# Exit the GUI program and close the network connection between the client 
# and server.
# =============================================================================
def quit_fun(event):
	top.quit()
	tcpCliSock.send('stop')
	tcpCliSock.close()

# =============================================================================
# Create buttons
# =============================================================================
Btn0 = Button(top, width=5, text='Forward')
Btn1 = Button(top, width=5, text='Backward')
Btn2 = Button(top, width=5, text='Left')
Btn3 = Button(top, width=5, text='Right')
Btn4 = Button(top, width=5, text='Quit')
Btn5 = Button(top, width=5, height=2, text='Home')

# =============================================================================
# Buttons layout
# =============================================================================
Btn0.grid(row=0,column=1)
Btn1.grid(row=2,column=1)
Btn2.grid(row=1,column=0)
Btn3.grid(row=1,column=2)
Btn4.grid(row=3,column=2)
Btn5.grid(row=1,column=1)

# =============================================================================
# Bind the buttons with the corresponding callback function.
# =============================================================================
Btn0.bind('<ButtonPress-1>', forward_fun)  # When button0 is pressed down, call the function forward_fun().
Btn1.bind('<ButtonPress-1>', backward_fun)
Btn2.bind('<ButtonPress-1>', left_fun)
Btn3.bind('<ButtonPress-1>', right_fun)
Btn0.bind('<ButtonRelease-1>', stop_fun)   # When button0 is released, call the function stop_fun().
Btn1.bind('<ButtonRelease-1>', stop_fun)
Btn2.bind('<ButtonRelease-1>', stop_fun)
Btn3.bind('<ButtonRelease-1>', stop_fun)
Btn4.bind('<ButtonRelease-1>', quit_fun)
Btn5.bind('<ButtonRelease-1>', home_fun)

# =============================================================================
# Create buttons
# =============================================================================
Btn07 = Button(top, width=5, text='X+', bg='red')
Btn08 = Button(top, width=5, text='X-', bg='red')
Btn09 = Button(top, width=5, text='Y-', bg='red')
Btn10 = Button(top, width=5, text='Y+', bg='red')
Btn11 = Button(top, width=5, height=2, text='HOME', bg='red')

# =============================================================================
# Buttons layout
# =============================================================================
Btn07.grid(row=1,column=5)
Btn08.grid(row=1,column=3)
Btn09.grid(row=2,column=4)
Btn10.grid(row=0,column=4)
Btn11.grid(row=1,column=4)

# =============================================================================
# Bind button events
# =============================================================================
Btn07.bind('<ButtonPress-1>', x_increase)
Btn08.bind('<ButtonPress-1>', x_decrease)
Btn09.bind('<ButtonPress-1>', y_decrease)
Btn10.bind('<ButtonPress-1>', y_increase)
Btn11.bind('<ButtonPress-1>', xy_home)
#Btn07.bind('<ButtonRelease-1>', home_fun)
#Btn08.bind('<ButtonRelease-1>', home_fun)
#Btn09.bind('<ButtonRelease-1>', home_fun)
#Btn10.bind('<ButtonRelease-1>', home_fun)
#Btn11.bind('<ButtonRelease-1>', home_fun)

# =============================================================================
# Bind buttons on the keyboard with the corresponding callback function to 
# control the car remotely with the keyboard.
# =============================================================================
top.bind('<KeyPress-a>', left_fun)   # Press down key 'A' on the keyboard and the car will turn left.
top.bind('<KeyPress-d>', right_fun) 
top.bind('<KeyPress-s>', backward_fun)
top.bind('<KeyPress-w>', forward_fun)
top.bind('<KeyPress-h>', home_fun)
top.bind('<KeyRelease-a>', home_fun) # Release key 'A' and the car will turn back.
top.bind('<KeyRelease-d>', home_fun)
top.bind('<KeyRelease-s>', stop_fun)
top.bind('<KeyRelease-w>', stop_fun)

spd = 50

def changeSpeed(ev=None):
	tmp = 'speed'
	global spd
	spd = speed.get()
	data = tmp + str(spd)  # Change the integers into strings and combine them with the string 'speed'. 
	print 'sendData = %s' % data
	tcpCliSock.send(data)  # Send the speed data to the server(Raspberry Pi)

label = Label(top, text='Speed:', fg='red')  # Create a label
label.grid(row=6, column=0)                  # Label layout
speed = Scale(top, from_=0, to=100, orient=HORIZONTAL, command=changeSpeed)  # Create a scale
speed.set(50)
speed.grid(row=6, column=1)

def main():
	top.after(200, taking_screenshot)
	#top.after(200, driving) Comment out to kick off autopilot.
	top.mainloop()

	# Print number of iteration to file:
	f = open(file_iteration, 'w')
	f.write(str(iteration))
	f.close()

if __name__ == '__main__':
	main()

