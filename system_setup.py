
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
    def __init__(self, window = None, slave_number = None, modbus_interface = None, color = "white"):
        self.window = window

        # Difference between slave_number and slave_address.
        # These values don't have to match. slave number is a user's identification of a slave. 
        # slave_address is the address in the modbus RTU protocol  to access a slave.
        # Eg: slave_number = 1, some device that performs a function. 
        # Then, slave_address can be any available address, eg 1, 2, 34, 69... upto 127
        self.slave_number = slave_number
        self.slave_address = None
        self.mi = modbus_interface     
        self.color = color   
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
        self.canvas_width = 500 
        self.canvas = tk.Canvas(self.window, bg="white", height = self.canvas_height, width = self.canvas_width, background= "white",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width-10, height = self.canvas_height-10, background= self.color)        
        self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )                       
        self.vbar = tk.Scrollbar(self.window, orient = 'vertical', command = self.canvas.yview)        
        # vbar = tk.Scrollbar(self.frame, orient = 'vertical', command = self.canvas.yview)        

        self.canvas.config(yscrollcommand = self.vbar.set)
        self.frame.bind('<Configure>', self.on_config_canvas)  
        # self.frame.bind_all("<Button-4>", self.on_mouse_wheel)   # Linux up
        # self.frame.bind_all("<Button-5>", self.on_mouse_wheel)   # Linux down        

        # Definitions
        self.gui_dict['Label_dict']['Name'] = Label(self.frame, text = "Name : " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Name"], bg = self.color, wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Address'] = Label(self.frame, text = "Address : " + str(slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Address"]), bg = self.color, wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Info'] = Label(self.frame, text = "Info : " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Info"], bg = self.color, wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Board'] = Label(self.frame, text = "Board : " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Board"], bg = self.color, wraplength = self.canvas_width - 10)
        
        # Placement of Label widgets on the slave's canvas' frame.
        self.gui_dict['Label_dict']['Name'].grid(row = 0, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Address'].grid(row = 1, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Info'].grid(row = 2, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Board'].grid(row = 3, column = 0, sticky = "w", pady = 2, columnspan = 2)

        self.row_counter = 3

        self.slave_address = int(slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Address"])  # Get the slave's address

        # Read upto 100 coils, digital output. Write only.        
        for coil_num in range(0, 100):
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)] = Label(self.frame, text = "Coil " + str(coil_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)], bg = self.color, wraplength = 200)
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)].grid(row = 4 + coil_num, column = 0, sticky = "w", pady = 2, columnspan = 2)

            # If the slave_dict has the Nth coil we create and place a check button on the frame, else, we break out of the for loop.
            # if the key "slave_N_Coil_M" exists in the slaves_mcfg.dict
            if "slave_" + str(self.slave_number) + "_Coil_" + str(coil_num) in slaves_mcfg.dict:
                self.row_counter = self.row_counter + 1
                self.coils_list.append(0)        

                self.gui_dict['Label_dict']['Coil_' + str(coil_num)] = Label(self.frame, text = "Coil " + str(coil_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)], bg = self.color, wraplength = 200)
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
                                                                                                    bg = self.color, wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num)].grid(row = self.row_counter, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Add ON/OFF labels to show status of the discrete inputs.
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num) + "_status"] = Label(self.frame, 
                                                                                                    text = "False", 
                                                                                                    bg = self.color, fg="orange" , wraplength = self.canvas_width - 10)
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

                # print("Slave number ", self.slave_number)
                if "range" in value:
                    self.holding_reg_min_list.append(float(splits[1]))
                    self.holding_reg_max_list.append(float(splits[2]))

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num)] = Label(self.frame, 
                                                                                                    text = "Holding_register " + str(holding_reg_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num)], 
                                                                                                    bg = self.color, wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num)].grid(row = self.row_counter + holding_reg_num * 2, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Display current value
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = "current value = ", 
                                                                                                    bg = self.color, wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"].grid(row = self.row_counter + holding_reg_num * 2 + 1, column = 1, sticky = "e", pady = 2, columnspan = 1)
               
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = str(self.holding_reg_list[holding_reg_num]), 
                                                                                                    bg = self.color, wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"].grid(row = self.row_counter + holding_reg_num * 2 + 1, column = 2, sticky = "w", pady = 2, columnspan = 1)

                # # Display the target value.
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_target"] = Label(self.frame, 
                                                                                                    text = "target value = ", 
                                                                                                    bg = self.color, wraplength = self.canvas_width - 10)

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
                                                                                                    bg = self.color, wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)].grid(row = self.row_counter, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Display current value
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = "current value = ", 
                                                                                                    bg = self.color, wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"].grid(row = self.row_counter, column = 1, sticky = "e", pady = 2, columnspan = 1)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = str(self.input_reg_list[input_reg_num]), 
                                                                                                    bg = self.color, wraplength = self.canvas_width - 10)

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

                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"].configure(text = str(self.holding_reg_list[holding_reg_num]))
            except:
                print("Invalid entries to holding registers !")
                break               
        res = self.mi.client.write_registers(address = 0, values = self.holding_reg_list, device_id = self.slave_address)      
        print("write_registers : ", res)

        # UPDATE INPUT REGISTERS: Read from slave and populate the GUI.
        # Registers contain uint16_t values
        res = self.mi.client.read_input_registers(address=0, count = len(self.input_reg_list), device_id=self.slave_address)
        print("read_input_registers : ")
        for i in range(0,len(self.input_reg_list)):
            self.input_reg_list[i] = res.registers[i]            
            self.gui_dict['Label_dict']['input_register_' + str(i) + "_current"].config(text = str(self.input_reg_list[i]))
        
    def on_config_canvas(self, e ):        
        # Set the canvas scrollregion to fit the whole of frame.
        # self.canvas.configure(scrollregion=(0, 0, e.width, e.height))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

class SAMPLE_BYPASS():
    def __init__(self, window  = None, data_exchange = None, slave = None, color = "white"):
        self.window = window
        self.data_exchange = data_exchange        
        self.slave = slave
        self.color = color        
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Entry_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Radio_dict':{}, 'Progress_bar':{} }
        self.gen_sample_bypass_gui()        

    def gen_sample_bypass_gui(self):
        # Enable module
        # Auto / debug mode : check button
        # tare load cell: Button + Label
        # get_weight: Buttom + Label
        # Set/ Entry box for desired target sample volume/weight
        # Start/ stop sample withdraw, given a flow rate/ PWM value, Pumps to run until we withdraw 150ml of sample
        # Some progress bar to monitor the level/ weight of the sample in the bottle. 
        # Start/ stop sample infusion into centrifuge, given a flow rate/ PWM value. 
        # Same progress bar to denote the sample/ weight level in the bottle
        # Get Humidity and Temperature info, lowest priority 

        self.canvas_height = 500
        self.canvas_width = 500 
        self.canvas = tk.Canvas(self.window, bg="white", height = self.canvas_height, width = self.canvas_width, background= "white",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width-10, height = self.canvas_height-10, background= self.color)        
        self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )                                                               

        self.gui_dict['Check_dict']['enable_sample_bypass_IntVar'] = IntVar()
        self.gui_dict['Check_dict']['enable_sample_bypass'] = Checkbutton(self.frame, 
                                                                            text="RUN: Sample bypass",
                                                                            variable=self.gui_dict['Check_dict']['enable_sample_bypass_IntVar'],
                                                                            onvalue=True,
                                                                            offvalue=False,
                                                                            height=1, 
                                                                            width=50,
                                                                            command=self.sample_bypass_enable)

        self.gui_dict['Radio_dict']['auto_debug_IntVar'] = StringVar(value="auto")
        self.gui_dict['Radio_dict']['auto'] = tk.Radiobutton(self.frame, text="Auto ", variable=self.gui_dict['Radio_dict']['auto_debug_IntVar'], value="auto", height=1, width=20)
        self.gui_dict['Radio_dict']['debug'] = tk.Radiobutton(self.frame, text="Debug", variable=self.gui_dict['Radio_dict']['auto_debug_IntVar'], value="debug", height=1, width=20)                                                                           
        self.gui_dict['Button_dict']['sample_bypass_start'] = Button(self.frame,
                                                                    text="Start",
                                                                    command=self.sample_bypass_start, 
                                                                    height=1, width = 20)

        self.gui_dict['Button_dict']['tare'] = Button(self.frame, text="Tare load cell", command=self.sample_bypass_tare, height=1, width = 20)
        self.gui_dict['Button_dict']['get_weight'] = Button(self.frame, text=" get sample weight ",  command=self.sample_bypass_get_weight, height=1, width=20)
        self.gui_dict['Label_dict']['get_weight'] = Label(self.frame, text="### grams")
        self.gui_dict['Label_dict']['set_weight'] = Label(self.frame, text="Set sample weight to withdraw (0 to 200 grams)", wraplength=250)
        self.gui_dict['Entry_dict']['set_weight_DoubleVar'] = DoubleVar(value=100.0)
        self.gui_dict['Entry_dict']['set_weight'] = Entry(self.frame, textvariable=self.gui_dict['Entry_dict']['set_weight_DoubleVar'], width=20)
        
        # Withdraw
        self.gui_dict['Check_dict']['start_stop_withdraw_IntVar'] = IntVar(value=0)
        self.gui_dict['Check_dict']['start_stop_withdraw'] = Checkbutton(self.frame,
                                                                        text="   WITHDRAW Sample: Start / Stop",
                                                                        variable=self.gui_dict['Check_dict']['start_stop_withdraw_IntVar'], 
                                                                        onvalue=1,
                                                                        offvalue=0,
                                                                        command=self.sample_bypass_withdraw,
                                                                        height=1,
                                                                        width=50)
        self.gui_dict['Progress_bar']['withdraw_progress'] = ttk.Progressbar(self.frame, orient='horizontal', length=400,mode="determinate")

        # Infuse
        self.gui_dict['Check_dict']['start_stop_infuse_IntVar'] = IntVar(value=0)
        self.gui_dict['Check_dict']['start_stop_infuse'] = Checkbutton(self.frame,
                                                                        text="   INFUSE Sample: Start / Stop",
                                                                        variable=self.gui_dict['Check_dict']['start_stop_infuse_IntVar'], 
                                                                        onvalue=1,
                                                                        offvalue=0,
                                                                        command=self.sample_bypass_infuse,
                                                                        height=1,
                                                                        width=50)
        self.gui_dict['Progress_bar']['infuse_progress'] = ttk.Progressbar(self.frame, orient='horizontal', length=400,mode="determinate")

        self.gui_dict['Label_dict']['humidity'] = Label(self.frame, text="Humidity (RH) ")
        self.gui_dict['Label_dict']['humidity_value'] = Label(self.frame, text="")
        self.gui_dict['Label_dict']['temperature'] = Label(self.frame, text="Temperature (deg C) ")
        self.gui_dict['Label_dict']['temperature_value'] = Label(self.frame, text="")        

        # Place all the widgets on the self.frame.
        self.canvas.grid(row=0, column=0, sticky="nw", padx=5, pady=50)
        self.gui_dict['Check_dict']['enable_sample_bypass'].grid(row = 0, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Radio_dict']['auto'].grid(row = 1, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Radio_dict']['debug'].grid(row = 2, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Button_dict']['sample_bypass_start'].grid(row = 3, column = 0, sticky = "nw", pady = 2, columnspan = 2)
        self.gui_dict['Button_dict']['tare'].grid(row = 4, column = 0, sticky = "nw", pady = 2, columnspan = 2)
        self.gui_dict['Button_dict']['get_weight'].grid(row = 5, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Label_dict']['get_weight'].grid(row = 5, column = 1, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Label_dict']['set_weight'].grid(row = 6, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Entry_dict']['set_weight'].grid(row = 6, column = 1, sticky = "nw", pady = 2, columnspan = 1)        
        self.gui_dict['Check_dict']['start_stop_withdraw'].grid(row = 7, column = 0, sticky = "nw", pady = 2, columnspan = 2)
        self.gui_dict['Progress_bar']['withdraw_progress'].grid(row = 8, column = 0, sticky = "nw", pady = 2, columnspan = 2)
        self.gui_dict['Check_dict']['start_stop_infuse'].grid(row = 9, column = 0, sticky = "nw", pady = 2, columnspan = 2)
        self.gui_dict['Progress_bar']['infuse_progress'].grid(row = 10, column = 0, sticky = "nw", pady = 2, columnspan = 2)
        self.gui_dict['Label_dict']['humidity'].grid(row = 11, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Label_dict']['humidity_value'].grid(row = 11, column = 1, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Label_dict']['temperature'].grid(row = 12, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Label_dict']['temperature_value'].grid(row = 12, column = 1, sticky = "nw", pady = 2, columnspan = 1)
        print("Complete gen_gui()")

    def sample_bypass_enable(self):
        pass

    def sample_bypass_start(self):
        pass
    
    def sample_bypass_tare(self):
        pass

    def sample_bypass_get_weight(self):
        pass        

    def sample_bypass_withdraw(self):
        pass    

    def sample_bypass_infuse(self):
        pass        

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
    window_width = 1600
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

    # Notebook widget
    notebook = ttk.Notebook(root_window)

    # # Place frames for each slave.
    # slave_1 = rs485_gui_slave(window = root_window, slave_number = 1, modbus_interface = mi, color="pale turquoise")
    # slave_1.gen_slave_modbus_gui()
    # slave_1.canvas.grid(row = 0, column = 0, sticky = "nw",  columnspan = 1)        
    # slave_1.vbar.grid(row = 0, column = 1, sticky = "ns", columnspan = 1, rowspan = 1)  

    # slave_2 = rs485_gui_slave(window = root_window, slave_number = 2, modbus_interface = mi, color="light goldenrod")
    # slave_2.gen_slave_modbus_gui()
    # slave_2.canvas.grid(row = 0, column = 2, sticky = "nw", columnspan = 1)           
    # slave_2.vbar.grid(row = 0, column = 3, sticky="ns", columnspan = 1, rowspan=1) 

    # slave_3 = rs485_gui_slave(window = root_window, slave_number = 3, modbus_interface = mi, color="white")
    # slave_3.gen_slave_modbus_gui()
    # slave_3.canvas.grid(row = 0, column = 4, sticky = "nw", columnspan = 1)        
    # slave_3.vbar.grid(row = 0, column = 5, sticky="ns", columnspan = 1, rowspan=1)           

    # Tab 1 : For sample extraction from the bypass with Y strainer    
    tab_1_sample_bypass_window = ttk.Frame(notebook, border= 2, height=window_height, width=window_width, padding=1)
    sample_bypass = SAMPLE_BYPASS(window  = root_window, data_exchange = None, slave = None)    

    tab_2_sample_bypass_window = ttk.Frame(notebook, border= 2, height=window_height, width=window_width, padding=1)
    sample_bypass_2 = SAMPLE_BYPASS(window  = root_window, data_exchange = None, slave = None)      

    root_window.bind('<Return>', root_window_bind_callback )            # This gets the values entered in the gui.
    root_window.lift()       # Bring window forwards
    # root_window.attributes('-topmost', True)
    root_window.protocol("WM_DELETE_WINDOW", on_closing)            # Let the window wait for any events


    s = ttk.Style()
    s.configure('TNotebook.Tab', font=('URW Gothic L','11','bold') )        # Gothic <3 :D !

    

    notebook.add(tab_1_sample_bypass_window, text='  Sample Bypass  ')    
    notebook.add(tab_2_sample_bypass_window, text='  Sample Bypass  2')   

    notebook.grid(row=0, column=0)

    # notebook.pack()
    notebook.bind("<<NotebookTabChanged>>", tab_selected)       # Bind a monitor to check if we change between Tabs.

    # root_window.grid_columnconfigure((0,2,4), weight=2, uniform="column")   # This spaces the frame equally in columns    

    root_window.mainloop()       # Blocking function.        


# DUMP
