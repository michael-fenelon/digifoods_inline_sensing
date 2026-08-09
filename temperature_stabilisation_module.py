# import all components from the tkinter library
from tkinter import *
import tkinter as tk
from tkinter import ttk
import copy
import time 
from slaves_modbus_configuration import*
from pymodbus.client import ModbusSerialClient
from modbus_interface import Modbus_Interface
from watchpoints import watch
from rs485_gui_slave import*

# Alias tsm = = Temperature_stabilisation_module
class Temperature_stabilisation_module():
    def __init__(self, window  = None, rs485_gui_slave = None, pumps_slave = None):
        self.window = window    # root window from main.py
        self.rs485_gui_slave = rs485_gui_slave     
        self.pumps_slave = pumps_slave
        self.color = "#d9d9d9"    # Deafult gray color of a widget print("Default color = ", self.gui_dict['Check_dict']['enable_tsm'].cget("bg"))              
        self.row_counter = 0
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Scale_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Radio_dict':{}, 'Progress_bar':{}, 'Scale_dict':{} }           
        self.gen_gui()

    def gen_gui(self):
        self.canvas_height = 800
        self.canvas_width = 800 
        self.canvas = tk.Canvas(self.window, bg = "white", height = self.canvas_height, width = self.canvas_width, background = "#d9d9d9",  highlightthickness = 5)  
        self.frame = tk.Frame(self.canvas, width = self.canvas_width-10, height = self.canvas_height-10, background = self.color)        
        self.canvas.create_window( 5, 5, window = self.frame, anchor = tk.NW )         

        width = 40    
        self.gui_dict['Check_dict']['enable_tsm_IntVar'] = IntVar()
        self.gui_dict['Check_dict']['enable_tsm'] = Checkbutton(self.frame, 
                                                                            text = "RUN: Temperature stabilisation module",
                                                                            variable = self.gui_dict['Check_dict']['enable_tsm_IntVar'],
                                                                            onvalue = True,
                                                                            offvalue = False,
                                                                            height = 1, 
                                                                            width = width,
                                                                            command = self.tsm_enable)
                                                                         
        self.gui_dict['Radio_dict']['auto_debug_IntVar'] = StringVar(value = "auto")
        self.gui_dict['Radio_dict']['auto'] = tk.Radiobutton(self.frame, text = "Auto ", variable = self.gui_dict['Radio_dict']['auto_debug_IntVar'], value = "auto", height = 1, width = width)
        self.gui_dict['Radio_dict']['debug'] = tk.Radiobutton(self.frame, text = "Debug", variable = self.gui_dict['Radio_dict']['auto_debug_IntVar'], value = "debug", height = 1, width = width)                                                                           
        self.gui_dict['Button_dict']['tsm_start'] = Button(self.frame, text = "Start", command = self.tsm_start, height = 1, width = width)   

        # 6 temperature sensors, 
        for num_temp_sensor in range(1,7):
            self.gui_dict['Label_dict']['temperature_' + str(num_temp_sensor)] = Label(self.frame, text = 'Temperature ' + str(num_temp_sensor) + ' (deg C)')
            self.gui_dict['Label_dict']['temperature_' + str(num_temp_sensor) + '_value'] = Label(self.frame, text = "---")

        # 6 three way valves, sliders for specific positions. 
        for num_servo_valve in range(1,7):
            self.gui_dict['Label_dict']['servo_valve_' + str(num_servo_valve)] = Label(self.frame, text = 'Valve ' + str(num_servo_valve) + ' position ' )
            # self.gui_dict['Label_dict']['servo_valve_' + str(num_servo_valve) + '_value'] = Label(self.frame, text = '---' )  # redundant          
            self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) + '_IntVar'] = IntVar(value = 1)
            self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) ] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) + '_IntVar'],
                                                                    from_ = 1, to = 2, resolution = 1,
                                                                    orient = HORIZONTAL, length = 100, border = 1, width = 20)            
        
        # vnh5019 slave with slider to control speed.
        for num_pump in range(1,3):
            self.gui_dict['Label_dict']['pump_' + str(num_pump)] = Label(self.frame, text = 'Set Pump ' + str(num_pump) + ' RPM')
            self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) + '_IntVar'] = IntVar(value = 1)
            self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) ] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) + '_IntVar'],
                                                                    from_ = 1, to = 100, resolution = 1,
                                                                    orient = HORIZONTAL, length = 350, border = 1, width = 20)               
       
        # relays ?

        
        
        # Place all the widgets on the self.frame.
        self.canvas.grid(row = 0, column = 0, sticky = "nw", padx = 5, pady = 50)
        self.gui_dict['Check_dict']['enable_tsm'].grid(row = 0, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Radio_dict']['auto'].grid(row = 1, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Radio_dict']['debug'].grid(row = 2, column = 0, sticky = "nw", pady = 2, columnspan = 1)
        self.gui_dict['Button_dict']['tsm_start'].grid(row = 3, column = 0, sticky = "nw", pady = 2, columnspan = 1)

        self.row_counter = 4

        # loop and place all temperature sensors.
        for num_temp_sensor in range(1,7):
            self.gui_dict['Label_dict']['temperature_' + str(num_temp_sensor)].grid(row = self.row_counter + num_temp_sensor, column = 0, sticky = "e", pady = 2, columnspan = 1)
            self.gui_dict['Label_dict']['temperature_' + str(num_temp_sensor) + '_value'].grid(row = self.row_counter + num_temp_sensor, column = 1, sticky = "nw", pady = 2, columnspan = 1)

        self.row_counter = 4 + num_temp_sensor

        # loop and place all servo valves.
        for num_servo_valve in range(1,7):
            self.gui_dict['Label_dict']['servo_valve_' + str(num_servo_valve)].grid(row = self.row_counter + num_servo_valve, column = 0, sticky = "e", pady = 2, columnspan = 1)
            # self.gui_dict['Label_dict']['servo_valve_' + str(num_servo_valve) + '_value'].grid(row = self.row_counter + num_servo_valve, column = 0, sticky = "e", pady = 2, columnspan = 1)
            self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) ].grid(row = self.row_counter + num_servo_valve, column = 1, sticky = "nw", pady = 2, columnspan = 1)

        self.row_counter = 4 + num_temp_sensor + num_servo_valve

        for num_pump in range(1,3):
            self.row_counter = self.row_counter + 1
            self.gui_dict['Label_dict']['pump_' + str(num_pump)].grid(row = self.row_counter + num_pump, column = 0, sticky = "e", pady = 2, columnspan = 1)
            self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) ].grid(row = self.row_counter + num_pump, column = 1, sticky = "e", pady = 2, columnspan = 1)

        # Update button: Large vertical button used and command/callback to read all the holding register entries, update the holding_reg_list and send value to the slave.
        # We use a button so that only ONE slave uses the RS485 line at a time; avoids RS485 communication conflicts between slaves.
        self.gui_dict['Button_dict']['update'] = Button(self.frame, text = "update", command = self.update, wraplength = 50) 
        self.gui_dict['Button_dict']['update'].grid(row = 4, column = 3, sticky = "nse", pady = 2, columnspan = 1, rowspan = self.row_counter)

    # Possible functions.
    # withdraw sample
    # recirculate sample
    # infuse sample into flowcell    
    
    # withdraw water
    # recirculate water.
    # infuse water into flow cell.

    def process_sample(self, action = None):
        #action = "withdraw" or "recirculate" 
        # We set the slider positions in the gui and call self.tsm_set_valve_positions()
        if action == "withdraw":
            self.gui_dict['Scale_dict']['set_servo_valve_1_IntVar'].set(1) 
            self.gui_dict['Scale_dict']['set_servo_valve_2_IntVar'].set(1) 
        elif action == "recirculate":
            self.gui_dict['Scale_dict']['set_servo_valve_1_IntVar'].set(2) 
            self.gui_dict['Scale_dict']['set_servo_valve_2_IntVar'].set(2)             

        self.tsm_set_valve_positions()


    def tsm_enable(self):
        print("In tsm_enable(): ...")        

    def tsm_start(self):
        print("In tsm_start(): ...")       

    # Function doesn't exist in Arduino slave
    # def tsm_get_valve_positions(self):
    #     self.rs485_gui_slave.coil_list[2] = 1
    #     self.rs485_gui_slave.update_slave_via_reg_list()
    #     self.rs485_gui_slave.update_gui()    
        
    def tsm_set_valve_positions(self):   
        for num_servo_valve in range(1,7):
            value = self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) + '_IntVar'].get()    # Get value from slider for respective valve.
            # print("In tsm_set_valve_positions ", value, type(value))

            # When the value = 1, we need the servo to be at ~900microseconds. 
            # When the value = 2, we need the servo to be at ~1900microseconds. 
            # Since each servo is different, the servo horn will not align to the ON/OFF of a valve. 
            # Thus we have a min and max value at which the servo horn visually aligns with ON/OFF positions of the valve.
            # These positions are store in XLSX file for each servo and is also in the holding_reg_min_list and holding_reg_max_list. 
            if value == 1:
                self.rs485_gui_slave.holding_reg_list[num_servo_valve] = copy.deepcopy(int(self.rs485_gui_slave.holding_reg_min_list[num_servo_valve])) # assign ~900 from the min list to command a servo.
            elif value == 2:
                self.rs485_gui_slave.holding_reg_list[num_servo_valve] = copy.deepcopy(int(self.rs485_gui_slave.holding_reg_max_list[num_servo_valve])) # assign ~1900 from the max list to command a servo.          
            else:
                raise ValueError("In tsm_set_valve_positions(): INVALID slider and servo microseconds value.")

        self.rs485_gui_slave.coils_list[3] = 1
        self.rs485_gui_slave.update_slave_via_reg_list()
        self.rs485_gui_slave.update_gui()

    # Generic function to withdraw a fluid, eith sample or water from 
    def get_fuild(self, type = None):
        pass 

        # Set valve A to flow cell and valve B
        # self.rs485_gui_slave.holding_reg_list[] = 

    # Function that runs when the update button is pressed.
    # It gets the values from the gui and send it to two slaves.
    def update(self):       
        self.rs485_gui_slave.holding_reg_list[9] = copy.deepcopy(self.gui_dict['Scale_dict']['set_pump_1_IntVar'].get())
        self.rs485_gui_slave.holding_reg_list[10] = copy.deepcopy(self.gui_dict['Scale_dict']['set_pump_2_IntVar'].get())
        # print("In update(): Setting pump 1 to ", self.rs485_gui_slave.holding_reg_list[9] )
        # print("In update(): Setting pump 2 to ", self.rs485_gui_slave.holding_reg_list[10])

        self.pumps_slave.holding_reg_list[0] = self.rs485_gui_slave.holding_reg_list[9]     # Set motor rpm for pump 1
        self.pumps_slave.holding_reg_list[1] = self.rs485_gui_slave.holding_reg_list[10]    # Set motor rpm for pump 2

        self.pumps_slave.update_slave_via_reg_list()
        # print("slave number ", self.pumps_slave.slave_number)
        # print("slave_address ", self.pumps_slave.slave_address)

        self.tsm_set_valve_positions()
        
def root_window_bind_callback():
    print("In root_window_bind_callback():  ...")
    
def on_closing():
    print("destroying main window.")
    root_window.destroy()       # main
    exit()     

if __name__ == "__main__":
    # Create the root window
    root_window = Tk()   
    root_window.title('Temperature stabilisation module')       # Set window title    
    window_width = 1600
    window_height = 1000
    root_window.geometry(str(window_width) + "x" + str(window_height))     # Set window size width x height   1600x1000
    # root_window.geometry("1600x1000")     # Set window size width x height   
    root_window.config(background = "white")     #Set window background color  
    root_window.columnconfigure( 0, weight = 1 ) # Stretch Column 0 to fit width.
    root_window.rowconfigure( 0, weight = 1 ) # Stretch row 0 to fit height. 
    root_window.resizable(width = False, height = False)         # This makes the GUI of fixed size and prevents resizing.
    root_window.bind('<Return>', root_window_bind_callback )            # This gets the values entered in the gui.
    root_window.lift()       # Bring window forwards
    # root_window.attributes('-topmost', True)
    root_window.protocol("WM_DELETE_WINDOW", on_closing)   

    slaves_mcfg = Slaves_Modbus_Config()       # Get configurations of all slaves (read xlsx file)
    slaves_mcfg.get_config()
    mi = Modbus_Interface()     # Create a RS485 Modbus RTU interface with baud rate, 8N1 ...etc. 

    tsm = Temperature_stabilisation_module(window = root_window)    
    tsm.canvas.grid(row = 0, column = 0)

    root_window.mainloop()       # Blocking function.   
