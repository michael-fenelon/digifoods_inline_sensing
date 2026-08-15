
# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from slaves_modbus_configuration import*
from pymodbus.client import ModbusSerialClient
from modbus_interface import Modbus_Interface
from watchpoints import watch
from element import*


class VALVE():
    def __init__(self, window = None, canvas_height = 200, canvas_width = 200, color = "white"):
        self.window = window
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.color = color           
        self.canvas = tk.Canvas(self.window,
                                bg="white",
                                height = self.canvas_height, 
                                width = self.canvas_width, 
                                background= "white",  
                                highlightthickness = 1)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width, height = self.canvas_height, background= self.color)        
        self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )                               
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Entry_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Scale_dict':{} }
        self.gen_gui()
    def gen_gui(self):
        self.gui_dict['Label_dict']['label_1'] = Label(self.frame, text = "label 1")
        self.gui_dict['Label_dict']['label_2'] = Label(self.frame, text = "label 2")
        self.gui_dict['Label_dict']['label_3'] = Label(self.frame, text = "label 3")
    
        self.gui_dict['Label_dict']['label_1'].grid(row=0, column=0)
        self.gui_dict['Label_dict']['label_2'].grid(row=1, column=1)
        self.gui_dict['Label_dict']['label_3'].grid(row=2, column=2)

        #self.canvas.grid(row=0, column=0)   # Needs to be done by master (the module that creates an instance of VALVE)
def root_window_bind_callback():
    print("In root_window_bind_callback():  ...")

def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit() 

if __name__ == "__main__":
    # Create the root window
    root_window = Tk()   
    root_window.title('VALVE')       # Set window title    
    window_width = 1600
    window_height = 1000
    root_window.geometry(str(window_width) + "x" + str(window_height))     # Set window size width x height   1600x1000
    root_window.config(background = "white")     #Set window background color  
    root_window.columnconfigure( 0, weight = 1 ) # Stretch Column 0 to fit width.
    root_window.rowconfigure( 0, weight = 1 ) # Stretch row 0 to fit height. 
    root_window.resizable(width=False, height=False)         # This makes the GUI of fixed size and prevents resizing.
    root_window.bind('<Return>', root_window_bind_callback )            # This gets the values entered in the gui.
    root_window.lift()       # Bring window forwards
    root_window.attributes('-topmost', True)
    root_window.protocol("WM_DELETE_WINDOW", on_closing)   

    valve = VALVE(window=root_window, canvas_height=150, canvas_width=200, color="orange")
    valve.gen_gui()

    root_window.mainloop()       # Blocking function.   



