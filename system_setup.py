
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

    def gen_slave_modbus_gui(self):  
        global slaves_modbus_config    
        # Create a canvas for the Wavelengths and XLSX sheet
        self.canvas_height = 400
        self.canvas_width = 550 
        self.canvas = tk.Canvas(self.window, bg="white", height = self.canvas_height, width = self.canvas_width, background= "white",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width, height = self.canvas_height, background= "white")
        self.canvas.create_window( 0,0, window = self.frame, anchor=tk.NW )       
        vbar = tk.Scrollbar(self.frame, orient = 'vertical', command = self.canvas.yview)
        # hbar = tk.Scrollbar(self.window, orient = 'horizontal', command= self.canvas.xview)

        self.canvas.config(yscrollcommand = vbar.set)
        self.frame.bind('<Configure>', self.on_config_canvas)  

        # Definitions
        self.gui_dict['Label_dict']['Name'] = Label(self.frame, text = "Name : " + slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_Name"], bg = "white", wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Address'] = Label(self.frame, text = "Address : " + str(slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_Address"]), bg = "white", wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Info'] = Label(self.frame, text = "Info : " + slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_Info"], bg = "white", wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Board'] = Label(self.frame, text = "Board : " + slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_Board"], bg = "white", wraplength = self.canvas_width - 10)
        
        # Placement of Label widgets on the slave's canvas' frame.
        self.gui_dict['Label_dict']['Name'].grid(row = 0, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Address'].grid(row = 1, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Info'].grid(row = 2, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Board'].grid(row = 3, column = 0, sticky = "w", pady = 2, columnspan = 2) 




        # Read upto 100 coils, break when we reach the last one.        
        for coil_num in range(0, 100):
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)] = Label(self.frame, text = "Coil " + str(coil_num) + ": " + slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)], bg = "white", wraplength = 200)
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)].grid(row = 4 + coil_num, column = 0, sticky = "w", pady = 2, columnspan = 2)

            # If the slave_dict has the Nth coil we create and place a check button on the frame, else, we break out of the for loop.
            if "slave_" + str(self.slave_number) + "_Coil_" + str(coil_num) in slaves_modbus_config.dict:
                # Create and place check buttons
                self.gui_dict['Check_dict']['Coil_' + str(coil_num) + "_var"] = tk.IntVar()
                self.gui_dict['Check_dict']['Coil_' + str(coil_num)] = tk.Checkbutton(self.frame, 
                                                                                            text = "Coil " + str(coil_num) + " (" + slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)] + ")",
                                                                                            variable = self.gui_dict['Check_dict']['Coil_' + str(coil_num) + "_var"], 
                                                                                            onvalue = 1, 
                                                                                            offvalue = 0, 
                                                                                            command = self.on_coil_button)

                self.gui_dict['Check_dict']['Coil_' + str(coil_num)].grid(row = 4 + coil_num, column = 0, sticky = "w", pady = 2, columnspan = 2)                              
            else:
                print("No more coils !")
                break

        ## Holding registers
        for holding_register_num in range(0, 100):
            # # If the slave_dict has the Nth holding_register we create and place a check button on the frame, else, we break out of the for loop.
            if "slave_" + str(self.slave_number) + "_Holding_register_" + str(holding_register_num) in slaves_modbus_config.dict:            
                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['holding_register_' + str(holding_register_num)] = Label(self.frame, 
                                                                                                    text = "Holding_register " + str(holding_register_num) + ": " + slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_Holding_register_" + str(holding_register_num)], 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['holding_register_' + str(holding_register_num)].grid(row = 4 + coil_num + holding_register_num * 2 + 1, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Display current value
                self.gui_dict['Label_dict']['holding_register_' + str(holding_register_num) + "_current"] = Label(self.frame, 
                                                                                                    text = "current value = " + str(100), 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_register_num) + "_current"].grid(row = 4 + coil_num + holding_register_num * 2 + 2, column = 0, sticky = "e", pady = 2, columnspan = 1)

                

                # # Display the desired value.
                self.gui_dict['Label_dict']['holding_register_' + str(holding_register_num) + "_target"] = Label(self.frame, 
                                                                                                    text = "target value = ", 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_register_num) + "_target"].grid(row = 4 + coil_num + holding_register_num * 2 + 2, column = 3, sticky = "w", pady = 2, columnspan = 1)
                
                # Create Entry box and place it.
                self.gui_dict['Entry_dict']['holding_register_' + str(holding_register_num) + "_target_StringVar"] = tk.StringVar()
                self.gui_dict['Entry_dict']['holding_register_' + str(holding_register_num) + "_target"] = Entry(self.frame, 
                                                                                                                    textvariable = self.gui_dict['Entry_dict']['holding_register_' + str(holding_register_num) + "_target_StringVar"],
                                                                                                                    border=1, width=10)
                self.gui_dict['Entry_dict']['holding_register_' + str(holding_register_num) + "_target"].grid(row = 4 + coil_num + holding_register_num * 2 + 2, column = 4, sticky = "e", pady = 2, columnspan = 1)                                                                                                          



                # # If the slave_dict has the Nth holding_register we create and place a check button on the frame, else, we break out of the for loop.
                # if "slave_" + str(self.slave_number) + "_holding_register_" + str(holding_register_num) in slaves_modbus_config.dict:
                #     # Create and place check buttons
                #     self.gui_dict['Entry_dict']['holding_register_' + str(holding_register_num) + "_var"] = tk.StringVar()
                #     self.gui_dict['Entry_dict']['holding_register_' + str(holding_register_num)] = tk.Checkbutton(self.frame, 
                #                                                                                 text = "holding_register " + str(holding_register_num) + " (" + slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_holding_register_" + str(holding_register_num)] + ")",
                #                                                                                 variable = self.gui_dict['Check_dict']['holding_register_' + str(holding_register_num) + "_var"], 
                #                                                                                 onvalue = 1, 
                #                                                                                 offvalue = 0, 
                #                                                                                 command = self.on_holding_register_button)

                #     self.gui_dict['Entry_dict']['holding_register_' + str(holding_register_num)].grid(row = 4 + holding_register_num, column = 0, sticky = "w", pady = 2, columnspan = 2)                              
            else:
                print("No more holding_registers !")
                break


        # Place the vertical bar        
        vbar.grid(row=0, column = 12, sticky="ns", columnspan=2, rowspan=20)

    def on_coil_button(self):
        print("Pressed slave " + str(self.slave_number) + " Coil ???" )        

    def on_config_canvas(self, e ):        
        # Set the canvas scrollregion to fit the whole of frame.
        self.canvas.configure(scrollregion=(0, 0, e.width, e.height))
        # self.canvas.configure(scrollregion=self.canvas.bbox("all"))




def root_window_bind_callback(*args):
    print("root_window_bind_callback()", *args)           

def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit()        

root_window = None
slaves_modbus_config = None

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

    slaves_modbus_config = Slaves_Modbus_Config()       # Get configurations of all slaves.
    slaves_modbus_config.get_config()


    # Place frames for each slave.
    slave_1 = rs485_gui_slave(window = root_window, slave_number=1)
    slave_1.gen_slave_modbus_gui()
    slave_1.canvas.grid(row = 0, column = 0,  columnspan = 2)

    # slave_2 = rs485_gui_slave(window = root_window, slave_number=2)
    # slave_2.gen_slave_modbus_gui()
    # slave_2.canvas.grid(row = 0, column = 2, columnspan = 2)


    root_window.mainloop()       # Blocking function.        


# DUMP

# class GUI():
#     def __init__(self):
#         self.rs485_port = ""
#         self.rs485_baud_rate = 9600
#         self.rs485_serial_config = "8N1"
#         self.class_variables = {}
#         self.window = None
#         self.slaves_modbus_configuration = Slaves_Modbus_Config()
#         self.slaves_modbus_configuration.get_config()
#         self.slaves = {}

#         # Create N slaves based on the XLSX file
#         for slave in range(0, self.slaves_modbus_configuration.max_num_of_slaves):
#             self.slaves[str(slave)] = rs485_gui_slave() 


