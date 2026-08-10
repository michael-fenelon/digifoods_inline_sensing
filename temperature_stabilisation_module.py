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

    # Possible functions.
    # Get temperatures. 
    # withdraw sample
    # recirculate sample
    # infuse sample into flowcell        
    # withdraw water
    # recirculate water.
    # infuse water into flow cell.

class Temperature_stabilisation_module():
    def __init__(self, window  = None, rs485_gui_slave = None, pumps_slave = None):
        self.window = window    # root window from main.py
        self.rs485_gui_slave = rs485_gui_slave     
        self.pumps_slave = pumps_slave
        self.color = "#d9d9d9"    # Deafult gray color of a widget print("Default color = ", self.gui_dict['Check_dict']['enable_tsm'].cget("bg"))              
        self.row_counter = 0
        self.process_sample_stop_flag = False
        self.process_water_stop_flag = False
        self.infusion_stop_flag = False

        self.sample_color = "light goldenrod"
        self.water_color = "light sky blue"
        self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Scale_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Radio_dict':{}, 'Progress_bar':{}, 'Scale_dict':{} }           
        self.gen_gui()
        try:
            self.get_temperatures()
        except:
            print("Slave TSM not connected to RS485")
          
    def gen_gui(self):
        self.canvas_height = 1000
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
            # We need specific labels for the valves.
            # Valve 1 and 2 for sample
            # Valve 3 and 4 for water
            # Valve 5 to choose between sample or water to flow cell.
            # Similarily we add color to respective slider to show that they are a set. 
            if num_servo_valve == 1:
                label = " Sample valve 1 position "
                troughcolor = self.sample_color
            elif num_servo_valve == 2:
                label = " Sample valve 2 position "
                troughcolor = self.sample_color
            elif num_servo_valve == 3:
                label = " Water valve 1 position "
                troughcolor = self.water_color
            elif num_servo_valve == 4:
                label = " Water valve 2 position "
                troughcolor = self.water_color
            elif num_servo_valve == 5:
                label = " Sample/Water to Flowcell, 1: Sample, 2: Water "
                troughcolor = "lightgreen"
            elif num_servo_valve == 6:
                label = " NA "         
                troughcolor="white"       

            self.gui_dict['Label_dict']['servo_valve_' + str(num_servo_valve)] = Label(self.frame, text = label)    
            #self.gui_dict['Label_dict']['servo_valve_' + str(num_servo_valve)] = Label(self.frame, text = 'Valve ' + str(num_servo_valve) + ' position ' )
            # self.gui_dict['Label_dict']['servo_valve_' + str(num_servo_valve) + '_value'] = Label(self.frame, text = '---' )  # redundant          
            self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) + '_IntVar'] = IntVar(value = 1)
            self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) ] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) + '_IntVar'],
                                                                    from_ = 1, to = 2, resolution = 1,
                                                                    orient = HORIZONTAL, length = 100, border = 1, width = 20, troughcolor = troughcolor)            
        
        # vnh5019 slave with slider to control speed.
        for num_pump in range(1,3):
            # Assign distinct colors for sample and water.
            if num_pump == 1:
                color = self.sample_color
            elif num_pump == 2:
                color = self.water_color
            else:
                color = "light green"

            self.gui_dict['Label_dict']['pump_' + str(num_pump)] = Label(self.frame, text = 'Set Pump ' + str(num_pump) + ' RPM')
            self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) + '_IntVar'] = IntVar(value = 100)
            self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) ] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) + '_IntVar'],
                                                                    from_ = 1, to = 100, resolution = 1, troughcolor = color,
                                                                    orient = HORIZONTAL, length = 350, border = 1, width = 20)               
       
        self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'] = StringVar(value = "withdraw")
        self.gui_dict['Radio_dict']['sample_withdraw'] = tk.Radiobutton(self.frame, text = "Sample withdraw ", variable = self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'], value = "withdraw", height = 1, width = width, bg = self.sample_color)
        self.gui_dict['Radio_dict']['sample_recirculate'] = tk.Radiobutton(self.frame, text = "Sample recirculate", variable = self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'], value = "recirculate", height = 1, width = width, bg = self.sample_color) 
        self.gui_dict['Button_dict']['process_sample'] = Button(self.frame, text = "Process Sample", command = self.tsm_process_sample, height = 1, width = width, bg = self.sample_color)   
        self.gui_dict['Button_dict']['process_sample_stop'] = Button(self.frame, text = " STOP ", command = self.tsm_process_sample_stop, height = 1, width = 10, bg = self.sample_color)   
        self.gui_dict['Label_dict']['sample_rec_temp_cutoff'] = Label(self.frame, text = 'Set sample recirculation cutoff temperature')
        self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_DoubleVar'] = DoubleVar(value = 25)
        self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_scale'] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_DoubleVar'] ,
                                                                from_ = 20, to = 40, resolution = 1, troughcolor = self.sample_color,
                                                                orient = HORIZONTAL, length = 350, border = 1, width = 20)
        self.gui_dict['Label_dict']['sample_rec_temp_cutoff_status'] = Label(self.frame, text = '---')                                                                

        self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'] = StringVar(value = "withdraw")
        self.gui_dict['Radio_dict']['water_withdraw'] = tk.Radiobutton(self.frame, text = "Water withdraw ", variable = self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'], value = "withdraw", height = 1, width = width, bg = self.water_color)
        self.gui_dict['Radio_dict']['water_recirculate'] = tk.Radiobutton(self.frame, text = "Water recirculate", variable = self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'], value = "recirculate", height = 1, width = width, bg = self.water_color) 
        self.gui_dict['Button_dict']['process_water'] = Button(self.frame, text = "Process Water", command = self.tsm_process_water, height = 1, width = width, bg = self.water_color)        
        self.gui_dict['Button_dict']['process_water_stop'] = Button(self.frame, text = " STOP ", command = self.tsm_process_water_stop, height = 1, width = 10, bg = self.water_color)        
        self.gui_dict['Label_dict']['water_rec_temp_cutoff'] = Label(self.frame, text = 'Set water recirculation cutoff temperature')
        self.gui_dict['Scale_dict']['water_rec_temp_cutoff_DoubleVar'] = DoubleVar(value = 25)
        self.gui_dict['Scale_dict']['water_rec_temp_cutoff_scale'] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['water_rec_temp_cutoff_DoubleVar'] ,
                                                                from_ = 20, to = 40, resolution = 1, troughcolor = self.water_color,
                                                                orient = HORIZONTAL, length = 350, border = 1, width = 20)
        self.gui_dict['Label_dict']['water_rec_temp_cutoff_status'] = Label(self.frame, text = '---')

        self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'] = StringVar(value = "sample")
        self.gui_dict['Radio_dict']['infuse_sample'] = tk.Radiobutton(self.frame, text = "Infuse Sample to Flow cell ", variable = self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'], value = "sample", height = 1, width = width, bg = "light green")
        self.gui_dict['Radio_dict']['infuse_water'] = tk.Radiobutton(self.frame, text = "Infuse Water to Flow cell", variable = self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'], value = "water", height = 1, width = width, bg = "light green") 
        self.gui_dict['Button_dict']['infuse'] = Button(self.frame, text = " Infusion to Flow Cell ", command = self.tsm_infusion_to_flow_cell, height = 1, width = width, bg = "light green")   
        self.gui_dict['Button_dict']['infuse_stop'] = Button(self.frame, text = " STOP ", command = self.tsm_infusion_to_flow_cell_stop, height = 1, width = 10, bg = "light green")   
        
        # Place all the widgets on the self.frame.
        self.canvas.grid(row = 0, column = 0, sticky = "nw", padx = 5, pady = 5)
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
        self.gui_dict['Button_dict']['update'].grid(row = 4, column = 2, sticky = "ns", pady = 2, columnspan = 1, rowspan = self.row_counter - 1)

        self.row_counter = self.row_counter + num_pump
        self.gui_dict['Radio_dict']['sample_withdraw'].grid(row = self.row_counter + 1, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Button_dict']['process_sample'].grid(row = self.row_counter + 1, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)
        self.gui_dict['Button_dict']['process_sample_stop'].grid(row = self.row_counter + 1, column = 2, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)        
        self.gui_dict['Radio_dict']['sample_recirculate'].grid(row = self.row_counter + 2, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Label_dict']['sample_rec_temp_cutoff'].grid(row = self.row_counter + 3, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_scale'].grid(row = self.row_counter + 3, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Label_dict']['sample_rec_temp_cutoff_status'].grid(row = self.row_counter + 3, column = 2, sticky = "w", pady = 2, columnspan = 1, rowspan = 1)
        
        self.gui_dict['Radio_dict']['water_withdraw'].grid(row = self.row_counter + 4, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Button_dict']['process_water'].grid(row = self.row_counter + 4, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)
        self.gui_dict['Button_dict']['process_water_stop'].grid(row = self.row_counter + 4, column = 2, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)        
        self.gui_dict['Radio_dict']['water_recirculate'].grid(row = self.row_counter + 5, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Label_dict']['water_rec_temp_cutoff'].grid(row = self.row_counter + 6, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Scale_dict']['water_rec_temp_cutoff_scale'].grid(row = self.row_counter + 6, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Label_dict']['water_rec_temp_cutoff_status'].grid(row = self.row_counter + 6, column = 2, sticky = "w", pady = 2, columnspan = 1, rowspan = 1)

        self.gui_dict['Radio_dict']['infuse_sample'].grid(row = self.row_counter + 7, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Radio_dict']['infuse_water'].grid(row = self.row_counter + 8, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Button_dict']['infuse'].grid(row = self.row_counter + 7, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)
        self.gui_dict['Button_dict']['infuse_stop'].grid(row = self.row_counter + 7, column = 2, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)

    def get_temperatures(self):
        self.rs485_gui_slave.coils_list[4] = 1
        self.rs485_gui_slave.update_slave_via_reg_list()
        self.rs485_gui_slave.update_gui()

        for num_temp_sensor in range(1,7):            
            self.gui_dict['Label_dict']['temperature_' + str(num_temp_sensor) + '_value'].config(text = str(self.rs485_gui_slave.input_reg_list[num_temp_sensor + 6]))

    def tsm_process_sample(self):       
        self.process_sample_stop_flag = False

        # Switch off the pump incase it was on

        action = self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'].get()     # "withdraw" or "recirculate" 
        # We set the slider positions in the gui and call self.tsm_set_valve_positions()
        if action == "withdraw":
            self.gui_dict['Scale_dict']['set_servo_valve_1_IntVar'].set(1) 
            self.gui_dict['Scale_dict']['set_servo_valve_2_IntVar'].set(1) 
            self.gui_dict['Scale_dict']['set_servo_valve_5_IntVar'].set(1)    # Set the 5th servo valve to flowcell. 
        elif action == "recirculate":
            self.gui_dict['Scale_dict']['set_servo_valve_1_IntVar'].set(2) 
            self.gui_dict['Scale_dict']['set_servo_valve_2_IntVar'].set(2)             
            self.gui_dict['Scale_dict']['set_servo_valve_5_IntVar'].set(2)    # Set the 5th servo valve to flowcell.         

        # Disable the user from changing the servo sliders until the process completes or by a timeout.
        # The slider can be "set" or "moved" from the code to a different value even when it is disabled.        
        # Even if the slider is disabled, the visuals don't seem to change and it still looks active.
        for num_servo_valve in range(1,7):
            self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) ].config(state = "disabled")
        # self.window.update()

        self.tsm_set_valve_positions()

        # Turn on pump 1 to
        if action == "withdraw":
            # Turn on the pump for ## seconds
            time_start = copy.deepcopy(time.time())      # Start a timer
            self.update()
            while True:
                time_now = copy.deepcopy(time.time())      # Start a timer                
                if self.process_sample_stop_flag == True or 10 < (time_now - time_start):  # If user pressed STOP or We wait for N seconds for sample withdrawal
                    self.gui_dict['Scale_dict']['set_pump_1_IntVar'].set(1) # Turn OFF pump
                    self.gui_dict['Scale_dict']['set_pump_2_IntVar'].set(1) # Turn OFF pump
                    self.update()
                    print("In tsm_process_sample(): User aborted process")
                    break
        # elif action == "recirculate":
        #     target_temp = self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_DoubleVar'].get()
        #     # Monitor the temperature and keep the pump running until the temperature is achieved or timeout or the user stops recicrulation.
        #     time_start = copy.deepcopy(time.time())      # Start a timer
        #     while True:
        #         time_now = copy.deepcopy(time.time())      # Start a timer

        #         self.get_temperatures()
        #         if temp == user's requirement':
        #             stop pump.
        #             wait a bit
        #             switch valves
        #             wait a bit
        #             switch on pump to infuse the stabilised sample to flow cell
         
    def tsm_process_sample_stop(self):        
        self.process_sample_stop_flag = True   
        print("In tsm_process_sample_stop(): process_sample_stop_flag ", self.process_sample_stop_flag)     

    def tsm_process_water(self):
        print("In tsm_process_water():...")        

    def tsm_process_water_stop(self):        
        self.process_water_stop_flag = True     
        print("In tsm_process_water_stop(): process_water_stop_flag ", self.process_water_stop_flag)   

    def tsm_infusion_to_flow_cell(self):
        pass

    def tsm_infusion_to_flow_cell_stop(self):
        self.infusion_stop_flag = True
        print("In tsm_infusion_to_flow_cell_stop(): infusion_stop_flag ", self.infusion_stop_flag)

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

    # Function that runs when the update button is pressed.
    # It gets the values from the gui and send it to two slaves, 1 - TSM, 2 - The peristatic pumps.
    def update(self):       
        self.rs485_gui_slave.holding_reg_list[9] = copy.deepcopy(self.gui_dict['Scale_dict']['set_pump_1_IntVar'].get())
        self.rs485_gui_slave.holding_reg_list[10] = copy.deepcopy(self.gui_dict['Scale_dict']['set_pump_2_IntVar'].get())
        # print("In update(): Setting pump 1 to ", self.rs485_gui_slave.holding_reg_list[9] )
        # print("In update(): Setting pump 2 to ", self.rs485_gui_slave.holding_reg_list[10])
        # print("Len ", len(self.pumps_slave.holding_reg_list))

        self.pumps_slave.holding_reg_list[0] = self.rs485_gui_slave.holding_reg_list[9]     # Set motor rpm for pump 1
        self.pumps_slave.holding_reg_list[1] = self.rs485_gui_slave.holding_reg_list[10]    # Set motor rpm for pump 2
        self.pumps_slave.update_slave_via_reg_list()    # update the pumps slave.
        # self.pumps_slave.update_gui()       # there's no GUI for the slave. 

        self.tsm_set_valve_positions()

        # self.get_temperatures()
        
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
