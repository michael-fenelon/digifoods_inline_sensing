# import all components from the tkinter library
from tkinter import *
import tkinter as tk
import copy
from slaves_modbus_configuration import*
from pymodbus.client import ModbusSerialClient
from modbus_interface import Modbus_Interface
from watchpoints import watch

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
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Entry_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Scale_dict':{} }
        self.coils_list = []            # Coils = Digital outputs/writes, Eg: LED, Relays, Bool list
        self.discrete_inputs_list = []  # Discrete Inputs = Digital inputs/reads, Eg: Switches, Bool list
        self.holding_reg_list = []      # Holding registers = 16bit variable values, R+W, INT16_t list
        self.holding_reg_min_list = []
        self.holding_reg_max_list = []
        self.input_reg_list = []        # Input_registers = 16bit variable values, R only. INT16_T list
        self.row_counter = 0            # Just to keep track of the tkinter frame row for grid()
        # self.window.bind('<Return>', self.window_bind_callback )            # This gets the values entered in the gui.

    def gen_slave_modbus_gui(self):          
        # Create a canvas for the Wavelengths and XLSX sheet
        # Canvas are scrollable, Frames are not.
        # So we create a Frame and put it on a canvas so that the frame and canvas become scrollable.
        self.canvas_height = 800
        self.canvas_width = 800 
        self.canvas = tk.Canvas(self.window, bg="white", height = self.canvas_height, width = self.canvas_width, background= "white",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width-10, height = self.canvas_height-10, background= self.color)        
        self.canvas.create_window( 5, 5, window = self.frame, anchor=tk.NW )                       
        self.vbar = tk.Scrollbar(self.window, orient = 'vertical', command = self.canvas.yview, width = 30)        
        # vbar = tk.Scrollbar(self.frame, orient = 'vertical', command = self.canvas.yview)        

        self.canvas.config(yscrollcommand = self.vbar.set)
        self.frame.bind('<Configure>', self.on_config_canvas)  

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
                self.gui_dict['Check_dict']['Coil_' + str(coil_num)].grid(row = self.row_counter, column = 2, sticky = "w", pady = 2, columnspan = 2)                                      
            else:
                print("Completed coil list !")
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
            else:
                print("Completed discrete input list !")
                break

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
                if "range" in value or "pulse" in value:
                    self.holding_reg_min_list.append(float(splits[1]))
                    self.holding_reg_max_list.append(float(splits[2]))
                    try:
                        resolution = float(splits[3])
                        # print("resolution ", resolution)
                    except:
                        resolution = 1
                else:
                    self.holding_reg_min_list.append(0)
                    self.holding_reg_max_list.append(100)
                    resolution = 1

                # print("self.holding_reg_min_list ", self.holding_reg_min_list)
                # print("Resolution = ", resolution)

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
                
                # # Create Slider/Scale box and place it.
                self.gui_dict['Scale_dict']['holding_register_' + str(holding_reg_num) + "_target_DoubleVar"] = tk.DoubleVar()
                self.gui_dict['Scale_dict']['holding_register_' + str(holding_reg_num) + "_target"] = Scale(self.frame, 
                                                                                                            variable = self.gui_dict['Scale_dict']['holding_register_' + str(holding_reg_num) + "_target_DoubleVar"],
                                                                                                            from_=self.holding_reg_min_list[holding_reg_num],
                                                                                                            to=self.holding_reg_max_list[holding_reg_num],
                                                                                                            resolution= resolution,
                                                                                                            orient=HORIZONTAL, length=250, border=1, width=20)

                self.gui_dict['Scale_dict']['holding_register_' + str(holding_reg_num) + "_target"].grid(row = self.row_counter + holding_reg_num * 2 + 2, column = 2, sticky = "w", pady = 2, padx= 10, columnspan = 1)                                                                                                          
            else:
                print("Completed holding_registers list !")
                break

        self.row_counter = self.row_counter + holding_reg_num * 2 + 2
        # print("Holding register min list ", self.holding_reg_min_list)
        # print("Holding register max list ", self.holding_reg_max_list)

        # # Input registers, read upto 100 Input registers. Read only
        for input_reg_num in range(0, 100):
            # # If the slave_dict has the Nth input_register we create and place a check button on the frame, else, we break out of the for loop.
            if "slave_" + str(self.slave_number) + "_Input_register_" + str(input_reg_num) in self.slaves_mcfg.dict:  
                self.row_counter = self.row_counter + 1

                self.input_reg_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)] = Label(self.frame, 
                                                                                                    text = "Input_register " + str(input_reg_num) + ": " + self.slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Input_register_" + str(input_reg_num)], 
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
                print("Completed input_registers list !")
                break

        # Update button: Large vertical button used and command/callback to read all the holding register entries, update the holding_reg_list and send value to the slave.
        # We use a button so that only ONE slave uses the RS485 line at a time; avoids RS485 communication conflicts between slaves.
        self.gui_dict['Button_dict']['update'] = Button(self.frame, text = "update", command = self.update_slave_via_gui, wraplength = 50) 
        self.gui_dict['Button_dict']['update'].grid(row = 4, column = 3, sticky = "nse", pady = 2, columnspan = 1, rowspan = self.row_counter)

    # Callback that gets all the values from the coil Checkboxes, Scale/Slider, Entry boxes and update the values in the slave. 
    # Does sanity check for each entry and update the holding_reg.    
    def update_slave_via_gui(self):
        print("\nIn update_slave_via_gui() Updating Slave ", self.slave_number)

        # UPDATE COILS: Write switches/status/ON/OFF to slave, values are bool: True/False
        # Get the values of all check boxes and update self.coil_list        
        for i in range(0, len(self.coils_list)):
            value = self.gui_dict['Check_dict']['Coil_' + str(i) + "_var"].get()
            self.coils_list[i] = value        # Update the coil_list
            # print("In update_slave(): Pressed slave " + str(self.slave_number) + " Coil " + str(i) + " value = " + str(value))    # Debug
        
        print("In update_slave_via_gui(): Updated Coil list ", self.coils_list, len(self.coils_list))        
        res = self.mi.client.write_coils(address = 0, values = copy.deepcopy(self.coils_list), device_id = self.slave_address)      # We use a copy.deepcopy() since the client appends the variable self.coil_list for some reason !!!
        print("In update_update_slave_via_guislave(): write_coils : res :", res)

        # UPDATE DISCRETE INPUTS Read switches/status/ON/OFF from slave, values are bool: True/False. 
        res = self.mi.client.read_discrete_inputs(address = 0, count = len(self.discrete_inputs_list), device_id = self.slave_address)
        print("In update_slave_via_gui(): discrete inputs : ", res)
        for i in range(0, len(self.discrete_inputs_list)):
            self.discrete_inputs_list[i] = res.bits[i]
            self.gui_dict['Label_dict']['discrete_input_' + str(i) + "_status"].config(text = str(self.discrete_inputs_list[i]))
        print("In update_slave_via_gui(): discrete_inputs_list ",self.discrete_inputs_list )

        # UPDATE HOLDING REGISTERS. Registers contain int16_t values.                 
        for holding_reg_num in range(0, len(self.holding_reg_list)):
            user_entry = self.gui_dict['Scale_dict']['holding_register_' + str(holding_reg_num) + "_target_DoubleVar"].get()   # This is a float value         
            value = max(min(user_entry,self.holding_reg_max_list[holding_reg_num]), self.holding_reg_min_list[holding_reg_num])     # saturate or check of the value is within bounds
            # print("Thresholded value ", value)            
            self.holding_reg_list[holding_reg_num] = int(value)                        
            self.gui_dict['Label_dict']['holding_register_' + str(holding_reg_num) + "_current"].configure(text = str(self.holding_reg_list[holding_reg_num]))  

        # Write data to holding registers: Convert a generic INT16_t list to Pymodbus' default UINT16_t list -> Arduino's INT16_T list. 
        self.holding_reg_list = copy.deepcopy(self.mi.client.convert_to_registers(value=self.holding_reg_list, data_type=self.mi.client.DATATYPE.INT16, word_order="little") )       
        res = self.mi.client.write_registers(address = 0, values = self.holding_reg_list, device_id = self.slave_address)      # Send values to slave/device
        # print("In update_slave_via_gui(): write_registers : ", res)
        print("In update_slave_via_gui(): Holding_reg_list", self.holding_reg_list)

        # UPDATE INPUT REGISTERS: Read from slave and populate the GUI. Registers contain int16_t values. 
        # Read data: Convert from Arduino's INT16_T list -> Pymodbus's default UINT16 list -> Actual INT16 list
        print("In update_slave_via_gui(): read_input_registers : ")
        result = self.mi.client.read_input_registers(address=0, count = len(self.input_reg_list), device_id=self.slave_address)
        res = self.mi.client.convert_from_registers(result.registers, self.mi.client.DATATYPE.INT16, 'little')    #  little endian since arduino uses little endian
        for i in range(0,len(self.input_reg_list)):
            self.input_reg_list[i] = round(res[i]/10.0,1)     # The values are scaled by 10, we divide and round them to 1 decimal point. 
            self.gui_dict['Label_dict']['input_register_' + str(i) + "_current"].config(text = str(self.input_reg_list[i]))
        print("In update_slave_via_gui(): input registers = ", self.input_reg_list)

        self.window.update()    # Update the GUI with latest values.

    # Update the slave via the values in the *_reg_list. 
    # Don't care for values in the gui.
    def update_slave_via_reg_list(self):
        # UPDATE COILS: Write switches/status/ON/OFF to slave, values are bool: True/False. 
        print("\nIn update_slave_via_reg_list(): Updated Coil list ", self.coils_list, ", length of coil_list = ", len(self.coils_list))        
        res = self.mi.client.write_coils(address = 0, values = copy.deepcopy(self.coils_list), device_id = self.slave_address)      # We use a copy.deepcopy() since the client appends the variable self.coil_list for some reason !!!

        # UPDATE DISCRETE INPUTS Read switches/status/ON/OFF from slave, values are bool: True/False. 
        res = self.mi.client.read_discrete_inputs(address = 0, count = len(self.discrete_inputs_list), device_id = self.slave_address)        
        for i in range(0, len(self.discrete_inputs_list)):
            self.discrete_inputs_list[i] = res.bits[i]
            self.gui_dict['Label_dict']['discrete_input_' + str(i) + "_status"].config(text = str(self.discrete_inputs_list[i]))
        print("In update_slave_via_reg_list(): discrete_inputs_list ",self.discrete_inputs_list )

        # UPDATE HOLDING REGISTERS, Write data to Arduino, registers contain int16_t values.
        # Convert a generic INT16_t list to Pymodbus' default UINT16_t list -> Arduino's INT16_T list
        self.holding_reg_list = self.mi.client.convert_to_registers(value=self.holding_reg_list, data_type=self.mi.client.DATATYPE.INT16, word_order="little") 
        res = self.mi.client.write_registers(address = 0, values = self.holding_reg_list, device_id = self.slave_address)              
        print("In update_slave_via_reg_list(): Holding_reg_list ", self.holding_reg_list, ", length of holding_list = ", len(self.holding_reg_list))

        # UPDATE INPUT REGISTERS: Read from slave and populate the GUI. Registers contain int16_t values. 
        # Convert from Arduino's INT16_T list -> Pymodbus's default UINT16 list -> Actual INT16 list
        result = self.mi.client.read_input_registers(address=0, count = len(self.input_reg_list), device_id=self.slave_address)        
        res = self.mi.client.convert_from_registers(result.registers, self.mi.client.DATATYPE.INT16, 'little') 
        for i in range(0,len(self.input_reg_list)):
            self.input_reg_list[i] = round(res[i]/10.0,1)     # The values are scaled by 10, we divide and round them to 1 decimal point. 
            self.gui_dict['Label_dict']['input_register_' + str(i) + "_current"].config(text = str(self.input_reg_list[i]))

        print("In update_slave_via_reg_list(): input registers = ", self.input_reg_list, ", length of input_reg = ", len(self.input_reg_list))
        
        self.window.update()        
        
    # Function that read the coils_list, discrete_input_list, holding_reg_list, input_register_list and updates the GUI.
    # This is required when an external control directly manipulates the *_reg_lists instead of changing the gui's widgets
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

    # Function to enable or disable any user input buttons, sliders, check boxes...etc
    def enable_disable(self):
        pass


    def on_config_canvas(self, e ):        
        # Set the canvas scrollregion to fit the whole of frame.
        # self.canvas.configure(scrollregion=(0, 0, e.width, e.height))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

def root_window_bind_callback():
    print("In root_window_bind_callback():  ...")

def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit() 

if __name__ == "__main__":
    # Create the root window
    root_window = Tk()   
    root_window.title('RS485 Slave')       # Set window title    
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

    slaves_mcfg = Slaves_Modbus_Config()       # Get configurations of all slaves (read xlsx file)
    slaves_mcfg.get_config()
    mi = Modbus_Interface()     # Create a RS485 Modbus RTU interface with baud rate, 8N1 ...etc. 

    slave_1 = rs485_gui_slave(window = root_window, slave_number = 2, modbus_interface = mi, slaves_mcfg = slaves_mcfg, color = "white")
    slave_1.gen_slave_modbus_gui()
    slave_1.canvas.grid(row = 0, column = 1, sticky = "nw",  columnspan = 1)        
    slave_1.vbar.grid(row = 0, column = 2, sticky = "ns", columnspan = 1, rowspan = 1) 

    root_window.mainloop()       # Blocking function.   

