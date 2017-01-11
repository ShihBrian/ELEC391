import sys
import tkinter as tk
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
f = Figure(figsize=(7,7), dpi=100)
a = f.add_subplot(111)
b = f.add_subplot(111)

x=0
y=0
square=0
circle=1

def animate(i):
    global x, y, square, circle
    
    x=x+2
    y=y+2
           
    a.clear()
    a.set_xlim([0,1000])
    a.set_ylim([0,1000])
    a.plot(x, y, 'or')
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
        
        for F in (MainPage, DataPage):
            
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
        button2 = ttk.Button(self, text="Data Page", command=lambda: controller.show_frame(DataPage)).place(x=75, y=0)
        button3 = ttk.Button(self, text="Square", command=lambda: setshape(1)).place(x=0,y=100)
        button4 = ttk.Button(self, text="Circle", command=lambda: setshape(2)).place(x=75,y=100)
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().place(x=0,y=200)
        
        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.place(x=0,y=150)
        
        
class DataPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        button1 = ttk.Button(self, text="Main Page", command=lambda: controller.show_frame(MainPage)).grid(row=1, column=1, sticky="nsew")
        button2 = ttk.Button(self, text="Data Page").grid(row=1, column=2, sticky="nsew")

def close(event):
    Gui.withdraw()
    sys.exit()


Gui = myGui()
Gui.bind('<Escape>', close)
ani = animation.FuncAnimation(f,animate, interval=10)
Gui.mainloop()
        
#enter values to reposition shapes
#display information on side bar x,y for now
#more shapes
#images
#custom shapes        
        