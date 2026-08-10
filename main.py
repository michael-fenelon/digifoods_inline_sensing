
# import all components from the tkinter library
from tkinter import *
# from tkinter import filedialog
# from tkinter.filedialog import asksaveasfile
# from os import walk
# from tkinter import messagebox
import tkinter as tk
# import tkinter.font as tkFont
from tkinter import ttk
import copy
import time 
from slaves_modbus_configuration import*
from pymodbus.client import ModbusSerialClient
from modbus_interface import Modbus_Interface
from watchpoints import watch
from rs485_gui_slave import*
from sample_bypass_module import*
from temperature_stabilisation_module import*


### MAIN ############################################################################################################################################
def root_window_bind_callback(*args):
    print("root_window_bind_callback()", *args)           

def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit()     

def tab_selected(event)   :
    pass

root_window = None
slaves_mcfg = None
mi = None

if __name__ == "__main__":
    # Create the root window
    root_window = Tk()   
    root_window.title('DigiFoods - Inline Sensing')       # Set window title    
    window_width = 1700
    window_height = 1000
    root_window.geometry(str(window_width) + "x" + str(window_height))     # Set window size width x height   1600x1000
    # root_window.geometry("1600x1000")     # Set window size width x height   
    root_window.config(background = "white")     #Set window background color  
    root_window.columnconfigure( 0, weight = 1 ) # Stretch Column 0 to fit width.
    root_window.rowconfigure( 0, weight = 1 ) # Stretch row 0 to fit height. 
    root_window.resizable(width=False, height=False)         # This makes the GUI of fixed size and prevents resizing.

    slaves_mcfg = Slaves_Modbus_Config()       # Get configurations of all slaves (read xlsx file)
    slaves_mcfg.get_config()
    mi = Modbus_Interface()     # Create a RS485 Modbus RTU interface with baud rate, 8N1 ...etc. 
    
    notebook = ttk.Notebook(root_window)    # Notebook widget

    # Tab1 
    tab_1_sample_bypass_window = ttk.Frame(notebook, border = 2, height = window_height, width = window_width, padding=1)
    slave_1 = rs485_gui_slave(window = tab_1_sample_bypass_window, slave_number = 3, modbus_interface = mi, slaves_mcfg = slaves_mcfg, color = "white")
    slave_1.gen_slave_modbus_gui()
    slave_1.canvas.grid(row = 0, column = 1, sticky = "nw",  columnspan = 1)        
    slave_1.vbar.grid(row = 0, column = 2, sticky = "ns", columnspan = 1, rowspan = 1, padx= 10)           
    sample_bypass = SAMPLE_BYPASS(window = tab_1_sample_bypass_window, rs485_gui_slave = slave_1)    

    # Tab2
    tab_2_tsm_window = ttk.Frame(notebook, border = 2, height = window_height, width = window_width, padding=1)
    slave_2 = rs485_gui_slave(window = tab_2_tsm_window, slave_number = 2, modbus_interface = mi, slaves_mcfg = slaves_mcfg, color="white", canvas_height=950)
    slave_2.gen_slave_modbus_gui()
    slave_2.canvas.grid(row = 0, column = 2, sticky = "nw", columnspan = 1)           
    slave_2.vbar.grid(row = 0, column = 3, sticky="ns", columnspan = 1, rowspan=1, padx= 10)
    
    pumps_slave = rs485_gui_slave(window = tab_2_tsm_window, slave_number = 1, modbus_interface = mi, slaves_mcfg = slaves_mcfg, color="white")
    pumps_slave.gen_slave_modbus_gui()      # We only create the gui and dictionary for the coils_list, discrete_input_list, holding_reg_lists and input_reg_list, but don't display it 
    # pumps_slave.canvas.grid(row = 1, column = 2, sticky = "nw", columnspan = 1)           
    # pumps_slave.vbar.grid(row = 1, column = 3, sticky="ns", columnspan = 1, rowspan=1, padx= 10)    
    tsm = Temperature_stabilisation_module(window = tab_2_tsm_window, rs485_gui_slave = slave_2, pumps_slave = pumps_slave)    

    root_window.bind('<Return>', root_window_bind_callback )            # This gets the values entered in the gui after ENTER key is pressed.
    root_window.lift()       # Bring window forwards
    # root_window.attributes('-topmost', True)
    root_window.protocol("WM_DELETE_WINDOW", on_closing)            # Let the window wait for any events

    s = ttk.Style()
    s.configure('TNotebook.Tab', font=('URW Gothic L','11','bold') )        # Gothic <3 :D !

    notebook.add(tab_1_sample_bypass_window, text='  Sample Bypass  ') 
    notebook.add(tab_2_tsm_window, text='  Temperature equalisation module  ')   
    # notebook.add(tab_3, text='  Temperature equalisation module (WIP)  ')   

    notebook.grid(row=0, column=0)
    notebook.bind("<<NotebookTabChanged>>", tab_selected)       # Bind a monitor to check if we change between Tabs.
    # root_window.grid_columnconfigure((0,1), weight=2, uniform="column")   # This spaces the frame equally in columns    
    root_window.mainloop()       # Blocking function.        


# DUMP
