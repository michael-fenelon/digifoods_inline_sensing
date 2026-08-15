# import all components from the tkinter library
from tkinter import *
import tkinter as tk

# Just a canvas for plots. 
class Element():
    def __init__(self, name = None, 
                    window = None, 
                    canvas_height = 100, 
                    canvas_width = 100, 
                    fg_color = "gray0",
                    bg_color = "#d9d9d9",
                    x = 0,
                    y = 0):   
        self.name = name
        self.window = window
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.x = x      # position for canvas placement
        self.y = y      # position for canvas placement
        self.gui_dict =  {}     # A dictionary to hold all the widgets.
        self.canvas = tk.Canvas(self.window, bg=self.bg_color, height = self.canvas_height, width = self.canvas_width, highlightthickness = 0)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width + 5, height = self.canvas_height + 5, background= self.bg_color)        
        self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )                       
        self.gen_gui()  # The master will not have to run this separately. 

    def gen_gui(self):
        self.gui_dict[self.name] = Label(self.frame, text = self.name, bg=self.bg_color, fg=self.fg_color)
        self.gui_dict[self.name].place(x = self.canvas_width * 0.25, y = self.canvas_height * 0.3)  #, anchor="center")
        # self.gui_dict[self.name].grid(row=0, column=0, sticky = "ns", columnspan = 2)
        self.canvas.place(x = self.x, y = self.y)


        