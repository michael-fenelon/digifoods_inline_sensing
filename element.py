
# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from slaves_modbus_configuration import*
from pymodbus.client import ModbusSerialClient
from modbus_interface import Modbus_Interface
from watchpoints import watch

# Generic canvas to create and place TK widgets. 
class Element():
    def __init__(self, window = None, canvas_height = 200, canvas_width = 200, color = "#d9d9d9"):
        self.window = window
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.color = color           
        self.canvas = tk.Canvas(self.window,                                
                                height = self.canvas_height, 
                                width = self.canvas_width, 
                                background= "#d9d9d9",  
                                highlightthickness = 1)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width, height = self.canvas_height, background= self.color)        
        self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )                               
        self.gui_dict =  {'Label_dict':{}, 
                        'Text_dict':{}, 
                        'Button_dict':{}, 
                        'Entry_dict':{}, 
                        'Check_dict':{},
                        'Drop_down_dict':{},
                        'Scale_dict':{}}
        # self.gen_gui()

    # Eg: Create an Element of a pump.
    # Create widgets and place them.
    def gen_gui(self):
        self.gui_dict['Label_dict']['pump_input'] = Label(self.frame, text = "IN")
        self.gui_dict['Label_dict']['pump_output'] = Label(self.frame, text = "OUT")
        self.gui_dict['Label_dict']['pump_name'] = Label(self.frame, text = "PUMP 1 (Sample/WATER)")
        self.gui_dict['Scale_dict']['pump_rpm_IntVar'] = IntVar(value = 50)
        self.gui_dict['Scale_dict']['pump_rpm'] = Scale(self.frame, 
                                                        variable = self.gui_dict['Scale_dict']['pump_rpm_IntVar'],
                                                        from_ = 0, to = 100, resolution = 1, troughcolor = "white",
                                                        orient = HORIZONTAL, length = 100, border = 1, width = 20)
        
        self.gui_dict['Label_dict']['pump_name'].grid(row=0, column=1)
        self.gui_dict['Scale_dict']['pump_rpm'].grid(row=1, column=1)
        self.gui_dict['Label_dict']['pump_input'].grid(row=2, column=0)
        self.gui_dict['Label_dict']['pump_output'].grid(row=2, column=2)
 
        #self.canvas.grid(row=0, column=0)   # Needs to be done by master (the module that creates an instance of Element)

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

    pump = Element(window=root_window, canvas_height=100, canvas_width=250, color="white")
    pump.gen_gui()    
    pump.canvas.grid(row=0, column=0)

    root_window.mainloop()       # Blocking function.   



