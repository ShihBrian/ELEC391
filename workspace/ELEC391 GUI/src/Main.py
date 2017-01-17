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

from matplotlib import style

style.use("ggplot")
f = Figure(figsize=(5.5,5.3), dpi=120)
a = f.add_subplot(111)
b = f.add_subplot(111)
b.add_patch(Rectangle((50,50),55,55,alpha = 0.5, hatch='\\'))
a.set_xlim([0,250])
a.set_ylim([0,250])
idx = 0
rcvBuf = [0]*6
state = 0
nxtstate = 0
changestate = False
success_count = 0
fail_count = 0
x_coord = 0
y_coord = 0
square=0
circle=1

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
    if shape == 1:
        w.create_oval(240,240,260,260, fill="green")
        
def init_serial():
    ser = serial.Serial()
    ser.baudrate = 57600
    ser.port = 'COM6'
    ser.timeout = 0
    ser.open()
    return ser

def draw_point(x,y):
    global rect
    w.delete(rect)
    rect = w.create_rectangle(x-1,507-y-1,x+3,507-y+3, fill="blue", outline="")

def main():
    global idx, rcvBuf, state, nextstate, changestate, success_count, fail_count, x_coord, y_coord
    fail_percent = 0.0
    if ser.inWaiting()>0:
        x = int(ser.read(3),16)
        if state == 0: #waiting to receive startbyte
            if x == 255: #received startbyte
                changestate = True
                nextstate = 1
        elif state == 1: #receive x coord
            rcvBuf[0] = x
            changestate = True
            nextstate = 2
        elif state == 2: #receive y coord
            rcvBuf[1] = x
            changestate = True
            nextstate = 3
        elif state == 3: #should receive endbyte
            if x == 254: #if endbyte is received then update x,y coordinate
                success_count = success_count + 1
                x_coord = rcvBuf[0]
                y_coord = rcvBuf[1]
                draw_point(x_coord*2,y_coord*2)  
            else: #else discard bytes and change state back to waiting for startbyte
                fail_count = fail_count + 1
            changestate = True
            nextstate = 0
            
        if changestate:
            state = nextstate
        
        if(success_count):
            fail_percent = fail_count/(fail_count+success_count) 
        stRcvFail.set("%d", fail_count)
        stRcvSuccess.set("%d", success_count)
        stXCoord.set("%d", x_coord)
        stYCoord.set("%d", y_coord)
        stFailPercent.set("%.2f", fail_percent*100)
        
    root.after(1,main)
    
ser = init_serial()  
root = Tk()
root.geometry('1600x900+100+80')
tk.Tk.wm_title(root, "TEST")
canvas = FigureCanvasTkAgg(f, root)
canvas.show()
canvas.get_tk_widget().place(x=0,y=200)
toolbar = NavigationToolbar2TkAgg(canvas, root)
toolbar.update()
canvas._tkcanvas.place(x=0,y=150)
stRcvFail = StatusBar(root)
stRcvSuccess = StatusBar(root)
stXCoord = StatusBar(root)
stYCoord = StatusBar(root)
stRcvFail.place(x=850,y=600)
stRcvSuccess.place(x=850,y=640)
stFailPercent = StatusBar(root)
stFailPercent.place(x=850,y=680)
stXCoord.place(x=850,y=720)
stYCoord.place(x=850,y=760)
ttk.Button(root, text="Square", command=lambda: draw_constraint(1)).place(x=0,y=100)
ttk.Button(root, text="Circle", command=lambda: draw_constraint(2)).place(x=75,y=100)
Label(root, text="Rx Fail", font=("Courier", 20)).place(x=700,y=600)
Label(root, text="Rx Success", font=("Courier", 18)).place(x=700,y=640)
Label(root, text="Fail %", font=("Courier", 20)).place(x=700,y=680)
Label(root, text="X Pos", font=("Courier", 20)).place(x=700,y=720)
Label(root, text="Y Pos", font=("Courier", 20)).place(x=700,y=760)
w = Canvas(root, width=508, height=507, highlightthickness = 0)
w.place(x=85,y=215)
rect = w.create_rectangle(250,250,253,253, fill="blue")
root.after(1,main)
root.mainloop()

#dont want to use tk.canvas to display point. ideally want to use matplotlib function but too laggy right now
#fix scaling issues
#pause screen update     
#enter values to reposition shapes
#display information on side bar x,y for now
#more shapes
#images
#custom shapes
#print adc, pin states, internal voltage, temp (if any are applicable)      
#add length option in receive protocol  
#handshake
#display extension length of actuator
        