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


#==============Plot Globals===============#
wHeight = 508
wWidth = 501
x_range = 160
y_start = 0
y_end = 140
y_range = y_end - y_start
style.use("ggplot")
f = Figure(figsize=(5.4,5.3), dpi=120)
a = f.add_subplot(111)
b = f.add_subplot(111)
a.set_xlim([-1*x_range/2,x_range/2])
a.set_ylim([y_start,y_end])
x_c = 0
y_c = 0
AL = 70
angle1 = 90
angle2 = 90
x_conv =(wWidth/x_range)
y_conv = (wWidth/y_range)
mouse_x = 0
mouse_y = 0
#=========================================#

#=========Communication Globals===========#
class States(Enum):
    RxStart = 1
    RxMsgType = 2
    RxMsgLength = 3
    RxMsg = 4
    RxEnd = 5
    
class eMsgType(Enum):
    encoderPosLeft = 1
    encoderPosRight = 2
    desiredLeft = 3
    desiredRight = 4
    debug = 5
    start =6;
    
PauseByte = b"\xFE"
IntersectTrue = b"\xFF"
IntersectFalse = b"\xFD"
MsgType = 0
state = States.RxStart
nxtstate = States.RxStart
MsgLength = 0
Startbyte = 255
EndByte = 254
success_count = 0
startrx= 0;
#==========================================#

#===========Constraint Globals=============#
class Shape(Enum):
    Rectangle = 1
    Circle = 2
    
sqX=-15
sqY=85
sqL=30
sqH=40
default_sqX=-15
default_sqY=85
default_sqL=30
default_sqH=40
circR = 25
circX = 125
circY = 125
curr_shape = Shape.Rectangle
manual_pos = 0;
#==========================================#

#==============PID Globals=================#
P = 10;
I = 0;
D = 1;
Wall_P = 100
Wall_D = 10
Spring_P = 10
Spring_D = 0
Damper_P = 10
Damper_D = 1
#==========================================#
pause = 0
intersect_time = time.time()
intersect_delay = 1
start_time = time.time()
start_time2 = time.time()*1000
time2_delay = 250

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

def draw_constraint(shape, sqX, sqY, sqL, sqH): 
    global circX, circY, circR, curr_shape, rectangle, manual_pos
    manual_pos = 0
    w.delete(rectangle)
    curr_shape = shape
    sqX = abs(sqX+x_range/2)
    if shape == Shape.Rectangle:
        rectangle = w.create_rectangle(sqX*x_conv,wHeight-sqY*y_conv+(y_conv*y_start),(sqX+sqL)*x_conv,\
                            wHeight-(sqY+sqH)*y_conv+(y_conv*y_start), fill="lightblue")
        create_entry(Shape.Rectangle)
    if shape == Shape.Circle:
        circle = w.create_oval((circX-circR)*x_conv,wHeight-(circY-circR)*y_conv,\
                      (circX+circR)*(wWidth/150),wHeight-(circY+circR)*(wWidth/150), fill="lightblue")
        create_entry(Shape.Circle)

bOnce = 1;
bOnce2 = 1;
def rectIntersect(pX, pY):
    global sqX, sqY, sqH, sqL, intersect_time, intersect_delay,start_time2
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
            desired_x = sqX-4
            desired_y = pY
        elif xRight == minimum:
            desired_x = cTRx+4
            desired_y = pY
        elif yUp == minimum:
            desired_x = pX
            desired_y = sqY-4
        else:
            desired_x = pX
            desired_y = cBLy+4
        if start_time2+time2_delay < time.time()*1000:
            angle1, angle2 = inverse_kinematic(desired_x, desired_y)
            stDesired1.set("%d", angle1)
            stDesired2.set("%d", angle2)            
            ser.write(b"\xFB")
            value = [int(angle1)]
            angle = bytes(value)
            ser.write(angle)
            value = [int(angle2)]
            angle = bytes(value)
            ser.write(angle)
            ser.write(b"\xFA")
            start_time2 = time.time()*1000
    else:
        Send_Intersect_Flag(FALSE)
        stDesired1.set("%s", "")
        stDesired2.set("%s", "")

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
                             
def create_entry(type):
    global entryLength, entryHeight, entryX, entryY, XYLabel, LengthLabel, WidthLabel   
    if type == Shape.Rectangle:
        LengthLabel.config(text="Length")
        XYLabel.config(text="Bottom Left XY")
        WidthLabel.config(text="Height")
        entryHeight.configure(state='normal')
    if type == Shape.Circle:
        LengthLabel.config(text="Radius")
        XYLabel.config(text="Center XY")
        WidthLabel.config(text="")
        entryHeight.configure(state='disabled')
        
 
def entry_callback(event):
    global sqX, sqY, sqH, sqL, circR, circX, circY, curr_shape, P, I, D
    if len(entryX.get()) != 0:
        if curr_shape == Shape.Rectangle:
            sqX = int(entryX.get())
            sqY = int(entryY.get())
            sqL = int(entryLength.get())
            sqH = int(entryHeight.get())
        elif curr_shape == Shape.Circle:
            circR = int(entryLength.get())
            circX = int(entryX.get())
            circY = int(entryY.get())
        draw_constraint(curr_shape, sqX, sqY, sqL, sqH) 
    if len(entryP.get()) != 0:
        Set_PID(entryP.get(),entryI.get(),entryD.get())

def Set_PID(P,I,D):
    txP = [int(P)]
    txI = [int(I)]
    txD = [int(D)]
    ser.write(b"\xFC")
    ser.write(txP)
    ser.write(txI)
    ser.write(txD)
    
def create_buttons(root):
    ttk.Button(root, text="Square", command=lambda: draw_constraint(Shape.Rectangle, default_sqX, default_sqY, default_sqL, default_sqH)).place(x=0,y=0)
    ttk.Button(root, text="Circle", command=lambda: draw_constraint(Shape.Circle)).place(x=75,y=0)
    ttk.Button(root, text="Pause", command=lambda: pause_update()).place(x=500,y=0)
    ttk.Button(root, text="Clear", command=lambda: clear()).place(x=575,y=0)
    ttk.Button(root, text="Wall", command=lambda: Set_PID(Wall_P, 0, Wall_D)).place(x=660,y=500)
    ttk.Button(root, text="Spring", command=lambda: Set_PID(Spring_P, 0, Spring_D)).place(x=740,y=500)
    ttk.Button(root, text="Button", command=lambda: Set_PID(Damper_P, 0, Damper_D)).place(x=820,y=500)

def create_labels(root):
    Label(root, text="Rx Count", font=("Courier", 18)).place(x=660,y=10)
    Label(root, text="X Pos", font=("Courier", 20)).place(x=660,y=40)
    Label(root, text="Y Pos", font=("Courier", 20)).place(x=660,y=70)
    Label(root, text="Angle 1", font=("Courier", 14)).place(x=685, y=155)
    Label(root, text="Angle 2", font=("Courier", 14)).place(x=785, y=155)
    Label(root, text="Desired1", font=("Courier", 14)).place(x=670, y=215)
    Label(root, text="Desired2", font=("Courier", 14)).place(x=780, y=215)
    
def init_window():
    root = Tk()
    root.geometry('900x700+200+80')
    tk.Tk.wm_title(root, "ELEC 391 GUI")
    canvas = FigureCanvasTkAgg(f, root)
    canvas.show()
    canvas.get_tk_widget().place(x=0,y=100)
    toolbar = NavigationToolbar2TkAgg(canvas, root)
    toolbar.update()
    canvas._tkcanvas.place(x=0,y=35)
    canvas.callbacks.connect('button_press_event', on_click)
    return root 
 
def init_serial():
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = 'COM4'
    ser.timeout = 1
    ser.open()
    return ser

def draw_point(x,y):
    global rect, pause, angle2, line1,line2,line3,line4, x_conv, y_conv, restrict
    if pause == 0:
        w.delete(rect)
        w.delete(line1)
        w.delete(line2)
        w.delete(line3)
        w.delete(line4)
        w.delete(restrict)
        line1x = x_conv*((x_range/4)+AL*math.cos(math.radians(angle1)))
        line1y = wHeight-y_conv*(AL*math.sin(math.radians(angle1)))
        line2x = x_conv*((x_range*0.75)+AL*math.cos(math.radians(180-angle2)))
        line2y = wHeight-y_conv*(AL*math.sin(math.radians(180-angle2)))
        restrict = w.create_rectangle(0,wHeight-100*y_conv+(y_conv*y_start),wWidth,wHeight, fill = "light salmon", outline = "")
        rect = w.create_rectangle(x-1,wHeight-y-1,x+3,wHeight-y+3, outline="")
        line1 = w.create_line(x_conv*(x_range/4), wHeight+(y_conv*y_start), line1x, line1y+(y_conv*y_start), width=4 )
        line2 = w.create_line(x_conv*(x_range*0.75), wHeight+(y_conv*y_start), line2x, line2y+(y_conv*y_start), width=4 )
        line3 = w.create_line(line1x, line1y+(y_conv*y_start),x,wHeight-y+(y_conv*y_start), width=4 )
        line4 = w.create_line(line2x, line2y+(y_conv*y_start),x, wHeight-y+(y_conv*y_start), width=4 )
        
def pause_update():
    ser.write(PauseByte)

def clear():
    global sqX, sqY, sqH, sqL
    sqX = sqY = 0
    sqH = sqL = 0
    w.delete(ALL)
   
def close(event):
    sys.exit()

def on_click(event):
    global mouse_x, mouse_y, manual_pos, sqX, sqY, sqL, sqH
    mouse_x = event.x
    mouse_y = event.y
    print(mouse_x/x_conv - (x_range/2),y_end-mouse_y/y_conv)
    manual_pos = 1
    sqX = sqY = sqL = sqH = 0
    Set_PID(10,0,1)
    angle1, angle2 = inverse_kinematic(mouse_x/x_conv - (x_range/2), y_end-mouse_y/y_conv)
    print(angle1, angle2)
    ser.write(b"\xFB")
    value = [int(angle1)]
    angle = bytes(value)
    ser.write(angle)
    value = [int(angle2)]
    angle = bytes(value)
    ser.write(angle)
    ser.write(b"\xFA")
    Send_Intersect_Flag(TRUE)
    
def forward_kinematic(p):
    global angle1, angle2
    alpha,beta = p
    f1 = AL - AL*math.cos(math.radians(angle2)) - AL*math.cos(beta) - AL*math.cos(math.radians(angle1)) - AL*math.cos(alpha)
    f2 = AL*math.sin(math.radians(angle2)) + AL*math.sin(beta) - AL*math.sin(math.radians(angle1)) - AL*math.sin(alpha)
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

def fk_solve():
    global x_c, y_c, angle1, angle2
    a,b = fsolve(forward_kinematic,(0,0))
    x_c = AL*(math.cos(math.radians(angle1))+math.cos(a))-(AL/2)
    y_c = AL*(math.sin(math.radians(angle1))+math.sin(a))    
    stXCoord.set("%d", x_c)
    stYCoord.set("%d", y_c)               
    draw_point(x_conv*(x_c+(x_range/2)), y_conv*y_c)
 
def MsgHandler(Msgtype, data):
    global angle1, angle2, startrx
    if Msgtype == eMsgType.encoderPosLeft:
        if startrx == 1:
            angle1 = data*0.9
            stAngle1.set("%.1lf", angle1)
            fk_solve()
    elif Msgtype == eMsgType.encoderPosRight:
        if startrx == 1:       
            angle2 = data*0.9
            stAngle2.set("%.1lf", angle2)
            fk_solve()  
    elif Msgtype == eMsgType.desiredLeft:
        #stDesired1.set("%d", data)
        pass
    elif Msgtype == eMsgType.desiredRight:
        #stDesired2.set("%d", data)
        pass
    elif Msgtype == eMsgType.debug:
        print(data)
    elif Msgtype == eMsgType.start:
        startrx = 1;
        
def main():
    global state, success_count, x_c, y_c, MsgLength, MsgType, data, manual_pos, mouse_x, mouse_y
    #-----------------------------------------------------------------------------------------    
    #-------------------------Transfer Protocol State Machine---------------------------------
    #-----------------------------------------------------------------------------------------
    if ser.inWaiting()>0:
        if state == States.RxStart: #waiting to receive startbyte
            x = int(ser.read(2),16)
            if x == Startbyte: #received startbyte
                state = States.RxMsgType
        elif state == States.RxMsgType: #receive msg type, 1 byte
            x = int(ser.read(1),16)
            if x == 1:
                MsgType = eMsgType.encoderPosLeft
            elif x == 2:
                MsgType = eMsgType.encoderPosRight
            elif x == 3:
                MsgType = eMsgType.desiredLeft
            elif x == 4:
                MsgType = eMsgType.desiredRight
            elif x == 5:
                MsgType = eMsgType.debug
            elif x == 6:
                MsgType = eMsgType.start
            state = States.RxMsgLength
        elif state == States.RxMsgLength: #receive message length, 1 byte
            x = int(ser.read(1),16)
            MsgLength = x
            if(MsgLength): #if msg length is 0, rx fail and reset to wait for start
                state = States.RxMsg
            else:
                state = States.RxStart
        elif state == States.RxMsg: #receive msg length bytes of data 
            data = int(ser.read(MsgLength),16)
            state = States.RxEnd
        elif state == States.RxEnd: #wait for endbyte, if received proceed to handle message, else go back to start          
            x = int(ser.read(2),16)
            if x == EndByte: #if endbyte is received then update x,y coordinate
                success_count = success_count + 1
                MsgHandler(MsgType, data)
            #else discard bytes and change state back to waiting for startbyte
            state = States.RxStart                         
    #-----------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------
    
    stRcvSuccess.set("%d", success_count)
    
    if not manual_pos:
        if curr_shape == Shape.Rectangle:
            rectIntersect(x_c, y_c)
        elif curr_shape == Shape.Circle:
            circIntersect(x_c, y_c)
    if manual_pos == 1:
        print(abs(x_c-(mouse_x/x_conv - (x_range/2))),abs(y_c-(y_end-mouse_y/y_conv)))
        if(abs(x_c-(mouse_x/x_conv - (x_range/2))) <2 and abs(y_c-(y_end-mouse_y/y_conv))<2):
            Send_Intersect_Flag(FALSE)
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
stDesired1 = StatusBar(root)
stDesired2 = StatusBar(root)
stRcvSuccess.place(x=780,y=10)
stXCoord.place(x=780,y=40)
stYCoord.place(x=780,y=70)
stAngle1.place(x=670,y=120)
stAngle2.place(x=770,y=120)
stDesired1.place(x=670, y=180)
stDesired2.place(x=770, y=180)
w = Canvas(root, width=wWidth, height=wHeight, highlightthickness = 0)
w.place(x=82,y=98)
rect = w.create_rectangle(0,0,0,0, fill="blue")
line1 = w.create_line(0,0,0,0)
line2 = w.create_line(0,0,0,0)
line3 = w.create_line(0,0,0,0)
line4 = w.create_line(0,0,0,0)
restrict = w.create_rectangle(0,0,0,0)
rectangle = w.create_rectangle(0,0,0,0)
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
entryX = Entry(root, width = 5)
entryX.place(x=760,y=300)
entryY = Entry(root, width = 5)
entryY.place(x=800,y=300)
entryLength = Entry(root, width = 5)
entryLength.place(x=760, y=325)
entryHeight = Entry(root, width = 5)
entryHeight.place(x=760, y=350)
entryP = Entry(root,width =5)
entryP.place(x=710, y= 450)
entryI = Entry(root,width =5)
entryI.place(x=760, y= 450)
entryD = Entry(root,width =5)
entryD.place(x=810, y= 450)
XYLabel = Label(root)
XYLabel.place(x=660,y=300)
LengthLabel = Label(root)
LengthLabel.place(x=660,y=325)
WidthLabel = Label(root)
WidthLabel.place(x=660,y=350)
PIDLabel = Label(root)
PIDLabel.place(x=720,y=470)
PIDLabel.config(text="P    I    D", font = "Courier 12 bold")
Label(root, text="Press Enter To Set", font = "Courier 12 bold").place(x=660, y=380)
Label(root, text="Constraint Region", font = "Courier 12 bold").place(x=660, y=270)
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
draw_constraint(Shape.Rectangle, default_sqX, default_sqY, default_sqL, default_sqH)
root.bind('<Escape>', close)
root.bind('<Return>', entry_callback)
w.bind('<Button-1>', on_click)
root.after(1,main)
root.mainloop()

#more shapes
#images
#custom shapes   
#multiple shapes at once
#bind keys to do something
#choose spring, wall, button, etc 
#keep in/keep out