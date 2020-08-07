import numpy as np
import cv2
import pickle
import time

#In this file, we perform face recognition...
#But in the case where we pass an image and instantly get a prediction, here we perform some computation to ensure that it is that persons face...
#Making sure that it is that persons face is important because, we are unlocking private folder using this...
#Now there is a possiblity that an image of person is used, but this program dosent allow access to images of person...
#This is achived because there is limited time to do all computation and when using image of person, all computation wont be completed in given time...
#Hence giving access to only real persons...
#The computation parameters may have to be changed depending upon hardware specifications...

#Using haar cascades to detect faces and eyes in the frame...
face_cascade = cv2.CascadeClassifier("cascades/data/haarcascade_frontalface_alt2.xml")
eye_cascade = cv2.CascadeClassifier("cascades/data/haarcascade_eye.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()
#Using our trained model to detect the faces... Here we have trained over my faces and other folder contained images of random people... so it detects if its me or its not me...
recognizer.read("Model1.yml")
#recognizer.read("Trainner1.yml")

labels = {}
#Loading the labels and reversing the dictionary ...
with open("Label1.pickle", "rb") as f:
    labels = pickle.load(f)
    labels = {v:k for k,v in labels.items()}

not_karan = 0    #Flag will be set if it is someone other than me ... and hence access will be denied...
frame_counter = 0    #Will increase when it detects my face upto certain count and get back to 0
check_counter = 0   #Once the frame_counter reacher its count it increases, if this gets to 3 and not_karan is 0 then access is granted...
eye_counter = 0     #Checks if eye blinked, Helps to ensure that this is real person and not the image of person
not_img_karan = 0   #This gets set if eye blinks...

#Capturing the video...
cap = cv2.VideoCapture(0)

now = time.time()#to get the current time
future = now + 3#The frame will stay for the mentioned seconds...

while True:
    #capture frame-by-frame
    ret, frame = cap.read()
    #if not ret:
        #break
    #frame = cv2.flip(frame,1)

    #Converting to grayscale for prediction...
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray,scaleFactor=1.5,minNeighbors=5)
    eyes = eye_cascade.detectMultiScale(gray,scaleFactor=1.5,minNeighbors=5)

    if eyes == () and faces != ():   #Detecting if we didnt detect eyes, (Closed eyes...)
        eye_counter += 1
        if eye_counter > 1:
            not_img_karan = 1

    #Going through all the faces inside frame...
    for (x,y,w,h) in faces:
        #print(x,y,w,h)
        if (h < 100):
            #The detected ROI will be small if you are far away ...
            #Important to neglect this because if image is small, possiblity of errors increases... (detecting other people as me...)
            color = (55,55,255)
            text = "Move closer!"
            cv2.putText(frame, text,(300,30) , cv2.FONT_HERSHEY_TRIPLEX, 1, color, 2, cv2.LINE_AA)
            continue
        elif (h > 155):
            #Similarly, if face is too close again increases errors ... (not detecting me as me ...)
            color = (55,55,255)
            text = "Too Close!"
            cv2.putText(frame, text,(300,30) , cv2.FONT_HERSHEY_TRIPLEX, 1, color, 2, cv2.LINE_AA)
            continue
        
        #If we are at right distance then only we save the data and update counters
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w] #region of interest

        id_, conf = recognizer.predict(roi_gray)    #predicting the labels and confidence...
        #print(conf)

        #Now here we only choose the frame if detected confidence is above 50
        #Getting confidence above is more prone to errors... and false prediction ...
        if conf>=50 and conf<=85:   #Confidence check
            #print(labels[id_],conf)
            font = cv2.FONT_HERSHEY_TRIPLEX
            name = labels[id_]    #Generating the names from the labels...
            stroke = 2

            if name == "karan":
                #After all this, if it detects mt face it will increase frame counter...
                frame_counter += 1
                #print(frame_counter)
                if frame_counter > 5:
                    frame_counter=0
                    check_counter+=1
                    print(check_counter)
                color = (255,161,0)

                #Displaying arectangle around my face...
                cv2.putText(frame, name, (x,y-10), font, 1, color, stroke, cv2.LINE_AA)
            else:
                #If it dosent detect me, (even for 1 instance) it will deny access...
                not_karan = 1 
                color = (55,55,255)
                cv2.putText(frame, name, (x,y-10), font, 1, color, stroke, cv2.LINE_AA)
        elif conf > 85:
            #Resitting frame if it has over-confidence...
            #Hene important to have frame-counter and check_counter...
            frame_counter = 0
        else:
            pass
        color = (255,0,0)   #BGR
        stroke = 2

        cv2.rectangle(frame, (x,y), (x+w,y+h), color, stroke)
    
    cv2.imshow("frame",frame)
    #Displaying the frame...
    if cv2.waitKey(20) & 0xFF == ord("q"):
        break
    elif check_counter >= 3:
        #Printing the time taken for completing the process... 
        print("It just took ",time.time()-now," seconds.")
        break
    elif time.time() > future:
        break
    else:
        pass
    
if check_counter >= 3:
    #Noew checking each condition's 
    #As you can see, it highly not possible to grant access if it is not you or iif it is your picture ...
    #But, a perfectly held image might grant access (Extremly less probablity)
    #print(eye_counter)
    if not_img_karan == 1:
        print("KARAN DETECTED")
    else:
        print("NOT KARAN")
elif not_karan == 1:
    print("NOT KARAN")
else:
    print("TIMEOUT")

cap.release()
cv2.destroyAllWindows()