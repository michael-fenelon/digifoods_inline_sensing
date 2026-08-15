
# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from slaves_modbus_configuration import*
from pymodbus.client import ModbusSerialClient
from modbus_interface import Modbus_Interface
from watchpoints import watch
from valve import*
from element import*

class TSM(Element):
    def __init__(self, window = None, *args, **kwargs):            
        super().__init__(*args, **kwargs)
        self.window = window
        self.valve_1 = Valve(name = "Valve 1", window = self.window, canvas_height = 200, canvas_width = 200, *args)
        self.valve_2 = Valve(name = "Valve 2", window = self.window, canvas_height = 200, canvas_width = 100, *args)#, **kwargs)
        self.valve_3 = Valve(name = "Valve 3", window = self.window, canvas_height = 200, canvas_width = 200, *args)#, **kwargs)
        self.valve_4 = Valve(name = "Valve 4", window = self.window, canvas_height = 50, canvas_width = 200, *args)# **kwargs)        

    def gen_gui(self):
        self.valve_1.gen_gui()
        self.valve_2.gen_gui()
        self.valve_3.gen_gui()
        self.valve_4.gen_gui()

        self.valve_1.canvas.place(x=0, y = 0)
        self.valve_2.canvas.place(x=200, y = 200)
        self.valve_3.canvas.place(x=400, y = 400)
        self.valve_4.canvas.place(x=800, y = 200)

        # self.valve_1.canvas.grid(row=0, column=0, sticky="nw")
        # self.valve_2.canvas.grid(row=0, column=1, sticky="nw")
        # self.valve_3.canvas.grid(row=1, column=0, sticky="nw")
        # self.valve_4.canvas.grid(row=1, column=1, sticky="nw")

def root_window_bind_callback():
    print("In root_window_bind_callback():  ...")

def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit() 

if __name__ == "__main__":
    # Create the root window
    root_window = Tk()   
    root_window.title('TEST')       # Set window title    
    window_width = 1600
    window_height = 1000
    root_window.geometry(str(window_width) + "x" + str(window_height))     # Set window size width x height   1600x1000
    root_window.config(background = "white")     #Set window background color  
    root_window.columnconfigure( 0, weight = 1 ) # Stretch Column 0 to fit width.
    root_window.rowconfigure( 0, weight = 1 ) # Stretch row 0 to fit height. 
    root_window.resizable(width=False, height=False)         # This makes the GUI of fixed size and prevents resizing.
    root_window.bind('<Return>', root_window_bind_callback )            # This gets the values entered in the gui.
    root_window.lift()       # Bring window forwards
    # root_window.attributes('-topmost', True)
    root_window.protocol("WM_DELETE_WINDOW", on_closing)   

    tsm = TSM(window=root_window, canvas_height=1000, canvas_width=1500, color="white")
    tsm.canvas.config(bg="blue")
    tsm.gen_gui()
    tsm.canvas.grid(row=0, column=0, sticky="nw")

    root_window.mainloop()       # Blocking function.   



