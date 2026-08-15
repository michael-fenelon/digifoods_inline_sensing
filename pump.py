
# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from element import*
 
# Inherit from the Parent class Element and build a Child class.
class Pump(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rpm = 0
        self.enable = False    
        self.gen_gui()  # The master will not have to run this separately.                
            
    def gen_gui(self):
        self.gui_dict[self.name] = Label(self.frame, text = self.name)
        self.gui_dict['enable_BooleanVar'] = BooleanVar()
        self.gui_dict['enable'] = Checkbutton(self.frame, 
                                            text = "Enable",
                                            variable = self.gui_dict['enable_BooleanVar'],
                                            onvalue = True,
                                            offvalue = False,
                                            height = 1, 
                                            width = 10,
                                            command = self.enable_callback)

        self.gui_dict['in'] = Label(self.frame, text = "IN")        
        self.gui_dict['out'] = Label(self.frame, text = "OUT")      
        self.gui_dict['rpm_status_IntVar'] = IntVar(value=0)
        self.gui_dict['rpm_status'] = Scale(self.frame, 
                                            variable = self.gui_dict['rpm_status_IntVar'],
                                            from_ = 0, to = 100, resolution = 1, troughcolor = "white",
                                            orient = HORIZONTAL, length = self.canvas_width-8, border = 1, width = 20)              

        # Placement of widgets for a pump on the canvas.
        self.gui_dict[self.name] .grid(row= 0, column=1, sticky = "nw", columnspan = 2)
        self.gui_dict['enable'] .grid(row= 0, column=2, sticky = "e", columnspan = 1)
        self.gui_dict['rpm_status'].grid(row= 1, column=0, columnspan = 3, sticky = "ns")
        self.gui_dict['in'].grid(row= 2, column=0, sticky = "ns")
        self.gui_dict['out'].grid(row= 2, column=2, sticky = "ns") 

        self.canvas.place(x = self.x, y = self.y)
    
    def enable_callback(self):
        print("clicked")
        self.enable = self.gui_dict['enable_BooleanVar'].get()
        self.rpm = self.gui_dict['rpm_status'].get()
        print("In pump ", self.name, " status = ", self.enable, " , RPM = ", self.rpm)
    
def root_window_bind_callback():
    print("In root_window_bind_callback():  ...")

def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit() 

if __name__ == "__main__":
    # Create the root window
    root_window = Tk()   
    root_window.title('pump')       # Set window title    
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

    # Create pump 1
    pump1 = Pump(name="pump 1", window=root_window, bg_color="white")
    pump1.canvas.configure(highlightthickness=3)    
    pump1.gen_gui()
    pump1.canvas.grid(row=0, column=0)
    
    # Create pump 2
    pump2 = Pump(name = "pump 2", window=root_window, canvas_height=150, canvas_width=200, bg_color="orange")
    pump2.canvas.configure(highlightthickness=1)    
    pump2.gen_gui()
    pump2.canvas.grid(row=1, column=1)
    # pump2.canvas.config(bg = 'blue')
    # pump2.canvas.config(background = 'orange')

    root_window.mainloop()       # Blocking function.   

# DUMP


# class Pump():    
    # def __init__(self, name = None, 
    #                 window = None, 
    #                 canvas_height = 100, 
    #                 canvas_width = 200, 
    #                 color = "#d9d9d9",
    #                 x = 0,
    #                 y = 0): 
    #     self.name = name
    #     self.window = window
    #     self.canvas_height = canvas_height
    #     self.canvas_width = canvas_width
    #     self.color = color
    #     self.x = x      # position for canvas placement
    #     self.y = y      # position for canvas placement        
    #     self.gui_dict =  {}     # A dictionary to hold all the widgets.
    #     self.canvas = tk.Canvas(self.window, bg=self.color, height = self.canvas_height, width = self.canvas_width, highlightthickness = 5)  
    #     self.frame = tk.Frame(self.canvas, width = self.canvas_width + 5, height = self.canvas_height + 5, background= self.color)        
    #     self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )   
