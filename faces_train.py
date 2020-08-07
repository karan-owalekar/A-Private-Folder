import os
import cv2
import numpy as np
from PIL import Image
import pickle

#This program is used to train the yml file to recognize faces

#Getting the location of the current file...
base_dir = os.path.dirname(os.path.abspath(__file__))
#Setting up location of our training data...
img_dir = os.path.join(base_dir,"Images")

#Using haar cascade file to detect faces in the image and getting the ROI (Region of interest)
face_cascade = cv2.CascadeClassifier("cascades/data/haarcascade_frontalface_alt2.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()

#Setting up id's for each persons face (folders)
current_id = 0
label_ids = {}
y_label = []
x_train = []

for root, dirs, files in os.walk(img_dir):
    for file in files:
        #Going through all the files inside each folder one-by-one ...
        #Only considering '.png' or '.jpg'
        if file.endswith("png") or file.endswith("jpg"):
            path = os.path.join(root, file)
            label = os.path.basename(root).replace(" ","-").lower()
            #print(label,path)

            #Checking if this is new folfer  or not ...
            if not label in label_ids:
                label_ids[label] = current_id
                current_id +=1

            id_ = label_ids[label]
            #print(label_ids)
            
            #Opening and converting images into numpy arrays...
            pil_image = Image.open(path).convert("L")   #Converts to grayscale
            image_array = np.array(pil_image, "uint8")
            #print(image_array)

            #Detecting faces inside the image...
            faces = face_cascade.detectMultiScale(image_array,scaleFactor=1.5,minNeighbors=5)

            #Now for all the faces (expected 1 for best perfomance), we get ROI and store that inside training variable...
            for (x, y, w, h) in faces:
                roi = image_array[y:y+h, x:x+w]
                x_train.append(roi)
                y_label.append(id_)

#After the loop we will have list of numpy array containing image data and other list associated with its labels...

#print(y_label)
#print(x_train)

with open("Label1.pickle", "wb") as f:
    #Ssving the folder name as label inside dictionary using pickle
    pickle.dump(label_ids, f)

#Training the model...
recognizer.train(x_train, np.array(y_label))
#Saving it as '.yml' file...
recognizer.save("Model1.yml")