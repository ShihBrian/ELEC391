import sys
import tkinter as tk
from tkinter import *
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import serial
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from enum import Enum
from matplotlib import style
import time
from scipy.optimize import fsolve
start_time = time.time()

wHeight = 508
wWidth = 501



style.use("ggplot")
f = Figure(figsize=(5.4,5.3), dpi=120)
a = f.add_subplot(111)
b = f.add_subplot(111)
a.set_xlim([-125,125])
a.set_ylim([0,125])
idx = 0
rcvBuf = [0]*6
changestate = False
success_count = 0
fail_count = 0
angle1 = 0
angle2 = 0
pause = 0
AL = 55
angle1 = 90
angle2 = 90
angle1_old = 0
angle2_old = 0

intersect_time = time.time()
intersect_delay = 1
#----------Communication Globals----------#
PauseByte = b"\xFE"
IntersectTrue = b"\xFF"
IntersectFalse = b"\xFD"
#-----------------------------------------#
x_c = 0
y_c = 0
class States(Enum):
    RxStart = 1
    RxXCoord = 2
    RxYCoord = 3
    RxEnd = 4

class Shape(Enum):
    Rectangle = 1
    Circle = 2

state = States.RxStart
nxtstate = States.RxStart

sqX=100
sqY=100
sqL=50
sqH=50
circR = 25
circX = 125
circY = 125
curr_shape = Shape.Rectangle

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
    global sqX, sqY, sqL, sqH, circX, circY, circR, curr_shape
    w.delete(ALL)
    curr_shape = shape
    if shape == Shape.Rectangle:
        w.create_rectangle(sqX*(wWidth/250),wHeight-sqY*(wHeight/125),(sqX+sqL)*(wWidth/250),\
                            wHeight-(sqY+sqH)*(wHeight/125), fill="lightblue")
        create_entry(Shape.Rectangle)
    if shape == Shape.Circle:
        w.create_oval((circX-circR)*(wWidth/250),wHeight-(circY-circR)*(wWidth/250),\
                      (circX+circR)*(wWidth/250),wHeight-(circY+circR)*(wWidth/250), fill="lightblue")
        create_entry(Shape.Circle)

bOnce = 1;
bOnce2 = 1;
def rectIntersect(pX, pY):
    global sqX, sqY, sqH, sqL, intersect_time, intersect_delay
    cTRx = sqX+sqL
    cBLy = sqY+sqH  
    if (pX >= sqX and pX <= cTRx) and (pY >= sqY and pY <= cBLy):
        Send_Intersect_Flag(TRUE)
        xLeft = pX - sqX
        xRight = cTRx - pX
        yUp = pY - sqY
        yDown = cBLy - pY
        minimum = min(xLeft,xRight,yUp,yDown)
        if xLeft == minimum:
            desired_x = sqX
            desired_y = pY
        elif xRight == minimum:
            desired_x = cTRx
            desired_y = pY
        elif yUp == minimum:
            desired_x = pX
            desired_y = sqY
        else:
            desired_x = pX
            desired_y = cBLy
        if time.time()-intersect_delay >= intersect_time:
            angle1, angle2 = inverse_kinematic(desired_x-125, desired_y)
            print(angle1, " ", angle2)
            ser.write(b"\xFB")
            ser.write(str(chr(int(angle1))).encode())
            ser.write(str(chr(int(angle2))).encode())
            ser.write(b"\xFA")
            intersect_time = time.time()
    else:
        Send_Intersect_Flag(FALSE)

def circIntersect(pX, pY):
    global circX, circY, circR
    distance = np.sqrt(np.square(circX-pX) + np.square(circY-pY))
    if distance < circR:
        Send_Intersect_Flag(TRUE)
        if circR-distance > 9:
            ser.write("9".encode())
        else:
            ser.write(str(int(circR-distance)).encode())
    else:
        Send_Intersect_Flag(FALSE)
        
def Send_Intersect_Flag(flag):
    global bOnce, bOnce2
    if flag:
        if bOnce:
            bOnce2 = 1
            ser.write(IntersectTrue)
            bOnce = 0
    else:
        if bOnce2:
            if start_time+1 < time.time():
                bOnce = 1
                ser.write(IntersectFalse)
                bOnce2 = 0   
                             
def create_entry(shape):
    global entryLength, entryHeight, entryX, entryY, XYLabel, LengthLabel, WidthLabel    
    if shape == Shape.Rectangle:
        LengthLabel.config(text="Length")
        XYLabel.config(text="Bottom Left XY")
        WidthLabel.config(text="Height")
        entryHeight.configure(state='normal')
    if shape == Shape.Circle:
        LengthLabel.config(text="Radius")
        XYLabel.config(text="Center XY")
        WidthLabel.config(text="")
        entryHeight.configure(state='disabled')
 
def entry_callback(event):
    global sqX, sqY, sqH, sqL, circR, circX, circY, curr_shape
    if len(entryX.get()) != 0:
        if curr_shape == Shape.Rectangle:
            sqX = int(entryX.get()) + 125
            sqY = int(entryY.get())
            sqL = int(entryLength.get())
            sqH = int(entryHeight.get())
        elif curr_shape == Shape.Circle:
            circR = int(entryLength.get())
            circX = int(entryX.get())
            circY = int(entryY.get())
        draw_constraint(curr_shape)        
     
def create_buttons(root):
    ttk.Button(root, text="Square", command=lambda: draw_constraint(Shape.Rectangle)).place(x=0,y=0)
    ttk.Button(root, text="Circle", command=lambda: draw_constraint(Shape.Circle)).place(x=75,y=0)
    ttk.Button(root, text="Pause", command=lambda: pause_update()).place(x=500,y=0)
    ttk.Button(root, text="Clear", command=lambda: clear()).place(x=575,y=0)

def create_labels(root):
    Label(root, text="Rx Count", font=("Courier", 18)).place(x=660,y=10)
    Label(root, text="X Pos", font=("Courier", 20)).place(x=660,y=40)
    Label(root, text="Y Pos", font=("Courier", 20)).place(x=660,y=70)
    Label(root, text="Angle 1", font=("Courier", 14)).place(x=685, y=160)
    Label(root, text="Angle 2", font=("Courier", 14)).place(x=785, y=160)
    
def init_window():
    root = Tk()
    root.geometry('900x700+600+80')
    tk.Tk.wm_title(root, "ELEC 391 GUI")
    canvas = FigureCanvasTkAgg(f, root)
    canvas.show()
    canvas.get_tk_widget().place(x=0,y=100)
    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.place(x=0,y=35)
    return root 
 
def init_serial():
    ser = serial.Serial()
    ser.baudrate = 115200
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
    ser.write(PauseByte)

def clear():
    global sqX, sqY, sqH, sqL
    sqX = sqY = 100
    sqH = sqL = 50
    w.delete(ALL)
   
def close(event):
    sys.exit()

def forward_kinematic(p):
    global angle1, angle2
    a,b = p
    f1 = AL - AL*math.cos(math.radians(angle2)) - AL*math.cos(b) - AL*math.cos(math.radians(angle1)) - AL*math.cos(a)
    f2 = AL*math.sin(math.radians(angle2)) + AL*math.sin(b) - AL*math.sin(math.radians(angle1)) - AL*math.sin(a)
    return(f1, f2)

def inverse_kinematic(x,y):
    left_base = x + AL/2
    right_base = AL/2 - x
    left_inner_length = math.sqrt(left_base**2 + y**2)
    right_inner_length = math.sqrt(right_base**2 + y**2)
    left_outer_angle = math.acos(left_inner_length**2/(2*AL*left_inner_length))
    right_outer_angle = math.acos(right_inner_length**2/(2*AL*right_inner_length))
    left_inner_angle = math.atan(y/left_base)
    right_inner_angle = math.atan(y/right_base)
    left_angle = math.degrees(left_outer_angle + left_inner_angle)
    right_angle = math.degrees(right_outer_angle + right_inner_angle)
    return left_angle, right_angle
    
def main():
    global idx, rcvBuf, state, nextstate, changestate, success_count, angle1, angle2, angle1_old, angle2_old, x_c, y_c
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
                angle1 = rcvBuf[0]
                angle2 = 180 - rcvBuf[1]
                stAngle1.set("%d", angle1)
                stAngle2.set("%d", angle2)
                if angle1_old != angle1 or angle2_old != angle2:
                    a,b = fsolve(forward_kinematic,(0,0))
                    x_c = int(AL*(math.cos(math.radians(angle1))+math.cos(a)))-(AL/2)
                    y_c = int(AL*(math.sin(math.radians(angle1))+math.sin(a))) 
                    stXCoord.set("%d", x_c)
                    stYCoord.set("%d", y_c)               
                    draw_point((x_c+125)*2,y_c*4.064)  
                    angle1_old = angle1
                    angle2_old = angle2
            #else discard bytes and change state back to waiting for startbyte
            changestate = True
            nextstate = States.RxStart
                
    if changestate:
        state = nextstate
        
    #-----------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------
    stRcvSuccess.set("%d", success_count)
    
    if curr_shape == Shape.Rectangle:
        rectIntersect(x_c+125, y_c)
    elif curr_shape == Shape.Circle:
        circIntersect(x_c, y_c)
    
    root.after(1,main)

#-----------------------------------------------------------------------------------------    
#-------------------------------------Initialization--------------------------------------
#-----------------------------------------------------------------------------------------    
ser = init_serial()  
root = init_window()
create_buttons(root)
create_labels(root)
stRcvSuccess = StatusBar(root)
stXCoord = StatusBar(root)
stYCoord = StatusBar(root)
stAngle1 = StatusBar(root)
stAngle2 = StatusBar(root)
stRcvSuccess.place(x=780,y=10)
stXCoord.place(x=780,y=40)
stYCoord.place(x=780,y=70)
stAngle1.place(x=670,y=120)
stAngle2.place(x=770,y=120)
w = Canvas(root, width=wWidth, height=wHeight, highlightthickness = 0)
w.place(x=82,y=98)
rect = w.create_rectangle(0,0,0,0, fill="blue")
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
entryX = Entry(root, width = 5)
entryX.place(x=760,y=200)
entryY = Entry(root, width = 5)
entryY.place(x=800,y=200)
entryLength = Entry(root, width = 5)
entryLength.place(x=760, y=225)
entryHeight = Entry(root, width = 5)
entryHeight.place(x=760, y=250)
XYLabel = Label(root)
XYLabel.place(x=660,y=200)
LengthLabel = Label(root)
LengthLabel.place(x=660,y=225)
WidthLabel = Label(root)
WidthLabel.place(x=660,y=250)
Label(root, text="Press Enter To Set", font = "Courier 16 bold").place(x=660, y=280)
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
draw_constraint(Shape.Rectangle)
root.bind('<Escape>', close)
root.bind('<Return>', entry_callback)
root.after(1,main)
root.mainloop()

#more shapes
#images
#custom shapes
#print adc, pin states, internal voltage, temp (if any are applicable)      
#add length option in receive protocol  
#display extension length of actuator
#multiple shapes at once
#bind keys to do something
#choose spring, wall, button, etc 