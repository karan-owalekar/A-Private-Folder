from tkinter import *
from PIL import Image,ImageTk

#UI design for password 

r = Tk()

large_font = ('Verdana',17)

fP = Frame(r)
fP.config(bg= "Black")

imgEntry = ImageTk.PhotoImage(Image.open("UI_Images/Pwd_Entry.png"))
L = Label(fP,image=imgEntry,borderwidth=0)
L.grid(row=0,column=0)

imgSubmit = ImageTk.PhotoImage(Image.open("UI_Images/Submit.png"))
B = Button(fP,image=imgSubmit,borderwidth=0,bg= "Black",activebackground="black",highlightthickness = 0, bd = 0)
B.grid(row=1)

E = Entry(fP,width=13,font = large_font,show="*",background="Black",highlightthickness = 0, bd = 0,fg="#1287ff", insertbackground='#1287ff')
E.grid(row=0,column=0,padx=(8,0))

fP.pack()

#r.geometry("200x150")
r.mainloop()
