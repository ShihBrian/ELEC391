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
from collections import deque
import argparse
import imutils
import cv2
from PIL import ImageTk, Image
from pyimagesearch.shapedetector import ShapeDetector
from operator import xor
#==============Plot Globals===============#
wHeight = 508
wWidth = 501
x_range = 250
y_start = 0
y_end = 250
y_range = y_end - y_start
style.use("ggplot")
f = Figure(figsize=(5.4,5.3), dpi=120)
a = f.add_subplot(111)
b = f.add_subplot(111)
a.set_xlim([-1*x_range/2,x_range/2])
a.set_ylim([y_start,y_end])
x_c = 0
y_c = 0
left_length = 50
right_length = 50
base_length = 225  
coil_length = 80
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
    
sqX=-20
sqY=90
sqL=40
sqH=40
default_sqX=-20
default_sqY=90
default_sqL=40
default_sqH=40
circR = 10
circX = 0
circY = 100
curr_shape = Shape.Rectangle
manual_pos = 0;
#==========================================#

#==============PID Globals=================#
P = 10;
I = 0;
D = 1;
Wall_P = 45
Wall_D = 0
Spring_P = 20
Spring_D = 0
Damper_P = 0
Damper_D = 100
#==========================================#
pause = 0
intersect_delay = 1
start_time = time.time()
start_time2 = time.time()*1000
time2_delay = 10
bOnce = 1;
bOnce2 = 1;
start_time3 = time.time()*1000
time3_delay = 10
bOnce3 = 1
start_time_manual = time.time()*1000
time_delay_manual = 100

Camera_Toggle = 0

first_start = 0;

default_P = 45
default_I = 0
default_D = 0

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
        
def draw_constraint(shape, sqX1, sqY1, sqL1, sqH1): 
    global circX, circY, circR, curr_shape, rectangle, manual_pos, circle_C,sqX, sqY, sqL, sqH
    manual_pos = 0
    w.delete(rectangle)
    w.delete(circle_C)
    sqX = sqX1
    sqY = sqY1
    sqH = sqH1
    sqL = sqL1
    curr_shape = shape
    if shape == Shape.Rectangle:
        rectangle = w.create_rectangle(abs(sqX+(x_range/2))*x_conv,wHeight-sqY*y_conv+(y_conv*y_start),abs((sqX+(x_range/2)+sqL))*x_conv,\
                            wHeight-(sqY+sqH)*y_conv+(y_conv*y_start), fill="lightblue")
        create_entry(Shape.Rectangle)
    if shape == Shape.Circle:
        circle_C = w.create_oval((circX-circR+x_range/2)*x_conv,wHeight-(circY-circR)*y_conv,\
                      (circX+circR+x_range/2)*x_conv,wHeight-(circY+circR)*y_conv, fill="lightblue")
        create_entry(Shape.Circle)
        
def rectIntersect(pX, pY):
    global sqX, sqY, sqH, sqL,start_time2,start_time3, bOnce3, damper_once
    cTRx = sqX+sqL
    cBLy = sqY+sqH 
    if (pX >= sqX and pX <= cTRx) and (pY >= sqY and pY <= cBLy):
        Send_Intersect_Flag(TRUE)
        bOnce3 = 1
        xLeft = pX - sqX
        xRight = cTRx - pX
        yUp = pY - sqY
        yDown = cBLy - pY
        minimum = min(xLeft,xRight,yUp,yDown)
        if xLeft == minimum:
            desired_x = sqX-2
            desired_y = pY
        elif xRight == minimum:
            desired_x = cTRx+2
            desired_y = pY
        elif yUp == minimum:
            desired_x = pX
            desired_y = sqY-2
        else:
            desired_x = pX
            desired_y = cBLy+2
        send_desired(desired_x, desired_y)
    else:
        if bOnce3:
            start_time3 = time.time()*1000
            bOnce3 = 0
        elif start_time3+time3_delay < time.time()*1000:
            if (damper_once == 1):
                Send_Intersect_Flag(FALSE)
                stDesired1.set("%s", "")
                stDesired2.set("%s", "")
            start_time3 = time.time()*1000

damper_once = 1
last_x = -45
last_y = 120
def work_area(pX, pY):
    global last_x, last_y, damper_once
    if(pX > 36 or pX < -36):
        if(damper_once):
            Set_PID(0,0,30)
            Send_Intersect_Flag(TRUE)
            damper_once = 0
            last_x = pX
            last_y = pY
        else:
            send_desired(last_x, last_y)
    elif(pY>150 or pY < 72):
        if(damper_once):
            Set_PID(0,0,30)
            Send_Intersect_Flag(TRUE)
            damper_once = 0
            last_x = pX
            last_y = pY
        else:
            send_desired(last_x, last_y)
            last_x = pX
            last_y = pY
    else:
        if(damper_once == 0):
            Send_Intersect_Flag(FALSE)
            Set_PID(default_P, default_I, default_D)
            damper_once = 1

def circIntersect(pX, pY):
    global circX, circY, circR, start_time3, bOnce3, damper_once
    distance = np.sqrt(np.square(circX-pX) + np.square(circY-pY))
    if distance < circR:
        Send_Intersect_Flag(TRUE)
        desired_x = circX + circR*((pX-circX)/np.sqrt((pX-circX)**2+(pY-circY)**2))
        desired_y = circY + circR*((pY-circY)/np.sqrt((pX-circX)**2+(pY-circY)**2))
        print(desired_x, desired_y)
        left_length, right_length = inverse_kinematic(desired_x, desired_y)
        send_desired(desired_x, desired_y)
    else:
        if bOnce3:
            start_time3 = time.time()*1000
            bOnce3 = 0
        elif start_time3+time3_delay < time.time()*1000:
            if (damper_once == 1):
                Send_Intersect_Flag(FALSE)
                stDesired1.set("%s", "")
                stDesired2.set("%s", "")
            start_time3 = time.time()*1000

def send_desired(desired_x,desired_y):
    global start_time2,start_time3, bOnce3  
    if start_time2+time2_delay < time.time()*1000:
        left_length1, right_length1 = inverse_kinematic(desired_x, y_end-desired_y+4)
        stDesired1.set("%d", (left_length1-120)*2)
        stDesired2.set("%d", (right_length1-120)*2)            
        ser.write(b"\xFB")
        value = [int((left_length-120))*2]
        length = bytes(value)
        ser.write(length)
        value = [int((right_length1-120))*2]
        length = bytes(value)
        ser.write(length)
        ser.write(b"\xFA")
        start_time2 = time.time()*1000
        
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

def ToggleCamera():
    global Camera_Toggle, camera
    if Camera_Toggle == 0:
        Camera_Toggle = 1
        clear()
        Set_PID(40,0,5)
        if not args.get("video", False):
            camera = cv2.VideoCapture(1)
    else:
        Camera_Toggle = 0
        camera.release()
        cv2.destroyAllWindows()
        Send_Intersect_Flag(FALSE)
        clear()
    
def create_buttons(root):
    global frame
    ttk.Button(root, text="Square", command=lambda: draw_constraint(Shape.Rectangle, default_sqX, default_sqY, default_sqL, default_sqH)).place(x=0,y=0)
    ttk.Button(root, text="Circle", command=lambda: draw_constraint(Shape.Circle, circX, circY, circR, 0)).place(x=75,y=0)
    ttk.Button(root, text="Stop", command=lambda: Stop()).place(x=500,y=0)
    ttk.Button(root, text="Clear", command=lambda: clear()).place(x=575,y=0)
    ttk.Button(root, text="Wall", command=lambda: Set_PID(Wall_P, 0, Wall_D)).place(x=660,y=500)
    ttk.Button(root, text="Spring", command=lambda: Set_PID(Spring_P, 0, Spring_D)).place(x=740,y=500)
    ttk.Button(root, text="Damper", command=lambda: Set_PID(Damper_P, 0, Damper_D)).place(x=820,y=500)
    ttk.Button(root, text="Camera On/Off",command=lambda: ToggleCamera()).place(x=409,y=0)
    ttk.Button(root, text="Eight", command=lambda: set_path(1)).place(x=333, y=0)
    ttk.Button(root, text="Manual Pos", command=lambda: manual_position(1)).place(x=150, y=0)
    ttk.Button(root, text="Star", command=lambda: set_path(2)).place(x=258, y=0)
    ttk.Button(root, text="100%", command=lambda: set_path(4)).place(x=660, y=550)
    ttk.Button(root, text="Custom Path", command=lambda: set_path(3)).place(x=660, y=600)

def create_labels(root):
    Label(root, text="Rx Count", font=("Courier", 18)).place(x=660,y=10)
    Label(root, text="X Pos", font=("Courier", 20)).place(x=660,y=40)
    Label(root, text="Y Pos", font=("Courier", 20)).place(x=660,y=70)
    Label(root, text="Ext Left", font=("Courier", 14)).place(x=670, y=155)
    Label(root, text="Ext Right", font=("Courier", 14)).place(x=770, y=155)
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
    global rect, pause, right_length, line1,line2,line3,line4, x_conv, y_conv,circle
    if pause == 0:
        w.delete(rect)
        w.delete(line1)
        w.delete(line2)
        w.delete(line3)
        w.delete(line4)
        w.delete(circle)
        angleleft = math.atan(y/(base_length/2+x))
        left_x = coil_length*math.cos(angleleft)
        left_y = coil_length*math.sin(angleleft)
        angleright = math.atan(y/(base_length/2-x))
        right_x = coil_length*math.cos(angleright)
        right_y = coil_length*math.sin(angleright)
        rect = w.create_rectangle(x-1,wHeight-y-1,x+3,wHeight-y+3, outline="")
        left_base_pos = (x_range/2)-(base_length/2)
        right_base_pos = (x_range/2)+(base_length/2)
        line1 = w.create_line(x_conv*left_base_pos,(y_conv*y_start), \
                              x_conv*(x+x_range/2),(y)*y_conv, width=4 )
        line2 = w.create_line(x_conv*right_base_pos,(y_conv*y_start), \
                              x_conv*(x+x_range/2), (y)*y_conv, width=4 )
        line3 = w.create_line(x_conv*left_base_pos, -3+(y_conv*y_start), \
                              x_conv*(left_base_pos+left_x),(left_y)*y_conv, width=15, fill='red' )
        line4 = w.create_line(x_conv*right_base_pos, -3+(y_conv*y_start), \
                              x_conv*(right_base_pos-right_x),(right_y)*y_conv, width=15, fill='red' )
        circle = w.create_oval((x-1.5+x_range/2)*x_conv, (y-1.5)*y_conv,\
                               (x+1.5+x_range/2)*x_conv, (y+1.5)*y_conv, fill='green')
        
        
def pause_update():
    ser.write(PauseByte)

def clear():
    global sqX, sqY, sqH, sqL, manual_pos, custom_path
    #custom_path = []
    sqX = sqY = 0
    manual_pos = 0
    sqH = sqL = 0
    w.delete(ALL)
    init_regions()
   
def close(event):
    Stop()
    Send_Intersect_Flag(FALSE)
    clear()
    sys.exit()

def Stop():
    global bpath, custom_path
    custom_path = []
    init_regions()
    bpath = 0
    
def on_click(event):
    global mouse_x, mouse_y, manual_pos, sqX, sqY, sqL, sqH
    if manual_pos:
        mouse_x = (event.x/x_conv)-x_range/2
        mouse_y = event.y/y_conv
        sqX = sqY = sqL = sqH = 0
        w.create_oval((mouse_x-1+x_range/2)*x_conv,(mouse_y+1)*y_conv,(mouse_x+1+x_range/2)*x_conv,(mouse_y-1)*y_conv)
        left_length, right_length = inverse_kinematic(mouse_x,mouse_y)
        left_length = (left_length-120)*2
        right_length = (right_length-120)*2
        ser.write(b"\xFB")
        value = [int(left_length)]
        angle = bytes(value)
        ser.write(angle)
        value = [int(right_length)]
        angle = bytes(value)
        ser.write(angle)
        ser.write(b"\xFA")
        Send_Intersect_Flag(TRUE)


custom_path = []
def on_drag(event):
    global custom_path, drag_timer
    if not manual_pos:
        x = (event.x/x_conv)-x_range/2
        y = y_end-event.y/y_conv
        pos = [int(x),int(y+4)]
        if not custom_path:
            custom_path.append(pos)
            circle = w.create_oval((x-1.5+x_range/2)*x_conv, (y_end-y-1.5)*y_conv,\
                           (x+1.5+x_range/2)*x_conv, (y_end-y+1.5)*y_conv, fill='red')
        elif not(custom_path[-1][0] == pos[0] and custom_path[-1][1] == pos[1]):
            custom_path.append(pos)
            circle = w.create_oval((x-1.5+x_range/2)*x_conv, (y_end-y-1.5)*y_conv,\
                           (x+1.5+x_range/2)*x_conv, (y_end-y+1.5)*y_conv, fill='red')
                  
def manual_position(flag):
    global manual_pos
    clear()
    manual_pos = 1
    Set_PID(50,0,5)

path_point = 0
path_length = 0
bpath = 0;
path = 1
last_x2 = 0
last_y2 = 0
def draw_path(flag,x,y):
    global last_x2, last_y2
    if flag and not last_x2 == x and not last_y2 == y:
        circle = w.create_oval((x-1.5+x_range/2)*x_conv, (y-1.5)*y_conv,\
                       (x+1.5+x_range/2)*x_conv, (y+1.5)*y_conv, fill='blue')
        last_x2 = x
        last_y2 = y
 
count = 0  
path_list = []  
def draw_path2(flag):
    global x_c, y_c, count, path_list
    count = count+1
    if flag and count > 30:
        x=x_c
        y=y_c-4
        circle = w.create_oval((x-1.5+x_range/2)*x_conv, (y_end-y-1.5)*y_conv,\
                       (x+1.5+x_range/2)*x_conv, (y_end-y+1.5)*y_conv, fill='red')
        path_list.insert(0,circle)
        if(len(path_list)>100):
            w.delete(path_list[-1])
            path_list.pop()
        count = 0
        
def prescribed_path(path_x):
    global path_point, manual_pos, bpath
    path_length = len(path_x)
    if path_point == 0:
        w.delete(ALL)
    if(path_point < path_length):
        go_to_pos(path_x[path_point][0], y_end-path_x[path_point][1])
        draw_path2(1)
        draw_path(1,path_x[path_point][0], y_end-path_x[path_point][1])
    else:
        Send_Intersect_Flag(TRUE)
        path_point = 0
        go_to_pos(path_x[0][0], y_end-path_x[0][1])
        time.sleep(1)
        w.delete(ALL)

def go_to_pos(x,y):
    Send_Intersect_Flag(TRUE)
    left_length, right_length = inverse_kinematic(x,y)
    left_length = (left_length-120)*2
    right_length = (right_length-120)*2
    ser.write(b"\xFB")
    value = [int(left_length)]
    angle = bytes(value)
    ser.write(angle)
    value = [int(right_length)]
    angle = bytes(value)
    ser.write(angle)
    ser.write(b"\xFA")     
                   
def set_path(p):
    global bpath, path, curr_path
    clear()
    bpath = 1
    path = p
    if(path==1):
        Set_PID(50,0,3)
        go_to_pos(eight_path[0][0], y_end-eight_path[0][1])
        time.sleep(0.7)
        curr_path = eight_path
        prescribed_path(eight_path)
        w.delete(ALL)
    elif(path==2):
        Set_PID(50,0,3)
        go_to_pos(star_path[0][0], y_end-star_path[0][1])
        time.sleep(0.7)
        curr_path = star_path
        prescribed_path(star_path)
        w.delete(ALL)
    elif(path==3):
        Set_PID(55,0,5)
        #go_to_pos(pts[0][0]*x_scale+(-36), pts[0][1]*y_scale + 72)
        #o_to_pos(custom_path[0][0], y_end-custom_path[0][1])
        
        time.sleep(0.7)
        curr_path = custom_path
        prescribed_path(custom_path)
        w.delete(ALL)
    elif(path==4):
        Set_PID(30,0,5)
        go_to_pos(E_path[0][0], y_end-E_path[0][1])
        time.sleep(0.7)
        curr_path = E_path
        prescribed_path(custom_path)
        w.delete(ALL)       

def forward_kinematic(right_length, left_length):
    global x_c, y_c, base_length
    left_angle = CosLaw(right_length,left_length, base_length)
    y_c = left_length*math.sin(left_angle)
    x_c = left_length*math.cos(left_angle) - base_length/2;
    return(x_c,y_c)

def inverse_kinematic(x,y):
    global base_length
    height = y
    width = (base_length/2)+x
    left_length = math.sqrt(height**2+width**2)
    width = (base_length/2)-x
    right_length = math.sqrt(height**2+width**2)
    return left_length, right_length

def CosLaw(desired_l,a,b):
    angle = (a**2 + b**2 - desired_l**2)/(2*a*b)
    return math.acos(angle)
 
def MsgHandler(Msgtype, data):
    global left_length, right_length, startrx,x_c,y_c, first_start
    if Msgtype == eMsgType.encoderPosLeft:
        if startrx == 1:
            left_length = ((data/2)+40)+coil_length
            stleft_length.set("%.1lf", data)
    elif Msgtype == eMsgType.encoderPosRight:
        if startrx == 1:       
            right_length = ((data/2)+40)+coil_length
            x,y = forward_kinematic(right_length, left_length)
            stXCoord.set("%.1lf", x)
            stYCoord.set("%.1lf", y_end-y+4)
            stright_length.set("%.1lf", data)
            draw_point(x,y)
            x_c = x
            y_c = y_end-y+4
    elif Msgtype == eMsgType.desiredLeft:
        #stDesired1.set("%d", data)
        pass
    elif Msgtype == eMsgType.desiredRight:
        #stDesired2.set("%d", data)
        pass
    elif Msgtype == eMsgType.debug:
        print(data)
    elif Msgtype == eMsgType.start:
        if(first_start==0):
            Set_PID(40,0,3)
            ser.write(b"\xEF")
            first_start = 1
        if (first_start):
            startrx = 1;


camera_count = 0
start_delay = 0
frame = 0
def main():
    global state, success_count, x_c, y_c, MsgLength, MsgType, data, manual_pos, mouse_x, mouse_y, y_coordinate, x_coordinate
    global start_time_manual, Camera_Toggle, startrx, bpath, path_point, path_length, path, camera_count, start_delay, frame
    #-----------------------------------------------------------------------------------------    
    #-------------------------Transfer Protocol State Machine---------------------------------
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
    #-----------------------------OpenCV Object Tracking--------------------------------------
    if Camera_Toggle:
        if(start_delay > 299):
            draw_path2(1)
        if camera_count > 10:
            # grab the current frame
            (grabbed, frame) = camera.read()
        
            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if args.get("video") and not grabbed:
                print("Asds")
         
            # resize the frame, blur it, and convert it to the HSV
            # color space
            frame = imutils.resize(frame, width=600)
            # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
         
            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            mask = cv2.inRange(hsv, greenLower, greenUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
         
            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
         
                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(frame, (int(x), int(y)), int(radius),
                        (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 0, 255), -1)
         
            # update the points queue
            if center is not None:
                manual_pos = 1
                if (start_delay > 199):
                    pts.appendleft(center)
                    go_to_pos((pts[0][0]*x_scale+(-36)),y_end-((450-pts[0][1])*y_scale+72))
            if(center != None):
                pass
                #draw_point((600-center[0])/x_conv-x_range/2, center[1]/y_conv)
                #x = ((600-center[0])/x_conv)-x_range/2
                #y = center[1]/y_conv
                #stXCoord.set("%.1lf", x)
                #stYCoord.set("%.1lf", y)            
            for i in range(1, len(pts)):
                # if either of the tracked points are None, ignore
                # them
                if pts[i - 1] is None or pts[i] is None:
                    continue
         
                # otherwise, compute the thickness of the line and
                # draw the connecting lines    
                #thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                if (start_delay > 199):
                    cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), 5)  
            cv2.imshow("Frame", frame)
            camera_count =0
        camera_count +=1
        if(start_delay < 300):
            start_delay +=1
    #-----------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------     
    stRcvSuccess.set("%d", success_count)
    
    if not manual_pos and not bpath and startrx:
        if(y_c > 0):
            work_area(x_c, y_c)
            pass
        if curr_shape == Shape.Rectangle:
            rectIntersect(x_c, y_c)
            pass
        elif curr_shape == Shape.Circle:
            circIntersect(x_c, y_c)
    if manual_pos == 1 and not bpath:
        if(abs(x_c-mouse_x) <2 and abs(y_c-(y_end-mouse_y+4)) < 2):
            if start_time_manual+time_delay_manual < time.time()*1000:
                Send_Intersect_Flag(FALSE)
        else:
            start_time_manual = time.time()*1000
    if bpath:
        prescribed_path(curr_path)  
        if(abs(x_c-curr_path[path_point][0])<2 and abs(y_c-4-curr_path[path_point][1])<2):
            path_point = path_point + 1
            prescribed_path(curr_path)                       
    root.after(1,main)

def init_regions():
    w.create_rectangle(-1, -1, wWidth, wHeight, \
                       stipple='gray25', fill = "red")
    w.create_polygon((x_range/2)*x_conv,(y_end-200)*y_conv,abs(15+x_range/2)*x_conv,(y_end-175)*y_conv,(36+x_range/2)*x_conv,(y_end-150)*y_conv,\
                      abs(90+x_range/2)*x_conv,(y_end-130)*y_conv,abs(65+x_range/2)*x_conv, (y_end-98)*y_conv,abs(36+x_range/2)*x_conv, (y_end-72)*y_conv,\
                     (x_range/2)*x_conv,(y_end-46)*y_conv,abs(-36+x_range/2)*x_conv, (y_end-72)*y_conv,abs(-65+x_range/2)*x_conv, (y_end-98)*y_conv, \
                     abs(-90+x_range/2)*x_conv,(y_end-130)*y_conv,\
                     abs(-36+x_range/2)*x_conv, (y_end-150)*y_conv,abs(-15+x_range/2)*x_conv,(y_end-175)*y_conv, fill='yellow', stipple='gray25')
    w.create_rectangle(abs(-36+x_range/2)*x_conv, (y_end-150)*y_conv,abs(36+x_range/2)*x_conv, (y_end-72)*y_conv, \
                       stipple='gray75', fill = "lawngreen")    
#-----------------------------------------------------------------------------------------    
#-------------------------------------Initialization--------------------------------------
#-----------------------------------------------------------------------------------------    

def get_distance(points, cornerPoints):
    points_length = len(points)
    if (points_length == 4):
        for i in range(0,4):
            x1,y1 = points[i]
            x2,y2 = cornerPoints[i]
            d1 = x2 - x1
            d2 = y2 - y1
            distance = math.sqrt(d1**2 + d2**2)
            if distance > 1:
                return True
    return False

centerPoints = []
cornerPoints = []
MIN_THRESH = 0
cX = 0
cY = 0
shape = 0
def ConstraintDetector(image):
    global centerPoints, cornerPoints, circX, circY,shape,cX,cY,circR
    done = 0
    Send_Intersect_Flag(FALSE)
    while 1:
        frame_to_thresh = cv2.cvtColor(cv2.medianBlur(cv2.GaussianBlur(image,(5, 5), 0),5), cv2.COLOR_BGR2HSV)
        frame_to_thresh = cv2.bilateralFilter(frame_to_thresh,0,4,8,2)
        frame_to_thresh = cv2.erode(frame_to_thresh, (5,5),iterations=2)
    
        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = 0,0,200,255,255,255
        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        sd = ShapeDetector()
        
        for c in cnts:
            # compute the center of the contour
            M = cv2.moments(c)
            if cv2.contourArea(c) > MIN_THRESH:
                # process the contour
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                shape = sd.detect(c)
                tup = cX, cY
                if not centerPoints:
                    centerPoints.append(tup)
                elif (tup != centerPoints[-1]):
                    centerPoints.append(tup) #send to haptic interface for center
            points = []
            done = 1
            corners = cv2.goodFeaturesToTrack(thresh,4,0.05,25)
            if corners is not None:
                for i in corners:
                    pt = i[0][0],i[0][1]
                    if not points:
                        points.append(pt)
                    elif (pt != points[-1]):
                        points.append(pt)
                        cv2.circle(image,(pt),5,255,-1)
            for i in range(0,4):
                if not cornerPoints:
                    cornerPoints.append(points)
                elif (get_distance(points, cornerPoints[-1])):
                    cornerPoints.append(points) #send to haptic interface for corners of shape
            
            # draw the contour and center of the shape on the image
            cv2.drawContours(image, [c], -1, (0, 255, 0), 2) # draw contours on the image
            cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 2)
            cv2.circle(image, (cX, cY), 7, (0, 0, 255), -1) # draw center circle on the image
            cv2.putText(image, "center", (cX - 20, cY - 20),    #draw center text on the image
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            if(shape == 'circle'):
                circX, circY = cX*x_scale-36, (450-cY)*y_scale+72
                circR = 5
                print(cX, cY,circX, circY)
                
        if done:
            ToggleCamera()
            draw_constraint(Shape.Circle, circX, circY, circR, 0)
            break 

x_scale = 72/600
y_scale = 78/450
ser = init_serial()  
root = init_window()
create_buttons(root)
create_labels(root)
stRcvSuccess = StatusBar(root)
stXCoord = StatusBar(root)
stYCoord = StatusBar(root)
stleft_length = StatusBar(root)
stright_length = StatusBar(root)
stDesired1 = StatusBar(root)
stDesired2 = StatusBar(root)
stRcvSuccess.place(x=780,y=10)
stXCoord.place(x=780,y=40)
stYCoord.place(x=780,y=70)
stleft_length.place(x=670,y=120)
stright_length.place(x=770,y=120)
stDesired1.place(x=670, y=180)
stDesired2.place(x=770, y=180)
w = Canvas(root, width=wWidth, height=wHeight, highlightthickness = 0)
w.place(x=82,y=98)
rect = w.create_rectangle(0,0,0,0, fill="blue")
line1 = w.create_line(0,0,0,0)
line2 = w.create_line(0,0,0,0)
line3 = w.create_line(0,0,0,0)
line4 = w.create_line(0,0,0,0)
circle = w.create_oval(0,0,0,0)
rectangle = w.create_rectangle(0,0,0,0)
circle_C = w.create_oval(0,0,0,0)
init_regions()
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
Label(root, text="Constraint Region", font = "Courier 12 bold").place(x=660, y=270)
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (24,103,70)
greenUpper = (157, 255, 255)
pts = deque(maxlen=250)

eight_path = [[0,150],[-7,145],[-15,140],[-18,135],[-20, 130],[-18,125],[-15,120],[-7,115],[0,110],[7,105],[15,100],[18,95],\
              [20,90],[18,85],[15,80],[7,75],[0,70],[-7,75],\
              [-15,80],[-18,85],[-20,90],[-18,95],[-15,100],[-7,105],[0,110],[7,115],[15,120],[18,125],[20,130],\
              [18,135],[15,140],[7,145],[0,150]]

star_path = [[0,150],[-15,130],[-35,130],[-20,110],[-35,85],[0,100],[35,85],[20,110],[35,130],[15,130],[0,150]]

curr_path = eight_path

draw_constraint(Shape.Rectangle, default_sqX, default_sqY, default_sqL, default_sqH)
root.bind('<Escape>', close)
root.bind('<Return>', entry_callback)
w.bind('<Button-1>', on_click)
w.bind('<B1-Motion>', on_drag)
root.after(1,main)
root.mainloop()

#images
#custom shapes   
#keep in/keep out
#opencv move arms or move constraint region