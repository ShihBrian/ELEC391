import sys
import tkinter as tk
from tkinter import *
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import serial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.patches import *
from enum import Enum
from matplotlib import style
import time

start_time = time.time()

wHeight = 508
wWidth = 501

style.use("ggplot")
f = Figure(figsize=(5.4,5.3), dpi=120)
a = f.add_subplot(111)
b = f.add_subplot(111)
a.set_xlim([0,250])
a.set_ylim([0,250])
idx = 0
rcvBuf = [0]*6
changestate = False
success_count = 0
fail_count = 0
x_coord = 0
y_coord = 0
pause = 0

class States(Enum):
    RxStart = 1
    RxXCoord = 2
    RxYCoord = 3
    RxEnd = 4

state = States.RxStart
nxtstate = States.RxStart

sqX=100
sqY=100
sqL=50
sqH=50


class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, anchor=W, relief="solid", borderwidth =2, font=("Courier", 20), width = 6)
        self.label.pack()

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

def draw_constraint(shape): 
    global sqX, sqY, sqL, sqH
    w.delete(ALL)
    if shape == 1:
        w.create_rectangle(sqX*(wWidth/250),wHeight-sqY*(wHeight/250),(sqX+sqL)*(wWidth/250), wHeight-(sqY+sqH)*(wHeight/250), fill="lightblue")
        create_entry(1)
    if shape == 2:
        w.create_oval(150,150,350,350, fill="lightblue")

bOnce = 1;
bOnce2 = 1;
def rectIntersect(pX, pY):
    global sqX, sqY, sqH, sqL, bOnce, bOnce2
    cTRx = sqX+sqL
    CBLy = sqY+sqH
    
    if (pX >= sqX and pX <= cTRx) and (pY >= sqY and pY <= CBLy):
        if bOnce:
            bOnce2 = 1
            ser.write(b"\xFF")
            bOnce = 0
    else:
        if bOnce2:
            if start_time+1 < time.time():
                bOnce = 1
                ser.write("1".encode())
                bOnce2 = 0
            
def create_entry(shape):
    def entry_callback():
        global sqX, sqY, sqH, sqL
        sqX = int(entryX.get())
        sqY = int(entryY.get())
        sqL = int(entryLength.get())
        sqH = int(entryHeight.get())
        draw_constraint(shape)     
    b=Button(root, text="Set", width = 10, command=entry_callback)
    b.place(x=680, y=280)
    if shape == 1:
        entryX = Entry(root, width = 5)
        entryX.place(x=760,y=200)
        entryY = Entry(root, width = 5)
        entryY.place(x=800,y=200)
        XYLabel = Label(root, text="Bottom Left X,Y")
        XYLabel.place(x=660,y=200)
        entryLength = Entry(root, width = 5)
        entryLength.place(x=760, y=225)
        LengthLabel = Label(root, text="Length")
        LengthLabel.place(x=660,y=225)
        entryHeight = Entry(root, width = 5)
        entryHeight.place(x=760, y=250)
        WidthLabel = Label(root, text="Height")
        WidthLabel.place(x=660,y=250)     
  
def init_serial():
    ser = serial.Serial()
    ser.baudrate = 57600
    ser.port = 'COM6'
    ser.timeout = 1
    ser.open()
    return ser

def draw_point(x,y):
    global rect, pause
    if pause == 0:
        w.delete(rect)
        rect = w.create_rectangle(x-1,507-y-1,x+3,507-y+3, fill="blue", outline="")

def pause_update():
    ser.write(b"\xFE")

def create_buttons(root):
    ttk.Button(root, text="Square", command=lambda: draw_constraint(1)).place(x=0,y=0)
    ttk.Button(root, text="Circle", command=lambda: draw_constraint(2)).place(x=75,y=0)
    ttk.Button(root, text="Pause", command=lambda: pause_update()).place(x=500,y=0)
    ttk.Button(root, text="Clear", command=lambda: clear()).place(x=575,y=0)

def create_labels(root):
    Label(root, text="Rx Count", font=("Courier", 18)).place(x=660,y=10)
    Label(root, text="X Pos", font=("Courier", 20)).place(x=660,y=40)
    Label(root, text="Y Pos", font=("Courier", 20)).place(x=660,y=70)
    
def init_window():
    root = Tk()
    root.geometry('900x700+600+80')
    tk.Tk.wm_title(root, "TEST")
    canvas = FigureCanvasTkAgg(f, root)
    canvas.show()
    canvas.get_tk_widget().place(x=0,y=100)
    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.place(x=0,y=35)
    return root

def clear():
    global square, sqX, sqY, sqH, sqL
    sqX = sqY = 100
    sqH = sqL = 50
    w.delete(ALL)
   
def close(event):
    sys.exit()
         
def main():
    global idx, rcvBuf, state, nextstate, changestate, success_count, x_coord, y_coord, pause

#-----------------------------------------------------------------------------------------    
#-------------------------Transfer Protocol State Machine---------------------------------
#-----------------------------------------------------------------------------------------
    if ser.inWaiting()>0:
        x = int(ser.read(3),16)

        if state == States.RxStart: #waiting to receive startbyte
            if x == 255: #received startbyte
                changestate = True
                nextstate = States.RxXCoord
        elif state == States.RxXCoord: #receive x coord
            rcvBuf[0] = x
            changestate = True
            nextstate = States.RxYCoord
        elif state == States.RxYCoord: #receive y coord
            rcvBuf[1] = x
            changestate = True
            nextstate = States.RxEnd
        elif state == States.RxEnd: #should receive endbyte
            if x == 254: #if endbyte is received then update x,y coordinate
                success_count = success_count + 1
                x_coord = rcvBuf[0]
                y_coord = rcvBuf[1]
                draw_point(x_coord*2,y_coord*2)  
            #else discard bytes and change state back to waiting for startbyte
            changestate = True
            nextstate = States.RxStart
                
    if changestate:
        state = nextstate
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
    stRcvSuccess.set("%d", success_count)
    stXCoord.set("%d", x_coord)
    stYCoord.set("%d", y_coord)
    rectIntersect(x_coord, y_coord)
    
    root.after(1,main)



#-----------------------------------------------------------------------------------------    
#-------------------------Initialization---------------------------------
#-----------------------------------------------------------------------------------------    
ser = init_serial()  
root = init_window()
create_buttons(root)
create_labels(root)
stRcvSuccess = StatusBar(root)
stXCoord = StatusBar(root)
stYCoord = StatusBar(root)
stRcvSuccess.place(x=780,y=10)
stXCoord.place(x=780,y=40)
stYCoord.place(x=780,y=70)
w = Canvas(root, width=wWidth, height=wHeight, highlightthickness = 0)
w.place(x=82,y=98)
rect = w.create_rectangle(0,0,0,0, fill="blue")
create_entry(1)
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
root.bind('<Escape>', close)
root.after(1,main)
root.mainloop()

#dont want to use tk.canvas to display point. ideally want to use matplotlib function but too laggy right now
#fix scaling issues    
#enter values to reposition shapes
#display information on side bar x,y for now
#more shapes
#images
#custom shapes
#print adc, pin states, internal voltage, temp (if any are applicable)      
#add length option in receive protocol  
#handshake
#display extension length of actuator
        