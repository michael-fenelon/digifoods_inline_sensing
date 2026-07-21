
# import all components from the tkinter library
from tkinter import *
# from tkinter import filedialog
# from tkinter.filedialog import asksaveasfile
# from os import walk
# from tkinter import messagebox
import tkinter as tk
# import tkinter.font as tkFont
from tkinter import ttk
from datetime import date
import copy
import datetime
import time 
from slaves_modbus_configuration import*
import time
from pymodbus.client import ModbusSerialClient

class rs485_gui_slave():
    def __init__(self, window = None, slave_number = None):
        self.window = window
        self.slave_number = slave_number
        self.slave_variables = None
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Entry_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{} }
        self.coils_list = []            # Coils = Digital outputs/writes, Eg: LED, Relays
        self.discrete_inputs_list = []  # Discrete Inputs = Digital inputs/reads, Eg: Switches
        self.holding_reg_list = []      # Holding registers = 16bit variable values, R+W
        self.input_reg_list = []        # Input_registers = 16bit variable values, R only.
        self.row_counter = 0 # 

    def gen_slave_modbus_gui(self):  
        global slaves_mcfg    
        # Create a canvas for the Wavelengths and XLSX sheet
        # Canvas are scrollable, Frames are not.
        # So we create a Frame and put it on a canvas so that the frame and canvas become scrollable.
        self.canvas_height = 400
        self.canvas_width = 550 
        self.canvas = tk.Canvas(self.window, bg="white", height = self.canvas_height, width = self.canvas_width, background= "white",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width-10, height = self.canvas_height-10, background= "white")        
        self.canvas.create_window( 5,5, window = self.frame, anchor=tk.NW )                       
        self.vbar = tk.Scrollbar(self.window, orient = 'vertical', command = self.canvas.yview)        
        # vbar = tk.Scrollbar(self.frame, orient = 'vertical', command = self.canvas.yview)        

        self.canvas.config(yscrollcommand = self.vbar.set)
        self.frame.bind('<Configure>', self.on_config_canvas)  
        # self.frame.bind_all("<Button-4>", self.on_mouse_wheel)   # Linux up
        # self.frame.bind_all("<Button-5>", self.on_mouse_wheel)   # Linux down        

        # Definitions
        self.gui_dict['Label_dict']['Name'] = Label(self.frame, text = "Name : " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Name"], bg = "white", wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Address'] = Label(self.frame, text = "Address : " + str(slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Address"]), bg = "white", wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Info'] = Label(self.frame, text = "Info : " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Info"], bg = "white", wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Board'] = Label(self.frame, text = "Board : " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Board"], bg = "white", wraplength = self.canvas_width - 10)
        
        # Placement of Label widgets on the slave's canvas' frame.
        self.gui_dict['Label_dict']['Name'].grid(row = 0, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Address'].grid(row = 1, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Info'].grid(row = 2, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Board'].grid(row = 3, column = 0, sticky = "w", pady = 2, columnspan = 2) 

        # Read upto 100 coils, break when we reach the last one.        
        for coil_num in range(0, 100):
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)] = Label(self.frame, text = "Coil " + str(coil_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)], bg = "white", wraplength = 200)
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)].grid(row = 4 + coil_num, column = 0, sticky = "w", pady = 2, columnspan = 2)

            # If the slave_dict has the Nth coil we create and place a check button on the frame, else, we break out of the for loop.
            # if the key "slave_N_Coil_M" exists in the slaves_mcfg.dict
            if "slave_" + str(self.slave_number) + "_Coil_" + str(coil_num) in slaves_mcfg.dict:
                self.coils_list.append(0)        

                # Create and place check buttons
                self.gui_dict['Check_dict']['Coil_' + str(coil_num) + "_var"] = tk.IntVar()
                self.gui_dict['Check_dict']['Coil_' + str(coil_num)] = tk.Checkbutton(self.frame, 
                                                                                            text = "Coil " + str(coil_num) + " (" + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)] + ")",
                                                                                            variable = self.gui_dict['Check_dict']['Coil_' + str(coil_num) + "_var"], 
                                                                                            onvalue = 1, 
                                                                                            offvalue = 0, 
                                                                                            command = self.on_coil_button)

                self.gui_dict['Check_dict']['Coil_' + str(coil_num)].grid(row = 4 + coil_num, column = 0, sticky = "w", pady = 2, columnspan = 2)                                      
            else:
                print("No more coils !")
                break

        # Discrete Inputs. Read upto 100 discrete inputs
        for discrete_inputs_num in range(0,100):
            if "slave_" + str(self.slave_number) + "_Discrete_input_" + str(discrete_inputs_num) in slaves_mcfg.dict:  
                self.discrete_inputs_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num)] = Label(self.frame, 
                                                                                                    text = "Discrete input " + str(discrete_inputs_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Discrete_input_" + str(discrete_inputs_num)], 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num)].grid(row = 4 + coil_num + discrete_inputs_num * 2 + 1, column = 0, sticky = "w", pady = 2, columnspan = 2)

        # Holding registers, read upto 100 holding registers
        for holding_reg_num in range(0, 100):
            # # If the slave_dict has the Nth holding_register we create and place a check button on the frame, else, we break out of the for loop.
            if "slave_" + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num) in slaves_mcfg.dict:  
                self.holding_reg_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num)] = Label(self.frame, 
                                                                                                    text = "Holding_register " + str(holding_reg_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num)], 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num)].grid(row = 4 + coil_num + discrete_inputs_num + holding_reg_num * 2 + 1, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Display current value
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = "current value = " + str(100), 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"].grid(row = 4 + coil_num + discrete_inputs_num + holding_reg_num * 2 + 2, column = 0, sticky = "e", pady = 2, columnspan = 1)

                

                # # Display the target value.
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_target"] = Label(self.frame, 
                                                                                                    text = "target value = ", 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_target"].grid(row = 4 + coil_num + discrete_inputs_num + holding_reg_num * 2 + 2, column = 2, sticky = "w", pady = 2, columnspan = 1)
                
                # Create Entry box and place it.
                self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target_StringVar"] = tk.StringVar()
                self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target"] = Entry(self.frame, 
                                                                                                                    textvariable = self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target_StringVar"],
                                                                                                                    border=1, width=10)
                self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target"].grid(row = 4 + coil_num + discrete_inputs_num + holding_reg_num * 2 + 2, column = 3, sticky = "e", pady = 2, columnspan = 1)                                                                                                          
            else:
                print("No more holding_registers !")
                break

        # # Input registers, read upto 100 Input registers
        for input_reg_num in range(0, 100):
            # # If the slave_dict has the Nth input_register we create and place a check button on the frame, else, we break out of the for loop.
            if "slave_" + str(self.slave_number) + "_Input_register_" + str(input_reg_num) in slaves_mcfg.dict:  
                self.input_reg_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)] = Label(self.frame, 
                                                                                                    text = "Input_register " + str(input_reg_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Input_register_" + str(input_reg_num)] + "  ,", 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)].grid(row = 4 + coil_num + discrete_inputs_num + holding_reg_num * 2 + 2 + input_reg_num, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Display current value
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = "current value = " + str(100), 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"].grid(row = 4 + coil_num + discrete_inputs_num + holding_reg_num * 2 + 2 + input_reg_num, column = 2, sticky = "e", pady = 2, columnspan = 1)

    
            else:
                print("No more input_registers !")
                break




        # # Place the vertical bar        
        # vbar.grid(row=0, column = 1, sticky="ns", columnspan=1, rowspan=1)

    def on_coil_button(self):
        print("Pressed slave " + str(self.slave_number) + " Coil ???" )        

    def on_config_canvas(self, e ):        
        # Set the canvas scrollregion to fit the whole of frame.
        # self.canvas.configure(scrollregion=(0, 0, e.width, e.height))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")


def root_window_bind_callback(*args):
    print("root_window_bind_callback()", *args)           

def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit()        

root_window = None
slaves_mcfg = None

if __name__ == "__main__":
    # gui = GUI()

    # Create the root window
    root_window = Tk()   
    root_window.title('DigiFoods - Inline Sensing')       # Set window title    
    root_window.geometry("1400x1000")     # Set window size width x height   1350 x 750
    root_window.config(background = "white")     #Set window background color  
    root_window.columnconfigure( 0, weight = 1 ) # Stretch Column 0 to fit width.
    root_window.rowconfigure( 0, weight = 1 ) # Stretch row 0 to fit height. 
    root_window.resizable(width=False, height=False)         # This makes the GUI of fixed size and prevents resizing.
    root_window.bind('<Return>', root_window_bind_callback )            # This gets the values entered in the gui.
    root_window.lift()       # Bring window forwards
    root_window.attributes('-topmost', True)
    root_window.protocol("WM_DELETE_WINDOW", on_closing)            # Let the window wait for any events

    slaves_mcfg = Slaves_Modbus_Config()       # Get configurations of all slaves.
    slaves_mcfg.get_config()

    # Place frames for each slave.
    slave_1 = rs485_gui_slave(window = root_window, slave_number=1)
    slave_1.gen_slave_modbus_gui()
    slave_1.canvas.grid(row = 0, column = 0,  columnspan = 2)
    
    # Place the vertical bar        
    slave_1.vbar.grid(row=0, column = 1, sticky="ns", columnspan=1, rowspan=1)

    slave_2 = rs485_gui_slave(window = root_window, slave_number=2)
    slave_2.gen_slave_modbus_gui()
    slave_2.canvas.grid(row = 0, column = 3, columnspan = 2)
    
    # Place the vertical bar        
    # slave_2.vbar.grid(row=0, column = 4, sticky="ns", columnspan=1, rowspan=1)    

    root_window.mainloop()       # Blocking function.        


# DUMP

# class GUI():
#     def __init__(self):
#         self.rs485_port = ""
#         self.rs485_baud_rate = 9600
#         self.rs485_serial_config = "8N1"
#         self.class_variables = {}
#         self.window = None
#         self.slaves_mcfguration = slaves_mcfg()
#         self.slaves_mcfguration.get_config()
#         self.slaves = {}

#         # Create N slaves based on the XLSX file
#         for slave in range(0, self.slaves_mcfguration.max_num_of_slaves):
#             self.slaves[str(slave)] = rs485_gui_slave() 

     # # If the slave_dict has the Nth holding_register we create and place a check button on the frame, else, we break out of the for loop.
                # if "slave_" + str(self.slave_number) + "_holding_register_" + str(holding_reg_num) in slaves_mcfg.dict:
                #     # Create and place check buttons
                #     self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_var"] = tk.StringVar()
                #     self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num)] = tk.Checkbutton(self.frame, 
                #                                                                                 text = "holding_register " + str(holding_reg_num) + " (" + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_holding_register_" + str(holding_reg_num)] + ")",
                #                                                                                 variable = self.gui_dict['Check_dict']['holding_register_' + str(holding_reg_num) + "_var"], 
                #                                                                                 onvalue = 1, 
                #                                                                                 offvalue = 0, 
                #                                                                                 command = self.on_holding_register_button)

                #     self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num)].grid(row = 4 + holding_reg_num, column = 0, sticky = "w", pady = 2, columnspan = 2)            
            # # Display the desired value.
                # self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_target"] = Label(self.frame, 
                #                                                                                     text = "target value = ", 
                #                                                                                     bg = "white", wraplength = self.canvas_width - 10)

                # self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_target"].grid(row = 4 + coil_num + discrete_inputs_num + holding_reg_num * 2 + input_reg_num + 2, column = 3, sticky = "w", pady = 2, columnspan = 1)
                
                # # Create Entry box and place it.
                # self.gui_dict['Entry_dict']['input_register_' + str(input_reg_num) + "_target_StringVar"] = tk.StringVar()
                # self.gui_dict['Entry_dict']['input_register_' + str(input_reg_num) + "_target"] = Entry(self.frame, 
                #                                                                                                     textvariable = self.gui_dict['Entry_dict']['input_register_' + str(input_reg_num) + "_target_StringVar"],
                #                                                                                                     border=1, width=10)
                # self.gui_dict['Entry_dict']['input_register_' + str(input_reg_num) + "_target"].grid(row = 4 + coil_num + discrete_inputs_num + holding_reg_num * 2 + input_reg_num + 2, column = 4, sticky = "e", pady = 2, columnspan = 1)                                                                                                          


