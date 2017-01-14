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
f = Figure(figsize=(5.5,5.5), dpi=120)
a = f.add_subplot(111)
b = f.add_subplot(111)
a.set_xlim([0,500])
a.set_ylim([0,500])
square=0
circle=1
idx = 0
rcvBuf = [0]*6
state = 0
nxtstate = 0
changestate = False
success_count = 0
fail_count = 0
x_coord = 0
y_coord = 0

def animate(i):
    global square, circle
              
    a.clear()

    if square == 1: 
        b.add_patch(Rectangle((50,50),500,500,alpha = 0.5, hatch='\\'))
    elif circle == 1:
        b.add_patch(Circle((250,250), 100, alpha = 0.5, hatch = '\\'))
        
class myGui(tk.Tk):
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('1000x900+100+80')
        tk.Tk.wm_title(self, "ELEC 391 Gui")
        container = tk.Frame(self)
        
        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        
        self.frames = {}
        
        for F in (MainPage):
            
            frame = F(container,self)
            
            self.frames[F] = frame
            
            frame.grid(row=0, column = 0, sticky="nsew")
        
        self.show_frame(MainPage)
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()

def setshape(shape):
    global circle, square
    if shape == 1:
        square = 1
        circle = 0
    elif shape == 2:
        circle = 1
        square = 0
        
class MainPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
        button1 = ttk.Button(self, text="Main Page").place(x=0,y=0)
        button3 = ttk.Button(self, text="Square", command=lambda: setshape(1)).place(x=0,y=100)
        button4 = ttk.Button(self, text="Circle", command=lambda: setshape(2)).place(x=75,y=100)
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().place(x=0,y=200)
        
        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.place(x=0,y=150)
        
        Label(self, text="Failed Receive").place(x=700,y=300)

def close(event):
    Gui.withdraw()
    sys.exit()


def init_serial():
    ser = serial.Serial()
    ser.baudrate = 57600
    ser.port = 'COM6'
    ser.timeout = 0
    ser.open()
    return ser
    
def draw_square(x_coord,y_coord):
    w.delete(all)
    w.place(x=85+x_coord,y=725-y_coord)   

def main():
    global idx, rcvBuf, state, nextstate, changestate, success_count, fail_count, x_coord, y_coord

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
            else: #else discard bytes and change state back to waiting for startbyte
                fail_count = fail_count + 1
            changestate = True
            nextstate = 0
            
        if changestate:
            state = nextstate

        draw_square(x_coord, y_coord)
        
        
    Gui.after(1,main)

ser = init_serial()  
Gui = myGui()
w = tk.Canvas(Gui, bg = "blue", height=3, width=3, bd=1)
Gui.bind('<Escape>', close)
ani = animation.FuncAnimation(f,animate, interval=500)

Gui.after(1,main)

Gui.mainloop()

#dont want to use tk.canvas to display point. ideally want to use matplotlib function but too laggy right now
#fix scaling issues
#pause screen update     
#enter values to reposition shapes
#display information on side bar x,y for now
#more shapes
#images
#custom shapes
#print adc, pin states, internal voltage, temp (if any are applicable)        
        