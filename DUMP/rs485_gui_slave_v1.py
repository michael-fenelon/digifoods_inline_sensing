# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy


class rs485_gui_slave():
    def __init__(self, window = None, slave_number = None, modbus_interface = None, slaves_mcfg = None, color = "white"):
        self.window = window
        # Difference between slave_number and slave_address.
        # These values don't have to match. slave number is a user's identification of a slave. 
        # slave_address is the address in the modbus RTU protocol  to access a slave.
        # Eg: slave_number = 1, some device that performs a function. 
        # Then, slave_address can be any available address, eg 1, 2, 34, 69... upto 127
        self.slave_number = slave_number
        self.slave_address = None
        self.mi = modbus_interface     
        self.slaves_mcfg = slaves_mcfg  # Will changes to this variable reflect in other slaves and tabs ? 
        #We don't create local copy of the self.slaves_mcfg variable since in the GUI this variable would need to be accessed across all tabs and slaves.
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
        # Create a canvas for the Wavelengths and XLSX sheet
        # Canvas are scrollable, Frames are not.
        # So we create a Frame and put it on a canvas so that the frame and canvas become scrollable.
        self.canvas_height = 800
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
        self.gui_dict['Label_dict']['Name'] = Label(self.frame, text = "Name : " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Name"], bg = self.color, wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Address'] = Label(self.frame, text = "Address : " + str(self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Address"]), bg = self.color, wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Info'] = Label(self.frame, text = "Info : " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Info"], bg = self.color, wraplength = self.canvas_width - 10)
        self.gui_dict['Label_dict']['Board'] = Label(self.frame, text = "Board : " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Board"], bg = self.color, wraplength = self.canvas_width - 10)
        
        # Placement of Label widgets on the slave's canvas' frame.
        self.gui_dict['Label_dict']['Name'].grid(row = 0, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Address'].grid(row = 1, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Info'].grid(row = 2, column = 0, sticky = "w", pady = 2, columnspan = 2) 
        self.gui_dict['Label_dict']['Board'].grid(row = 3, column = 0, sticky = "w", pady = 2, columnspan = 2)

        self.row_counter = 3

        self.slave_address = int(self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Address"])  # Get the slave's address

        # Read upto 100 coils, digital output. Write only.        
        for coil_num in range(0, 100):
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)] = Label(self.frame, text = "Coil " + str(coil_num) + ": " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)], bg = self.color, wraplength = 200)
            # self.gui_dict['Label_dict']['Coil_' + str(coil_num)].grid(row = 4 + coil_num, column = 0, sticky = "w", pady = 2, columnspan = 2)

            # If the slave_dict has the Nth coil we create and place a check button on the frame, else, we break out of the for loop.
            # if the key "slave_N_Coil_M" exists in the self.slaves_mcfg.dict
            if "slave_" + str(self.slave_number) + "_Coil_" + str(coil_num) in self.slaves_mcfg.dict:
                self.row_counter = self.row_counter + 1
                self.coils_list.append(0)        

                self.gui_dict['Label_dict']['Coil_' + str(coil_num)] = Label(self.frame, text = "Coil " + str(coil_num) + ": " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Coil_" + str(coil_num)], bg = self.color, wraplength = 200)
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
            if "slave_" + str(self.slave_number) + "_Discrete_input_" + str(discrete_inputs_num) in self.slaves_mcfg.dict:  
                self.row_counter = self.row_counter + 1

                self.discrete_inputs_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num)] = Label(self.frame, 
                                                                                                    text = "Discrete input " + str(discrete_inputs_num) + ": " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Discrete_input_" + str(discrete_inputs_num)], 
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
            if "slave_" + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num) in self.slaves_mcfg.dict:  
                self.row_counter = self.row_counter + 1

                self.holding_reg_list.append(0)

                # Update holding registers with min and max allowed values
                value = self.slaves_mcfg.dict["slave_" + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num)]
                splits = value.split(":")
                # print("splits = ", splits)

                # print("Slave number ", self.slave_number)
                if "range" in value:
                    self.holding_reg_min_list.append(float(splits[1]))
                    self.holding_reg_max_list.append(float(splits[2]))

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num)] = Label(self.frame, 
                                                                                                    text = "Holding_register " + str(holding_reg_num) + ": " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Holding_register_" + str(holding_reg_num)], 
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
            if "slave_" + str(self.slave_number) + "_Input_register_" + str(input_reg_num) in self.slaves_mcfg.dict:  
                self.row_counter = self.row_counter + 1

                self.input_reg_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)] = Label(self.frame, 
                                                                                                    text = "Input_register " + str(input_reg_num) + ": " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Input_register_" + str(input_reg_num)] + "  ,", 
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
        print("In update_slave() Updating coils for Slave ", self.slave_number)
        for i in range(0, len(self.coils_list)):
            value = self.gui_dict['Check_dict']['Coil_' + str(i) + "_var"].get()
            self.coils_list[i] = value        # Update the coil_list
            # print("In update_slave(): Pressed slave " + str(self.slave_number) + " Coil " + str(i) + " value = " + str(value)) 
        
        print("In update_slave(): Updated Coil list ", self.coils_list, len(self.coils_list))        
        res = self.mi.client.write_coils(address = 0, values = copy.deepcopy(self.coils_list), device_id = self.slave_address)      # We use a copy.deepcopy() since the client appends the variable self.coil_list for some reason !!!
        print("In update_slave(): write_coils : res :", res)

        # UPDATE DISCRETE INPUTS Read switches/status/ON/OFF from slave
        # values are bool: True/False
        res = self.mi.client.read_discrete_inputs(address = 0, count = len(self.discrete_inputs_list), device_id = self.slave_address)
        print("In update_slave(): discrete inputs : ", res)
        for i in range(0, len(self.discrete_inputs_list)):
            self.discrete_inputs_list[i] = res.bits[i]
            self.gui_dict['Label_dict']['discrete_input_' + str(i) + "_status"].config(text = str(self.discrete_inputs_list[i]))

        print("In update_slave(): discrete_inputs_list ",self.discrete_inputs_list )

        # UPDATE HOLDING REGISTERS:
        # Registers contain uint16_t values
        print("\nIn update_slave(): Updating holding registers for Slave ", self.slave_number)
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
                print("Invalid entries to holding registers, setting to default value: 0")
                self.holding_reg_list[holding_reg_num] = 0      # Just default the value to 0
                # break               
        res = self.mi.client.write_registers(address = 0, values = self.holding_reg_list, device_id = self.slave_address)      
        print("In update_slave(): write_registers : ", res)
        print("In update_slave(): Holding_reg_list ", self.holding_reg_list)

        # UPDATE INPUT REGISTERS: Read from slave and populate the GUI.
        # Registers contain uint16_t values
        res = self.mi.client.read_input_registers(address=0, count = len(self.input_reg_list), device_id=self.slave_address)
        print("In update_slave(): read_input_registers : ")
        for i in range(0,len(self.input_reg_list)):
            self.input_reg_list[i] = round(res.registers[i]/10.0,1)     # The values are scaled by 10, we divide and round them to 1 decimal point. 
            self.gui_dict['Label_dict']['input_register_' + str(i) + "_current"].config(text = str(self.input_reg_list[i]))

        print("In update_slave(): input registers = ", self.input_reg_list)

        self.window.update()

    def update_slave_reg_list(self):
        # UPDATE COILS: Write switches/status/ON/OFF to slave
        # values are bool: True/False
        print("In update_slave(): Updated Coil list ", self.coils_list, len(self.coils_list))        
        res = self.mi.client.write_coils(address = 0, values = copy.deepcopy(self.coils_list), device_id = self.slave_address)      # We use a copy.deepcopy() since the client appends the variable self.coil_list for some reason !!!
        print("In update_slave(): write_coils : res :", res)

        # UPDATE DISCRETE INPUTS Read switches/status/ON/OFF from slave
        # values are bool: True/False
        res = self.mi.client.read_discrete_inputs(address = 0, count = len(self.discrete_inputs_list), device_id = self.slave_address)
        print("In update_slave(): discrete inputs : ", res)
        for i in range(0, len(self.discrete_inputs_list)):
            self.discrete_inputs_list[i] = res.bits[i]
            self.gui_dict['Label_dict']['discrete_input_' + str(i) + "_status"].config(text = str(self.discrete_inputs_list[i]))
        print("In update_slave(): discrete_inputs_list ",self.discrete_inputs_list )

        # UPDATE HOLDING REGISTERS:
        # Registers contain uint16_t values                    
        res = self.mi.client.write_registers(address = 0, values = self.holding_reg_list, device_id = self.slave_address)      
        print("In update_slave(): write_registers : ", res)
        print("In update_slave(): Holding_reg_list ", self.holding_reg_list)

        # UPDATE INPUT REGISTERS: Read from slave and populate the GUI.
        # Registers contain uint16_t values
        res = self.mi.client.read_input_registers(address=0, count = len(self.input_reg_list), device_id=self.slave_address)
        print("In update_slave(): read_input_registers : ")
        for i in range(0,len(self.input_reg_list)):
            self.input_reg_list[i] = round(res.registers[i]/10.0,1)     # The values are scaled by 10, we divide and round them to 1 decimal point. 
            self.gui_dict['Label_dict']['input_register_' + str(i) + "_current"].config(text = str(self.input_reg_list[i]))

        print("In update_slave(): input registers = ", self.input_reg_list)
        
        self.window.update()        
        
    # Function that read the coils_list, discrete_input_list, holding_reg_list, input_register_list and updates the GUI.
    # This is required when an external control directly manipulates the ###_reg_lists instead of changing the gui's widgets
    def update_gui(self):
        # Read coil_list and update gui
        for coil_num in range(0, len(self.coils_list)):
            self.gui_dict['Check_dict']['Coil_' + str(coil_num) + "_var"].set(self.coils_list[coil_num])

        # Read discrete_input_list and update gui
        for discrete_inputs_num in range(0, len(self.discrete_inputs_list)):
            self.gui_dict['Label_dict']['discrete_input_' + str(discrete_inputs_num) + "_status"].configure(text = str(self.discrete_inputs_list[discrete_inputs_num]))

        # Read holding_reg_list and update gui
        for holding_reg_num in range(0, len(self.holding_reg_list)):
            self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"].configure(text = str(self.holding_reg_list[holding_reg_num]))

        # Read input_reg_list and update gui
        for input_reg_num in range(0, len(self.input_reg_list)):
            self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"].configure(text = str(self.input_reg_list[input_reg_num]))

        self.window.update()

    def on_config_canvas(self, e ):        
        # Set the canvas scrollregion to fit the whole of frame.
        # self.canvas.configure(scrollregion=(0, 0, e.width, e.height))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
