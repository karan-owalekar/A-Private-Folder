import os
from tkinter import *
import numpy as np
import cv2
from PIL import Image,ImageTk
from itertools import count
import pickle
import time
import threading

folder_name = "Locker"    #Folder that we want to lock/ unlock...
Saved_Hash = "c#cCW1S-iN]B{Z>_^O"   #Hash value that must match when we enter password... (if program cannot confirm its you...)

large_font = ('Verdana',17)
Extra_large_font = ('Verdana',30)

#Recognition works exactly as in Face_recog.py
face_cascade = cv2.CascadeClassifier("cascades/data/haarcascade_frontalface_alt2.xml")
eye_cascade = cv2.CascadeClassifier("cascades/data/haarcascade_eye.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("Model/Model1.yml")

labels = {}
with open("Model/Label1.pickle", "rb") as f:
    labels = pickle.load(f)
    labels = {v:k for k,v in labels.items()}

cap = cv2.VideoCapture(0)

#But instead of displaying the captured frames we display loading-spinner and all computations are hidden from user...
#This provides some security against trying to access folder via images...
#Without seeing where and how we are holding the image, it id difficult to perfectly align ...
class ImageLabel(Label):
    """a label that displays images, and plays them if they are gifs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)

def Special():
    #This is a kind of hack/special buttin hidden in the UI.
    #This bypasses everything and unlocks the folder...
    print("Special Botton")
    os.system("attrib "+folder_name+" -h -s -r")

def ENCRYPT(plain,key):
    key_len = len(key)
    plain_split = []
    cipher=[]
    plain = list(plain)

    for i in range(0,len(plain),key_len):
        temp = []
        for j in range(key_len):
            temp.append(plain[i+j])
        plain_split.append(''.join(temp))
    
    for i in range(len(plain_split)):
        if i == 0:
            cipher.append(GET_CIPHER(plain_split[i],key))
        else:
            cipher.append(GET_CIPHER(plain_split[i],cipher[i-1]))

    return("".join(cipher))

def GET_CIPHER(plain,key):
    ans=[]
    for i in range(len(plain)):
        x = ord(plain[i])
        y = ord(key[i])
        if i%2 == 0:
            for j in range(y):
                x+=1
                if x==127:
                    x=32
        else:
            for j in range(y):
                x-=1
                if x==31:
                    x=126
        ans.append(chr(x))
    return("".join(ans))


def BACK():
    BackF.pack_forget()
    f.pack()
def BULB():
    f.pack_forget()
    BackF.pack()

def LOCK():
    os.system("attrib "+folder_name+" +h +s +r")

def UNLOCK():
    f.pack_forget()
    threading.Thread(target= SCAN_FACE).start()
    LoadingF.pack()
    lbl.load('Loading.gif')
    LoadingF.config(cursor="wait")


def SCAN_FACE():
    #This is the program for face recognition...
    not_karan = 0
    frame_counter = 0
    check_counter = 0
    eye_counter = 0
    not_img_karan = 0
    
    now = time.time()#to get the current time
    future = now + 3#The frame will stay for the mentioned seco

    while True:
        DisplayLabel.configure(text="")
        #capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break
        #frame = cv2.resize(frame, (960,720))
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray,scaleFactor=1.5,minNeighbors=5)
        eyes = eye_cascade.detectMultiScale(gray,scaleFactor=1.5,minNeighbors=5)
        #print(eyes)
        if eyes == () and faces != ():
            eye_counter += 1
            if eye_counter >1:
                not_img_karan = 1

        for (x,y,w,h) in faces:
            #print(x,y,w,h)
            if (h < 100):
                DisplayLabel.configure(text="Move Closer!",fg="Red")
                continue
            elif (h > 155):
                DisplayLabel.configure(text="Too Close!",fg="Red")
                continue

            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w] #region of interest
            #img_item = "my-image.png"
            #
            # cv2.imwrite(img_item,roi_color)

            id_, conf = recognizer.predict(roi_gray)
            #print(conf)
            if conf>=50 and conf<=85:   #Confidence check
                #print(labels[id_],conf)
                font = cv2.FONT_HERSHEY_TRIPLEX
                name = labels[id_]
                stroke = 2
                if name == "karan":
                    frame_counter += 1
                    #print(frame_counter)
                    if frame_counter > 5:
                        frame_counter=0
                        check_counter+=1
                        print(check_counter)
                    color = (255,161,0)
                    cv2.putText(frame, name, (x,y-10), font, 1, color, stroke, cv2.LINE_AA)
                else:
                    not_karan = 1 
                    color = (55,55,255)
                    cv2.putText(frame, name, (x,y-10), font, 1, color, stroke, cv2.LINE_AA)
            elif conf > 85:
                frame_counter = 0
            else:
                pass
            color = (255,0,0)   #BGR
            stroke = 2

            cv2.rectangle(frame, (x,y), (x+w,y+h), color, stroke)
        
        #cv2.imshow("frame",frame)
        if cv2.waitKey(20) & 0xFF == ord("q"):
            break
        elif check_counter >= 3:
            print(time.time()-now)
            break
        elif time.time() > future:
            break
        else:
            pass

    cap.release()
    cv2.destroyAllWindows()

    if check_counter >= 3:
        #print(eye_counter)
        if not_img_karan == 1:
            print("KARAN DETECTED")
            lbl.load('UI_Images/Openning.gif')
            LoadingF.config(cursor="")
            DisplayLabel.configure(text="Welcome!",fg="White")
            threading.Thread(target = UNLOCK_FOLDER).start()
        else:
            print("NOT KARAN")
            r.quit()
    elif not_karan == 1:
        print("NOT KARAN")
        r.quit()
    else:
        print("TIMEOUT")
        Password_Box()

def Password_Box():
    LoadingF.pack_forget()
    fP.pack()

def CheckPassword():
    pwd = E.get()
    Spl_chr_Even = "N#a&RaK9" 
    Spl_chr_Odd = "!Kar)*(an"
    new_pwd=[]
    if len(pwd)%2 == 0:
        new_pwd.append(Spl_chr_Odd)
        for i in range(len(pwd)//2):
            new_pwd.append(pwd[i])
        new_pwd.append(Spl_chr_Even)
        for i in range(len(pwd)//2,len(pwd)):
            new_pwd.append(pwd[i])
        new_pwd.append(Spl_chr_Odd[::-1])
    else:
        new_pwd.append(Spl_chr_Even[::-1])
        for i in range(len(pwd)//2):
            new_pwd.append(pwd[i])
        new_pwd.append(Spl_chr_Odd)
        for i in range(len(pwd)//2,len(pwd)):
            new_pwd.append(pwd[i])
        new_pwd.append(Spl_chr_Even)

    new_pwd = "".join(new_pwd)

    text = new_pwd[:len(new_pwd)//2]
    key = new_pwd[len(new_pwd)//2:]

    x = ENCRYPT(text,key)
    #hash_val = hash(x)
    #print(hash_val)
    if x == Saved_Hash:
        print("Correct Password")
        os.system("attrib "+folder_name+" -h -s -r")
        r.quit()
    else:
        print("Incorrect Password")
        r.quit()

def UNLOCK_FOLDER():
    time.sleep(1.8)
    os.system("attrib "+folder_name+" -h -s -r")
    r.quit()
    

#Building the UI

#MAIN

r = Tk()
r.title("Private Folder")

f = Frame(r)
f.configure(bg="Black")

imgBulb = ImageTk.PhotoImage(Image.open("UI_Images/Bulb.png"))
Bulb = Button(f,image = imgBulb,bg="Black",borderwidth = 0,height = 60,activebackground="black",highlightthickness = 0, bd = 0, command = BULB)
Bulb.grid(row=0,column=0)

imgBulbF = ImageTk.PhotoImage(Image.open("UI_Images/Bulb_Front.png"))
BulbF = Label(f,image = imgBulbF,borderwidth = 0)
BulbF.grid(row=0,column=1,columnspan=2)

imgPF = ImageTk.PhotoImage(Image.open("UI_Images/PF_Logo.png"))
PF = Label(f,image = imgPF,borderwidth = 0)
PF.grid(row=1,columnspan=3)

imgLock = ImageTk.PhotoImage(Image.open("UI_Images/Lock.png"))
Lock = Button(f,image = imgLock,borderwidth = 0,bg= "Black",activebackground="black",highlightthickness = 0, bd = 0, command = LOCK)
Lock.grid(row=2,columnspan=3)

imgUnlock = ImageTk.PhotoImage(Image.open("UI_Images/Unlock.png"))
Unlock = Button(f,image = imgUnlock,borderwidth = 0,bg= "Black",activebackground="black",highlightthickness = 0, bd = 0,command= UNLOCK)
Unlock.grid(row=3,columnspan=3)

imgBS = ImageTk.PhotoImage(Image.open("UI_Images/Before_Special.png"))
B4Spl = Label(f,image=imgBS,borderwidth=0)
B4Spl.grid(row=4,columnspan=2)

imgSpl = ImageTk.PhotoImage(Image.open("UI_Images/Special_Button.png"))
SpecialBtn = Button(f,image = imgSpl,borderwidth = 0,bg= "Black",activebackground="black",highlightthickness = 0, bd = 0,command = Special)
SpecialBtn.grid(row=4,column=2)

f.pack()

BackF = Frame(r)
BackF.configure(bg="Black")

imgBack = ImageTk.PhotoImage(Image.open("UI_Images/Back.png"))
Back = Button(BackF,image = imgBack,bg="Black",borderwidth = 0,height = 58,activebackground="black",highlightthickness = 0, bd = 0, command = BACK)
Back.grid(row=0,column=0)

imgBackF = ImageTk.PhotoImage(Image.open("UI_Images/Back_Front.png"))
Backf = Label(BackF,image=imgBackF,borderwidth=0)
Backf.grid(row=0,column=1)

imginfo = ImageTk.PhotoImage(Image.open("UI_Images/info.png"))
info = Label(BackF,image=imginfo,borderwidth=0)
info.grid(row=1,columnspan=2)

#Loading Screen
LoadingF = Frame(r)
LoadingF.config(bg="Black")

BGimg = ImageTk.PhotoImage(Image.open("UI_Images/Loading_Screen.png"))
BGl = Label(LoadingF,image = BGimg,borderwidth=0)
BGl.grid(row=0,rowspan=3)

lbl = ImageLabel(LoadingF,borderwidth=0)
lbl.grid(row=0)
#lbl.load('Openning.gif')

DisplayLabel = Label(LoadingF,text="",borderwidth=0,font=Extra_large_font,bg="Black")
DisplayLabel.grid(row=2)

#Password BOX
fP = Frame(r)
fP.config(bg= "Black")

imgEntry = ImageTk.PhotoImage(Image.open("UI_ImagesPwd_Entry.png"))
L = Label(fP,image=imgEntry,borderwidth=0)
L.grid(row=0,column=0)

imgSubmit = ImageTk.PhotoImage(Image.open("UI_Images/Submit.png"))
B = Button(fP,image=imgSubmit,borderwidth=0,bg= "Black",activebackground="black",highlightthickness = 0, bd = 0,command = CheckPassword)
B.grid(row=1)

E = Entry(fP,width=13,font = large_font,show="*",background="Black",highlightthickness = 0, bd = 0,fg="#1287ff", insertbackground='#1287ff')
E.grid(row=0,column=0,padx=(8,0))


#r.geometry("694x692")
r.mainloop()
