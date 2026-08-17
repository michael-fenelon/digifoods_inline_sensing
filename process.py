
# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from element import*

# Control canvas to perform sample preprocessing.
class Process(Element):
    def __init__(self, holding_reg_num = None, 
                    coil_num = None,     
                    mi = None, 
                    rs485_gui_slave = None, 
                    callback = None,
                    *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        self.holding_reg_num = holding_reg_num  # Holding reg num of the valve from XLSX sheet.
        self.coil_num = coil_num                # The Coil_## for Set Valve positions
        self.mi = mi                            # modbus interface     
        self.rs485_gui_slave = rs485_gui_slave  # The arduino connected to the slave.
        self.callback = callback
        self.enable_process = False
        self.sample_or_water = ""
        self.fluid_or_air = ""
        self.action = ""
        
        # self.gen_gui()        # Some issue with MRO when uncommented
    def gen_gui(self):      
        width = 15  # int(self.canvas_width/2)
        
        self.gui_dict[self.name] = Label(self.frame, text = self.name)
        self.gui_dict['sample_water_StringVar'] = StringVar(value = "sample")
        self.gui_dict['sample'] = tk.Radiobutton(self.frame, text = "Sample", variable = self.gui_dict['sample_water_StringVar'] , value = "sample", height = 1, width = width, bg=self.bg_color)
        self.gui_dict['water'] = tk.Radiobutton(self.frame, text = "Water", variable = self.gui_dict['sample_water_StringVar'] , value = "water", height = 1, width = width, bg=self.bg_color)
        self.gui_dict['fluid_air_StringVar'] = StringVar(value = "fluid")
        self.gui_dict['fluid'] = tk.Radiobutton(self.frame, text = "Fluid", variable = self.gui_dict['fluid_air_StringVar'] , value = "fluid", height = 1, width = width, bg=self.bg_color)
        self.gui_dict['air'] = tk.Radiobutton(self.frame, text = "Air", variable = self.gui_dict['fluid_air_StringVar'] , value = "air", height = 1, width = width, bg=self.bg_color)
        
        self.gui_dict['action_withdraw_rec_infuse_StringVar'] = StringVar(value="withdraw")
        self.gui_dict['action_withdraw'] = Radiobutton(self.frame, text = "Whitdraw", variable = self.gui_dict['action_withdraw_rec_infuse_StringVar'] , value = "withdraw", height = 1, width = width, bg=self.bg_color)
        self.gui_dict['action_recirculate'] = Radiobutton(self.frame, text = "Recirculate", variable = self.gui_dict['action_withdraw_rec_infuse_StringVar'] , value = "recirculate", height = 1, width = width, bg=self.bg_color)
        self.gui_dict['action_infuse'] = Radiobutton(self.frame, text = "Infuse (Empty)", variable = self.gui_dict['action_withdraw_rec_infuse_StringVar'] , value = "infuse", height = 1, width = width, bg=self.bg_color)

        self.gui_dict['label_target_temp'] = Label(self.frame, text="Target temp (deg C)")
        self.gui_dict['scale_target_temp_DoubleVar'] = DoubleVar(value=30.0)
        self.gui_dict['scale_target_temp'] = Scale(self.frame, variable = self.gui_dict['scale_target_temp_DoubleVar'],
                                                                from_ = 15, to = 50, resolution = 0.1,
                                                                orient = HORIZONTAL, length = 150, border = 1, width = 20, troughcolor = "white", bg=self.bg_color)  

        self.gui_dict['label_target_timeout'] = Label(self.frame, text="Process time (s)")
        self.gui_dict['scale_timer_IntVar'] = IntVar(value=30)
        self.gui_dict['scale_timer'] = Scale(self.frame, variable = self.gui_dict['scale_timer_IntVar'],
                                                                from_ = 1, to = 120, resolution = 1,
                                                                orient = HORIZONTAL, length = 150, border = 1, width = 20, troughcolor = "white", bg=self.bg_color)            

        self.gui_dict['label_time'] = Label(self.frame, text = "Timer @ #s", bg=self.bg_color)
        self.gui_dict['check_enable_IntVar'] = IntVar()
        self.gui_dict['check_enable'] = Checkbutton(self.frame, 
                                                    text = "Enable",
                                                    variable = self.gui_dict['check_enable_IntVar'],
                                                    onvalue = True,
                                                    offvalue = False,
                                                    height = 1, 
                                                    width = width,
                                                    command = self.enable, bg=self.bg_color)                                                    

        self.gui_dict['label_temp_diff'] = Label(self.frame, text="T diff = # deg C")
    
        self.canvas.place(x = self.x, y = self.y)        
        print("In Control " + self.name + " gen_gui(): Completed")

        # Place all the widgets on a canvas. 
        self.gui_dict[self.name]        
        self.gui_dict['sample'].grid(row = 0, column = 0, sticky = "w")
        self.gui_dict['water'].grid(row = 0, column = 1, sticky = "w")
        self.gui_dict['fluid'].grid(row = 1, column = 0, sticky = "w")
        self.gui_dict['air'].grid(row = 1, column = 1, sticky = "w")
        self.gui_dict['label_target_temp'].grid(row = 2, column = 0, sticky = "w")
        self.gui_dict['scale_target_temp'].grid(row = 2, column = 1, sticky = "w")
        self.gui_dict['label_target_timeout'].grid(row = 3, column = 0, sticky = "w")
        self.gui_dict['scale_timer'].grid(row = 3, column = 1, sticky = "w")
        self.gui_dict['label_time'].grid(row = 3, column = 2, sticky = "w")
        self.gui_dict['action_withdraw'].grid(row = 4, column = 0, sticky = "w")        
        self.gui_dict['action_recirculate'].grid(row = 5, column = 0, sticky = "w")
        self.gui_dict['label_temp_diff'].grid(row = 5, column = 1, sticky = "w")
        self.gui_dict['action_infuse'].grid(row = 6, column = 0, sticky = "w")                
        self.gui_dict['check_enable'].grid(row = 7, column = 0, columnspan = 2, sticky = "")

    def enable(self):
        self.enable_process = self.gui_dict['check_enable_IntVar'].get()        
        self.sample_or_water = self.gui_dict['sample_water_StringVar'].get()
        self.fluid_or_air = self.gui_dict['fluid_air_StringVar'].get()
        self.action = self.gui_dict['action_withdraw_rec_infuse_StringVar'].get()     

        self.callback()  

    def set_time(self, value):
        self.gui_dict['label_time'].config(text = "Timer @ " + str(value) + " s")        

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
