
# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from element import*
class T_sensor(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temperature = 0
        self.gen_gui()

    def gen_gui(self):
        self.gui_dict[self.name] = Label(self.frame, text = self.name, wraplength=self.canvas_width, fg = self.fg_color, bg = self.bg_color)
        self.gui_dict['temperature'] = Label(self.frame, text = "---", fg = self.fg_color, bg = self.bg_color)
        # Placement of widgets for a valve on the canvas.

        self.gui_dict[self.name].place(relx=0.5, rely=0.3, anchor="center")
        self.gui_dict['temperature'].place(relx=0.5, rely=0.6, anchor="center")

        # self.gui_dict[self.name] .grid(row= 0, column=0, sticky = "ns", columnspan = 3)
        # self.gui_dict['temperature'].grid(row= 1, column=0, sticky = "")
        self.canvas.place(x = self.x, y = self.y)
  
    # Get a float value and update the gui.
    def update_temp(self, value):
        self.temperature = value
        self.gui_dict['temperature'].config(text = str( round(value,2) ) + " degC")

