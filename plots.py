# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from slaves_modbus_configuration import*
from pymodbus.client import ModbusSerialClient
from modbus_interface import Modbus_Interface
from watchpoints import watch

class PLOTS():
    def __init__(self, window = None, canvas_height = None, canvas_width = None):
        self.window = window
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Entry_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Scale_dict':{} }
        # self.gen_gui()
    
    def gen_gui(self):
        self.canvas = tk.Canvas(self.window, bg = "white", height = self.canvas_height, width = self.canvas_width, background = "white",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width-10, height = self.canvas_height-10, background = "white")        
        self.canvas.create_window( 5, 5, window = self.frame, anchor = tk.NW )  


        self.gui_dict['Label_dict']['test'] = Label(self.frame, text = "PLOTS ", fg="red", bg="white")

        # self.canvas.grid(row = 0, column = 0, sticky = "nw")  # This is done in main.py. 

        self.gui_dict['Label_dict']['test'].grid(row = 0, column = 0)        