# import all components from the tkinter library
from tkinter import *
import tkinter as tk
from tkinter import ttk
import copy
import time 
from slaves_modbus_configuration import*
from pymodbus.client import ModbusSerialClient
from modbus_interface import Modbus_Interface
from watchpoints import watch
from rs485_gui_slave import*

# Alias tsm == Temperature_stabilisation_module
class Temperature_stabilisation_module():
    def __init__(self, window  = None, rs485_gui_slave = None):
        self.window = window    # root window from main.py
        self.rs485_gui_slave = rs485_gui_slave     
        self.color = "#d9d9d9"    # Deafult gray color of a widget print("Default color = ", self.gui_dict['Check_dict']['enable_tsm'].cget("bg"))              
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Scale_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Radio_dict':{}, 'Progress_bar':{}, 'Scale_dict':{} }           
        self.gen_gui()

    def gen_gui(self):
        self.canvas_height = 800
        self.canvas_width = 800 
        self.canvas = tk.Canvas(self.window, bg="white", height = self.canvas_height, width = self.canvas_width, background= "#d9d9d9",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width-10, height = self.canvas_height-10, background= self.color)        
        self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )         

        width = 40    
        self.gui_dict['Check_dict']['enable_tsm_IntVar'] = IntVar()
        self.gui_dict['Check_dict']['enable_tsm'] = Checkbutton(self.frame, 
                                                                            text="RUN: Temperature stabilisation module",
                                                                            variable=self.gui_dict['Check_dict']['enable_tsm_IntVar'],
                                                                            onvalue=True,
                                                                            offvalue=False,
                                                                            height=1, 
                                                                            width = width,
                                                                            command=self.tsm_enable)
                                                                         
        self.gui_dict['Radio_dict']['auto_debug_IntVar'] = StringVar(value="auto")
        self.gui_dict['Radio_dict']['auto'] = tk.Radiobutton(self.frame, text="Auto ", variable=self.gui_dict['Radio_dict']['auto_debug_IntVar'], value="auto", height=1, width = width)
        self.gui_dict['Radio_dict']['debug'] = tk.Radiobutton(self.frame, text="Debug", variable=self.gui_dict['Radio_dict']['auto_debug_IntVar'], value="debug", height=1, width = width)                                                                           
        self.gui_dict['Button_dict']['tsm_start'] = Button(self.frame, text="Start", command=self.tsm_start, height=1, width = width)   

        # 6 temperature sensors, 
        # 6 three way valves, sliders for specific positions. 
        # relays ?
        # vnh5019 slave 
        
        # Place all the widgets on the self.frame.
        self.canvas.grid(row=0, column=0, sticky="nw", padx=5, pady=50)
        self.gui_dict['Check_dict']['enable_tsm'].grid(row = 0, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Radio_dict']['auto'].grid(row = 1, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Radio_dict']['debug'].grid(row = 2, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Button_dict']['tsm_start'].grid(row = 3, column = 0, sticky = "nw", pady = 2, columnspan = 1)

    def tsm_enable(self):
        print("In tsm_enable(): ...")        

    def tsm_start(self):
        print("In tsm_start(): ...")       

    def tsm_get_valve_positions(self):
        self.rs485_gui_slave.coil_list[2] = 1
        self.rs485_gui_slave.update_slave_via_reg_list()
        self.rs485_gui_slave.update_gui()    
        
    # Generic function to withdraw a fluid, eith sample or water from 
    def get_fuild(self, type = None):
        pass 

        # Set valve A to flow cell and valve B
        self.rs485_gui_slave.holding_reg_list[] = 


def root_window_bind_callback():
    print("In root_window_bind_callback():  ...")
    
def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit()     

if __name__ == "__main__":
    # Create the root window
    root_window = Tk()   
    root_window.title('Temperature stabilisation module')       # Set window title    
    window_width = 1600
    window_height = 1000
    root_window.geometry(str(window_width) + "x" + str(window_height))     # Set window size width x height   1600x1000
    # root_window.geometry("1600x1000")     # Set window size width x height   
    root_window.config(background = "white")     #Set window background color  
    root_window.columnconfigure( 0, weight = 1 ) # Stretch Column 0 to fit width.
    root_window.rowconfigure( 0, weight = 1 ) # Stretch row 0 to fit height. 
    root_window.resizable(width=False, height=False)         # This makes the GUI of fixed size and prevents resizing.
    root_window.bind('<Return>', root_window_bind_callback )            # This gets the values entered in the gui.
    root_window.lift()       # Bring window forwards
    # root_window.attributes('-topmost', True)
    root_window.protocol("WM_DELETE_WINDOW", on_closing)   

    slaves_mcfg = Slaves_Modbus_Config()       # Get configurations of all slaves (read xlsx file)
    slaves_mcfg.get_config()
    mi = Modbus_Interface()     # Create a RS485 Modbus RTU interface with baud rate, 8N1 ...etc. 

    tsm = Temperature_stabilisation_module(window=root_window)    
    tsm.canvas.grid(row=0, column=0)

    root_window.mainloop()       # Blocking function.   
