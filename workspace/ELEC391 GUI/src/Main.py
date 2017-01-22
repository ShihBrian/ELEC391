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
import struct
from matplotlib import style

style.use("ggplot")
f = Figure(figsize=(5.5,5.3), dpi=120)
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
    global square, oval
    w.delete(square)
    w.delete(oval)
    if shape == 1:
        square = w.create_rectangle(150,150,350,350, fill="lightblue")
    if shape == 2:
        oval = w.create_oval(150,150,350,350, fill="lightblue")

        
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
    global pause
    if pause:
        pause = 0
    else:
        pause = 1

def create_buttons(root):
    ttk.Button(root, text="Square", command=lambda: draw_constraint(1)).place(x=0,y=0)
    ttk.Button(root, text="Circle", command=lambda: draw_constraint(2)).place(x=75,y=0)
    ttk.Button(root, text="Pause", command=lambda: pause_update()).place(x=500,y=0)

def create_labels(root):
    Label(root, text="Rx Count", font=("Courier", 18)).place(x=660,y=30)
    Label(root, text="X Pos", font=("Courier", 20)).place(x=660,y=60)
    Label(root, text="Y Pos", font=("Courier", 20)).place(x=660,y=90)
    
def init_window():
    root = Tk()
    root.geometry('900x700+600+80')
    tk.Tk.wm_title(root, "TEST")
    canvas = FigureCanvasTkAgg(f, root)
    canvas.show()
    canvas.get_tk_widget().place(x=0,y=100)
    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.place(x=0,y=25)
    return root
        
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

    if pause == 0:
        stRcvSuccess.set("%d", success_count)
        stXCoord.set("%d", x_coord)
        stYCoord.set("%d", y_coord)
        
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
stRcvSuccess.place(x=780,y=30)
stXCoord.place(x=780,y=60)
stYCoord.place(x=780,y=90)
w = Canvas(root, width=508, height=507, highlightthickness = 0)
w.place(x=85,y=90)
rect = w.create_rectangle(250,250,253,253, fill="blue")
square = w.create_rectangle(0,0,0,0) #initialize object
oval = w.create_oval(0,0,0,0) #initialize object

entry = Entry(root, width = 5)
entry.place(x=750, y=200)
entry.focus_set()
def entry_callback():
    print (entry.get())
b=Button(root, text="get", width = 10, command=entry_callback)
b.place(x=750, y=250)
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

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
        