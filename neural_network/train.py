#-------------------------------------------#
#											#
#		TRAINING THE NEURAL NETWORK			#
#											#
#-------------------------------------------#



import numpy as np
from os import listdir
from os.path import isfile, join
import re
import cv2
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from keras.models import model_from_json

def image_resize(image, size=(32,32)):
	return cv2.resize(image, size).flatten()

# Getting a list of all the files:
#---------------------------------
image_folder = '/home/vincent/Sunfounder_Smart_Video_Car_Kit_for_RaspberryPi/screenshots'
list_files = [f for f in listdir(image_folder) if isfile(join(image_folder, f))]
list_files = [f for f in list_files if re.match('.*\.jpg',f)]

# Getting the output and input (x,y):
#------------------------------------
y = np.ones(len(list_files))
x = []
for i,f in enumerate(list_files):
	if re.match('left.*', f):
		y[i] = 0
	elif re.match('normal.*',f):
		y[i] = 1
	image_path = image_folder + '/' + f
	image = cv2.imread(image_path)
	x.append(image_resize(image))

x = np.array(x)/255

(x_train, x_test, y_train, y_test) = train_test_split(x, y, test_size=0.25, random_state=42)

# Training the model:
#--------------------
second_layer = 768

model = Sequential()
model.add(Dense(768, input_dim=3072,activation = 'sigmoid'))
model.add(Dense(384, activation="sigmoid"))
model.add(Dense(3))

model.compile(loss='sparse_categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=5, batch_size=10)

(loss, accuracy) = model.evaluate(x_test, y_test)
print("[INFO] loss={:.4f}, accuracy: {:.4f}%".format(loss, accuracy * 100))

# Saving the model:
#------------------

model_json = model.to_json()
with open("model.json", "w") as json_file:
	json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("model.h5")
print("The model was saved to disk")
