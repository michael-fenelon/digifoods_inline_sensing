
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
from modbus_interface import Modbus_Interface
from watchpoints import watch

class rs485_gui_slave():
    def __init__(self, window = None, slave_number = None, modbus_interface = None):
        self.window = window

        # Difference between slave_number and slave_address.
        # These values don't have to match. slave number is a user's identification of a slave. 
        # slave_address is the address in the modbus RTU protocol  to access a slave.
        # Eg: slave_number = 1, some device that performs a function. 
        # Then, slave_address can be any available address, eg 1, 2, 34, 69... upto 127
        self.slave_number = slave_number
        self.slave_address = None
        self.mi = modbus_interface        
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Entry_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{} }
        self.coils_list = []            # Coils = Digital outputs/writes, Eg: LED, Relays
        self.discrete_inputs_list = []  # Discrete Inputs = Digital inputs/reads, Eg: Switches
        self.holding_reg_list = []      # Holding registers = 16bit variable values, R+W
        self.holding_reg_min_list = []
        self.holding_reg_max_list = []
        self.input_reg_list = []        # Input_registers = 16bit variable values, R only.
        self.row_counter = 0            # Just to keep track of the tkinter frame row for grid()
        # self.window.bind('<Return>', self.window_bind_callback )            # This gets the values entered in the gui.

    def gen_slave_modbus_gui(self):  
        global slaves_mcfg    
        # Create a canvas for the Wavelengths and XLSX sheet
        # Canvas are scrollable, Frames are not.
        # So we create a Frame and put it on a canvas so that the frame and canvas become scrollable.
        self.canvas_height = 400
        self.canvas_width = 550 
        self.canvas = tk.Canvas(self.window, bg="white", height = self.canvas_height, width = self.canvas_width, background= "white",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width-10, height = self.canvas_height-10, background= "white")        
        self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )                       
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

        self.row_counter = 3

        self.slave_address = int(slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Address"])  # Get the slave's address

        # Read upto 100 coils, digital output. Write only.        
        for coil_num in range(0, 100):
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)] = Label(self.frame, text = "Coil " + str(coil_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)], bg = "white", wraplength = 200)
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)].grid(row = 4 + coil_num, column = 0, sticky = "w", pady = 2, columnspan = 2)

            # If the slave_dict has the Nth coil we create and place a check button on the frame, else, we break out of the for loop.
            # if the key "slave_N_Coil_M" exists in the slaves_mcfg.dict
            if "slave_" + str(self.slave_number) + "_Coil_" + str(coil_num) in slaves_mcfg.dict:
                self.row_counter = self.row_counter + 1
                self.coils_list.append(0)        

                self.gui_dict['Label_dict']['Coil_' + str(coil_num)] = Label(self.frame, text = "Coil " + str(coil_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)], bg = "white", wraplength = 200)
                self.gui_dict['Label_dict']['Coil_' + str(coil_num)].grid(row = 4 + coil_num, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Create and place check buttons
                self.gui_dict['Check_dict']['Coil_' + str(coil_num) + "_var"] = tk.IntVar()
                self.gui_dict['Check_dict']['Coil_' + str(coil_num)] = tk.Checkbutton(self.frame, 
                                                                                            text = "",
                                                                                            variable = self.gui_dict['Check_dict']['Coil_' + str(coil_num) + "_var"], 
                                                                                            onvalue = 1, 
                                                                                            offvalue = 0)                                                                                              
                # self.gui_dict['Check_dict']['Coil_' + str(coil_num)] = tk.Checkbutton(self.frame, 
                #                                                                             text = "",
                #                                                                             variable = self.gui_dict['Check_dict']['Coil_' + str(coil_num) + "_var"], 
                #                                                                             onvalue = 1, 
                #                                                                             offvalue = 0, 
                #                                                                             command = lambda clicked_coil = coil_num : self.update_coils(clicked_coil))                

                self.gui_dict['Check_dict']['Coil_' + str(coil_num)].grid(row = self.row_counter, column = 2, sticky = "w", pady = 2, columnspan = 2)                                      
            else:
                print("No more coils !")
                break

        # print("coils_list ", self.coils_list)

        # Discrete Inputs. Read upto 100 discrete/digital inputs. Read only
        for discrete_inputs_num in range(0,100):
            if "slave_" + str(self.slave_number) + "_Discrete_input_" + str(discrete_inputs_num) in slaves_mcfg.dict:  
                self.row_counter = self.row_counter + 1

                self.discrete_inputs_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num)] = Label(self.frame, 
                                                                                                    text = "Discrete input " + str(discrete_inputs_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Discrete_input_" + str(discrete_inputs_num)], 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num)].grid(row = self.row_counter, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Add ON/OFF labels to show status of the discrete inputs.
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num) + "_status"] = Label(self.frame, 
                                                                                                    text = "False", 
                                                                                                    bg = "white", fg="orange" , wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num) + "_status"].grid(row = self.row_counter, column = 2, sticky = "w", pady = 2, columnspan = 2)                

        # Holding registers, read upto 100 holding registers. Read + Write.
        for holding_reg_num in range(0, 100):
            # # If the slave_dict has the Nth holding_register we create and place a check button on the frame, else, we break out of the for loop.
            if "slave_" + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num) in slaves_mcfg.dict:  
                self.row_counter = self.row_counter + 1

                self.holding_reg_list.append(0)

                # Update holding registers with min and max allowed values
                value = slaves_mcfg.dict["slave_" + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num)]
                splits = value.split(":")
                # print("splits = ", splits)
                self.holding_reg_min_list.append(float(splits[1]))
                self.holding_reg_max_list.append(float(splits[2]))

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num)] = Label(self.frame, 
                                                                                                    text = "Holding_register " + str(holding_reg_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num)], 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num)].grid(row = self.row_counter + holding_reg_num * 2, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Display current value
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = "current value = ", 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"].grid(row = self.row_counter + holding_reg_num * 2 + 1, column = 1, sticky = "e", pady = 2, columnspan = 1)
               
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = str(self.holding_reg_list[holding_reg_num]), 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"].grid(row = self.row_counter + holding_reg_num * 2 + 1, column = 2, sticky = "w", pady = 2, columnspan = 1)

                # # Display the target value.
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_target"] = Label(self.frame, 
                                                                                                    text = "target value = ", 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_target"].grid(row = self.row_counter + holding_reg_num * 2 + 2, column = 1, sticky = "e", pady = 2, columnspan = 1)
                
                # # Create Entry box and place it.
                self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target_StringVar"] = tk.StringVar()
                self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target"] = Entry(self.frame, 
                                                                                                            textvariable = self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target_StringVar"],                                                                                                           
                                                                                                            border=1, width=10)
                # self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target_StringVar"].trace_add(mode = "write", callback = self.update_holding_reg)                                                                                                            

                self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target"].grid(row = self.row_counter + holding_reg_num * 2 + 2, column = 2, sticky = "w", pady = 2, columnspan = 1)                                                                                                          
            else:
                print("No more holding_registers !")
                break

        self.row_counter = self.row_counter + holding_reg_num * 2 + 2
        print("Holding register min list ", self.holding_reg_min_list)
        print("Holding register max list ", self.holding_reg_max_list)

        # # Input registers, read upto 100 Input registers. Read only
        for input_reg_num in range(0, 100):
            # # If the slave_dict has the Nth input_register we create and place a check button on the frame, else, we break out of the for loop.
            if "slave_" + str(self.slave_number) + "_Input_register_" + str(input_reg_num) in slaves_mcfg.dict:  
                self.row_counter = self.row_counter + 1

                self.input_reg_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)] = Label(self.frame, 
                                                                                                    text = "Input_register " + str(input_reg_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Input_register_" + str(input_reg_num)] + "  ,", 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)].grid(row = self.row_counter, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Display current value
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = "current value = ", 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"].grid(row = self.row_counter, column = 1, sticky = "e", pady = 2, columnspan = 1)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = str(self.input_reg_list[input_reg_num]), 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"].grid(row = self.row_counter, column = 2, sticky = "w", pady = 2, columnspan = 1)

            else:
                print("No more input_registers !")
                break

        # Update button: Large vertical button used and command/callback to read all the holding register entries, update the holding_reg_list and send value to the slave.
        # We use a button so that only ONE slave uses the RS485 line at a time; avoids RS485 communication conflicts between slaves.
        self.gui_dict['Button_dict']['update'] = Button(self.frame, text = "update", command = self.update_slave, wraplength = 50) 
        self.gui_dict['Button_dict']['update'].grid(row = 4, column = 3, sticky = "ns", pady = 2, columnspan = 1, rowspan = self.row_counter)

    # def update_coils(self, clicked_coil):            
    #     value = self.gui_dict['Check_dict']['Coil_' + str(clicked_coil) + "_var"].get()
    #     self.coils_list[clicked_coil] = value        # Update the coil_list
    #     print("Pressed slave " + str(self.slave_number) + " Coil " + str(clicked_coil) + " value = " + str(value)) 
    #     print("Updated Coil list ", self.coils_list, len(self.coils_list))
    #     res = self.mi.client.write_coil(address = clicked_coil, value = value, device_id = self.slave_address)
    #     print("Updated coil result ", res)

    # Callback that gets all the values from the coil Checkboxes, Entry boxes and update the values in the slave
    # does sanity check for each entry and update the holding_reg.    
    def update_slave(self):
        # UPDATE COILS: Write switches/status/ON/OFF to slave
        # values are bool: True/False
        # Get the values of all check boxes and update self.coil_list
        print("Updating coils for Slave ", self.slave_number)
        for i in range(0, len(self.coils_list)):
            value = self.gui_dict['Check_dict']['Coil_' + str(i) + "_var"].get()
            self.coils_list[i] = value        # Update the coil_list
            print("Pressed slave " + str(self.slave_number) + " Coil " + str(i) + " value = " + str(value)) 
        
        print("Updated Coil list ", self.coils_list, len(self.coils_list))        
        res = self.mi.client.write_coils(address = 0, values = copy.deepcopy(self.coils_list), device_id = self.slave_address)      # We use a copy.deepcopy() since the client appends the variable self.coil_list for some reason !!!
        print("write_coils : ", res)

        # UPDATE DISCRETE INPUTS Read switches/status/ON/OFF from slave
        # values are bool: True/False
        res = self.mi.client.read_discrete_inputs(address = 0, count = len(self.discrete_inputs_list), device_id = self.slave_address)
        print("discrete inputs : ", res)
        for i in range(0, len(self.discrete_inputs_list)):
            self.discrete_inputs_list[i] = res.bits[i]
            self.gui_dict['Label_dict']['discrete_input_' + str(i) + "_status"].config(text = str(self.discrete_inputs_list[i]))

        # UPDATE HOLDING REGISTERS:
        # Registers contain uint16_t values
        print("\nUpdating holding registers for Slave ", self.slave_number)
        for holding_reg_num in range(0, len(self.holding_reg_list)):
            user_entry = copy.deepcopy(self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target_StringVar"].get())       # class str
            # print("user_entry = ", user_entry, type(user_entry), float(user_entry))  
            # Try to convert the user's input to floats, if invalid we return
            try:
                user_entry = copy.deepcopy(float(user_entry))
                # Sanity check: validity of the user's entry such as limits, floats, ints...etc                
                value = max(min(user_entry,self.holding_reg_max_list[holding_reg_num]), self.holding_reg_min_list[holding_reg_num])     # saturate or check of the value is within bounds
                print("Thresholded value ", value)
                
                self.holding_reg_list[holding_reg_num] = int(value)
                print("Inputting ", value , " to holding register")                        
                print("Updated holding register = ", self.holding_reg_list) 
            except:
                print("Invalid entries to holding registers !")
                break               
        res = self.mi.client.write_registers(address = 0, values = self.holding_reg_list, device_id = self.slave_address)      
        print("write_registers : ", res)

        # UPDATE INPUT REGISTERS: Read from slave and populate the GUI.
        # Registers contain uint16_t values
        res = self.mi.client.read_input_registers(address=0, count=2, device_id=self.slave_address)
        print("read_input_registers : ")
        for i in range(0,len(self.input_reg_list)):
            self.input_reg_list[i] = res.registers[i]            
            self.gui_dict['Label_dict']['input_register_' + str(i) + "_current"].config(text = str(self.input_reg_list[i]))
        
    def on_config_canvas(self, e ):        
        # Set the canvas scrollregion to fit the whole of frame.
        # self.canvas.configure(scrollregion=(0, 0, e.width, e.height))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def root_window_bind_callback(*args):
    print("root_window_bind_callback()", *args)           

def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit()        

root_window = None
slaves_mcfg = None
mi = None

if __name__ == "__main__":
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

    mi = Modbus_Interface()     

    # Place frames for each slave.
    slave_1 = rs485_gui_slave(window = root_window, slave_number = 1, modbus_interface = mi)
    slave_1.gen_slave_modbus_gui()
    slave_1.canvas.grid(row = 0, column = 0,  columnspan = 2)        
    slave_1.vbar.grid(row = 0, column = 1, sticky = "ns", columnspan = 1, rowspan = 1)  # Place the vertical bar        

    # slave_2 = rs485_gui_slave(window = root_window, slave_number=2)
    # slave_2.gen_slave_modbus_gui()
    # slave_2.canvas.grid(row = 0, column = 3, columnspan = 2)    
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

    # Function to bind the Enter key press and values from the entry boxes in the GUI.
    # There's no function/callback when a value is entered in the entry boxes.
    # So, we read all the entry boxes when the Enter key is press and process the values.
    # def window_bind_callback(self, *args):
    #     # print("Enter was pressed")
    #     # Update the holding registers with values from the GUI.
    #     print("\nUpdating holding registers for Slave ", self.slave_number)
    #     for holding_reg_num in range(0, len(self.holding_reg_list)):

    #         user_entry = copy.deepcopy(self.gui_dict['Entry_dict']['holding_register_' + str(holding_reg_num) + "_target_StringVar"].get())       # class str
    #         # print("user_entry = ", user_entry, type(user_entry), float(user_entry))  

    #         # Try to convert the user's input to floats, if invalid we return
    #         try:
    #             user_entry = copy.deepcopy(float(user_entry))
    #             # Sanity check: validity of the user's entry such as limits, floats, ints...etc                
    #             value = max(min(user_entry,self.holding_reg_max_list[holding_reg_num]), self.holding_reg_min_list[holding_reg_num])     # saturate or check of the value is within bounds
    #             print("Thresholded value ", value)
                
    #             self.holding_reg_list[holding_reg_num] = float(value)
    #             print("Inputting ", value , " to holding register")                        
    #             print("Updated holding register = ", self.holding_reg_list) 
    #         except:
    #             print("Invalid entries to holding registers !")
    #             return
