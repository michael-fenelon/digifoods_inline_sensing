
# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from element import*

class Valve(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gen_gui()
    def gen_gui(self):
        self.gui_dict[self.name] = Label(self.frame, text = self.name)
        self.gui_dict['in 1'] = Label(self.frame, text = "IN 1", fg = self.fg_color, bg=self.bg_color)
        self.gui_dict['in 2'] = Label(self.frame, text = "IN 2", fg = self.fg_color, bg=self.bg_color)
        self.gui_dict['out'] = Label(self.frame, text = "OUT", fg = self.fg_color, bg=self.bg_color)      
        self.gui_dict['position_status_IntVar'] = IntVar(value=1)
        self.gui_dict['position_status'] = Scale(self.frame, 
                                                        variable = self.gui_dict['position_status_IntVar'],
                                                        from_ = 1, to = 2, resolution = 1, troughcolor = "white",
                                                        orient = HORIZONTAL, length = self.canvas_width-8, border = 1, width = 20)                


        # Placement of widgets for a valve on the canvas.
        self.gui_dict[self.name] .grid(row= 0, column=1, sticky = "nw", columnspan = 3)
        self.gui_dict['position_status'].grid(row= 1, column=0, columnspan = 3, sticky = "ns")
        self.gui_dict['in 1'].grid(row= 2, column=0, sticky = "ns")
        self.gui_dict['out'].grid(row= 2, column=1, sticky = "ns") 
        self.gui_dict['in 2'].grid(row= 2, column=2, sticky = "ns")

        self.canvas.place(x = self.x, y = self.y)
    
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
    # root_window.attributes('-topmost', True)
    root_window.protocol("WM_DELETE_WINDOW", on_closing)   

    # Create valve 1
    valve1 = Valve(name="valve 1", window=root_window)
    valve1.canvas.configure(highlightthickness=3)    
    valve1.gen_gui()
    valve1.canvas.grid(row=0, column=0)
    
    # Create valve 2
    valve2 = Valve(name = "valve 2", window=root_window, canvas_height=150, canvas_width=100, color="orange")
    valve2.canvas.configure(highlightthickness=1)    
    valve2.gen_gui()
    valve2.canvas.grid(row=1, column=1)
    # valve2.canvas.config(bg = 'blue')
    # valve2.canvas.config(background = 'orange')

    root_window.mainloop()       # Blocking function.   

# # DUMP

# class Valve():
#     def __init__(self, name = None, 
#                     window = None, 
#                     canvas_height = 100, 
#                     canvas_width = 200, 
#                     color = "#d9d9d9",
#                     x = 0,
#                     y = 0):   
#         self.name = name
#         self.window = window
#         self.canvas_height = canvas_height
#         self.canvas_width = canvas_width
#         self.color = color
#         self.x = x      # position for canvas placement
#         self.y = y      # position for canvas placement
#         self.gui_dict =  {}     # A dictionary to hold all the widgets.
#         self.canvas = tk.Canvas(self.window, bg=self.color, height = self.canvas_height, width = self.canvas_width, highlightthickness = 5)  
#         self.frame = tk.Frame(self.canvas, width = self.canvas_width + 5, height = self.canvas_height + 5, background= self.color)        
#         self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )                       
#         self.gen_gui()  # The master will not have to run this separately.      

