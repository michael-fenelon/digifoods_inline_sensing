# import all components from the tkinter library
from tkinter import *
import tkinter as tk
from tkinter import ttk
import copy
import time 

from pymodbus.client import ModbusSerialClient
from watchpoints import watch
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import datetime as dt

from slaves_modbus_configuration import*
from modbus_interface import Modbus_Interface
from rs485_gui_slave import*
from element import*
from valve import*
from pump import*
from temp_sensor import*
from process import*

# Possible functions. 
# withdraw / recirculate. 
# air / fluid 
# sample / water 

# Alias tsm = = Temperature_stabilisation_module
class Temperature_stabilisation_module():
    def __init__(self, window  = None, 
                    ardu_mega_slave = None,
                    pumps_slave = None,
                    canvas_height = 1000,
                    canvas_width = 800,
                    color = "#d9d9d9",
                    plots = None ):

        self.window = window    # root window from main.py
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.color = color # "#d9d9d9"    # Default gray color of a widget print("Default color = ", self.gui_dict['Check_dict']['enable_tsm'].cget("bg"))              

        self.ardu_mega_slave = ardu_mega_slave     
        self.pumps_slave = pumps_slave

        self.gui_dict =  {}     # A dictionary to hold all the widgets.
        self.canvas_main = tk.Canvas(self.window, bg=self.color, height = self.canvas_height, width = self.canvas_width, highlightthickness = 5)  # Main canvas to place all valves, pumps, elements...etc.
        self.frame = tk.Frame(self.canvas_main, width = self.canvas_width + 5, height = self.canvas_height + 5, background= self.color)        
        self.canvas_main.create_window( 5, 5, window = self.frame, anchor=tk.NW )   
        
        self.plots = plots      # Since plots will need a different section on the GUI, the canvas needs to be from main.py. In main.py we place the plots. 
        # self.color = "#d9d9d9"    # Default gray color of a widget print("Default color = ", self.gui_dict['Check_dict']['enable_tsm'].cget("bg"))              
        # self.row_counter = 0

        self.time_start = 0
        self.time_now = 0
        self.target_sample_temp = 30
        self.withdraw_timeout = 30   # Maximum time for whitdrawal, in seconds.
        self.rec_timeout = 60*5       # Maximum time for recirculation, in seconds

        self.time_now_water = 0
        self.time_start_water = 0
        self.target_water_temp = 30
        self.water_withdraw_timeout = 30    # Maximum time for whitdrawal, in seconds.
        self.water_rec_timeout = 60*5        # Maximum time for recirculation, in seconds

        self.withdrawal_point_T_list = []
        self.rec_point_T_list = []
        self.cutoff_point_T_list = []
        self.sample_temp_diff_list = []

        self.time_temperature_list = []     # X axis
        self.wait_counter = 0
        self.temp_diff_tol = 1.0
        # self.sample_color = "#d9d9d9"
        # self.water_color = "#d9d9d9"
        self.sample_color = "light goldenrod"
        self.water_color = "light sky blue"
        # self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Scale_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Radio_dict':{}, 'Progress_bar':{}, 'Scale_dict':{} }           
        self.gen_gui()

        self.fig, (self.ax1) = plt.subplots(1, 1, figsize=(8, 4))
        self.draw_canvas = FigureCanvasTkAgg(self.fig, master = self.plots.canvas)  
        self.draw_canvas.get_tk_widget().grid(row=0, column=0, sticky="w")                
        self.ax1.set_title('Sample or Water')
        self.ax1.set_xlabel('Time(s)')
        self.ax1.set_ylabel('T (degC)')    
        self.ax1.legend(loc="upper right")             
        self.ax1.set_ylim(15, 50)
        self.ax1.grid() 

        self.get_temperatures()

        # try:
        #     self.get_temperatures()
        # except:
        #     print("Slave TSM not connected to RS485")
          
    # Method to create a 2D grid on the canvas with spacing.           
    def create_grid(self):
        pass
        # for x in range(0,self.canvas_width, 100):
        #     self.canvas_main.create_line(0,x,self.canvas_height,x, tags="grid_line")
            # self.canvas_main.create_line([(0,x),(self.canvas_height,x)], tags="grid_line")

    # Position all elements, pumps, valves...etc on canvas_main.
    # x axis points right, y axis points downwards.
    # Stuff is arranged w.r.t increasing y axis. 
    def gen_gui(self):
        self.t_sensor_room = T_sensor(name="T1: Room", window=self.window, fg_color="firebrick1", canvas_height = 50, canvas_width = 150, x=200, y = 50)
        self.t_sensor_room.gen_gui()

        self.heat_pump = Element(name="Heat Pump", window=self.window, canvas_width = 200, bg_color = "gray34",  x = 400, y= 10)        
        self.heat_pump.gen_gui()

        self.pump = Pump(name="Pump 1", window=self.window, canvas_height = 100, canvas_width = 200, x = 200, y= 150,
                            holding_reg_num = 0, coil_num = 0, ardu_uno_slave = self.pumps_slave)        
        self.pump.gen_gui()
        self.pump.set_rpm(25)

        self.valve_A = Valve(name="Valve A", window=self.window, canvas_height = 100, canvas_width = 200, x=600, y=300,
                            holding_reg_num = 1, coil_num = 3, ardu_mega_slave = self.ardu_mega_slave) 
        self.valve_A.gen_gui()   

        self.t_sensor_rec = T_sensor(name="T2: At recirculation", window=self.window, fg_color="firebrick1", canvas_height = 100, canvas_width = 150, x=430, y = 310)
        self.t_sensor_rec.gen_gui()   
        
        self.valve_B = Valve(name="Valve B", window=self.window, canvas_height = 100, canvas_width = 200, x=200, y=300,
                            holding_reg_num=2, coil_num=3, ardu_mega_slave = self.ardu_mega_slave)  
        self.valve_B.gen_gui()  

        self.t_sensor_after_radiator = T_sensor(name="T3: After Radiator", window=self.window, fg_color="firebrick1", canvas_height = 50, canvas_width = 200, x=200, y = 425)
        self.t_sensor_after_radiator.gen_gui()

        self.radiator = Element(name="Radiator", window=self.window, canvas_height = 60, canvas_width = 100, bg_color = "orange",  x = 200, y= 500)        
        self.radiator.gen_gui()

        self.t_sensor_before_radiator = T_sensor(name="T4: Before Radiator", window=self.window, fg_color="firebrick1", canvas_height = 50, canvas_width = 200, x=200, y = 600)
        self.t_sensor_before_radiator.gen_gui()

        self.valve_air_fluid = Valve(name="Valve Air/Fluid", canvas_height = 100, canvas_width = 200, window=self.window, x=200, y=700,
                                    holding_reg_num=1, coil_num=3, ardu_mega_slave = self.ardu_mega_slave)   
        self.valve_air_fluid.gen_gui()               

        
        self.valve_sample_water = Valve(name="Valve Sample/Water", canvas_height = 100, canvas_width = 200, window=self.window, x=200, y=850,
                                    holding_reg_num=1, coil_num=3, ardu_mega_slave = self.ardu_mega_slave)   
        self.valve_sample_water.gen_gui()
        
        self.flow_cell = Element(name="Flow Cell", window=self.window, canvas_height = 120,canvas_width = 200, bg_color = "pale green",  x = 600, y= 500)        
        self.flow_cell.gen_gui()

        self.process = Process(name="Flow Cell", window=self.window, canvas_height = 250,canvas_width = 350, bg_color = "#d9d9d9",  x = 450, y= 650, callback = self.tsm_run)        
        self.process.gen_gui()       

    def get_temperatures(self):
        self.ardu_mega_slave.coils_list[4] = 1
        self.ardu_mega_slave.update_slave_via_reg_list()
        self.ardu_mega_slave.update_gui()

        self.t_sensor_room.update_temp(self.ardu_mega_slave.input_reg_list[7])
        self.t_sensor_rec.update_temp(self.ardu_mega_slave.input_reg_list[8])
        self.t_sensor_after_radiator.update_temp(self.ardu_mega_slave.input_reg_list[9])
        self.t_sensor_before_radiator.update_temp(self.ardu_mega_slave.input_reg_list[10])

    def tsm_run(self):
        print("IN TSM !")
        if self.process.enable_process == True:
            pass

            if self.process.sample_or_water == "sample":                
                self.valve_sample_water.set_valve_pos(1)
            elif self.process.sample_or_water == "water":                
                self.valve_sample_water.set_valve_pos(2)
            else:
                raise ValueError ("In tsm(): Invalid value for sample or water valve")

            if self.process.fluid_or_air == "fluid":
                self.valve_air_fluid.set_valve_pos(1)                
            elif self.process.fluid_or_air == "air":
                self.valve_air_fluid.set_valve_pos(2)
            else:
                raise ValueError("In tsm(): Invalid value for fluid or air valve")

            if self.process.action == "withdraw":
                self.withdraw_timeout = self.process.gui_dict['scale_timer_IntVar'].get()    # Get slider value
                self.valve_A.set_valve_pos(1)       
                self.valve_B.set_valve_pos(1)
                self.pump.set_rpm( self.pump.gui_dict['rpm_status_IntVar'].get() )                  # Pump's rpm from slider.                
                self.time_start = copy.deepcopy(time.time())      # Start a timer            
                self.update()  
                self.tsm_clear_plots()          
                self.while_withdraw()    # We need to move the while True loop to a recursive function such that TK GUI's widgets are active.
            elif self.process.action == "recirculate":     
                self.rec_timeout = gui_dict['scale_timer_IntVar'].get()
                self.valve_A.set_valve_pos(2)
                self.valve_B.set_valve_pos(2)                                  
                self.time_start = copy.deepcopy(time.time())      # Start a timer
                self.sample_temp_diff_list = []     # reset the list to monitor temp_diff
                self.tsm_clear_plots()
                self.while_recirculate()    
            # elif self.process.action == "infuse" :
            #     pass
            else:
                raise ValueError("In tsm(): Invalid action value.")

        elif self.process.enable_process == False:
            pass
      
    # Recursive function to simulate a While True loop while widgets are active. 
    def while_withdraw(self):              
        self.time_now = copy.deepcopy(time.time())      # Curent time

        # If the user unchecks the button or the timer runs out we stop the motor and return.
        if (self.process.enable_process == False) or self.withdraw_timeout < (self.time_now - self.time_start):  
            self.process.set_time( str(round(self.time_now - self.time_start,2)) )
            self.pump.set_rpm(0)                 
            self.update()
            self.set_to_normal()
            print("In while_withdraw(): User aborted process or timeout")
            return
        else:
            self.process.set_time( str(round(self.time_now - self.time_start,2)) )            
            self.tsm_plot_sample_rec_temp()

        self.window.after(100,self.while_withdraw)

    # Recursive function to monitor the temperature and keep the pump running until the temperature is achieved or timeout or the user stops recicrulation.
    def while_recirculate(self):
        # The target is the room temperature.
        self.target_sample_temp = self.t_sensor_room.temperature
        self.time_now = copy.deepcopy(time.time())      # Curent time

        # If the user unchecks the button or the 30 timer runs out we stop the motor and return.
        if (self.process.enable_process == False) or self.rec_timeout < (self.time_now - self.time_start):  
            self.process.set_time(round(self.time_now - self.time_start,2))   
            self.pump.set_rpm(0)               
            self.update()            
            print("In while_recirculate(): User aborted process or timeout")           
            return
        else:  
            self.process.set_time(round(self.time_now - self.time_start,2))               
            self.gui_dict['Label_dict']['process_sample_timeout'].config(text = str(self.rec_timeout) + 's Timer @ ' + str(round(self.time_now - self.time_start,2)))                                  
            self.update()      # This will automatically update the temperatures. 
            self.tsm_plot_sample_rec_temp()
            
            # If temperature difference between target and current is less than 3 degC we exit , else we wait until timeout or the user aborts
            temp_diff = round(abs(self.ardu_mega_slave.input_reg_list[10]- self.target_sample_temp),2)
            
            # Take the avg of the time_diff
            self.sample_temp_diff_list.append(temp_diff)
            self.sample_temp_diff_list = self.sample_temp_diff_list[-10:]   # Keep only latest 10 elements of the list.
            avg = np.mean(self.sample_temp_diff_list)                       # use the average of samples to decide if the temperature is stabilised.
            if (avg <= self.temp_diff_tol):                
                print("In while_recirculate(), Sample temperature is stabilised ", temp_diff)
                self.pump.set_rpm(0)                
                self.update()                       
                return            
            else:                
                print("while_recirculate(): Waiting for temperature to stabilise")
                print("Target temp = ", round(self.target_sample_temp,2))
                print("Current temp = ", round(self.ardu_mega_slave.input_reg_list[8],2))

        self.window.after(100,self.while_recirculate)

    # def tsm_infusion_to_flow_cell(self):
    #     if self.gui_dict['Check_dict']['infuse_sample_or_water_IntVar'].get() == True:
    #         print("In tsm_infusion_to_flow_cell(): START")

    #         # Disable the infuse sample / water RadioButton until user aborts or timeout.
    #         self.gui_dict['Radio_dict']['infuse_sample'].config(state = 'disabled')
    #         self.gui_dict['Radio_dict']['infuse_water'].config(state = 'disabled')
    #         self.gui_dict['Check_dict']['process_sample'].config(state = 'disabled')
    #         self.gui_dict['Check_dict']['process_water'].config(state = 'disabled')
            
    #         # When we want to infuse the sample to the flow cell, 
    #         # We can set the sample section to "withdraw" and set the Process Sample check box to True.            
    #         if self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'].get() == "sample":
    #             self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'].set("withdraw") 
    #             self.gui_dict['Check_dict']['process_sample_IntVar'].set(1)     # Setting a value of 1 in a checkbox != actually clicking the checkbox.
    #             self.gui_dict['Check_dict']['process_water_IntVar'].set(0)      # Setting a value of 1 in a checkbox != actually clicking the checkbox.
    #             self.tsm_process_sample()              
            
    #         # When we want to infuse the water to the flow cell, 
    #         # We can set the water section to "withdraw" and set the Process water check box to True.            
    #         elif self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'].get() == "water":
    #             self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'].set("withdraw") 
    #             self.gui_dict['Check_dict']['process_sample_IntVar'].set(0)     # Setting a value of 1 in a checkbox != actually clicking the checkbox.
    #             self.gui_dict['Check_dict']['process_water_IntVar'].set(1)      # Setting a value of 1 in a checkbox != actually clicking the checkbox.
    #             self.tsm_process_water()               
    #     else:
    #         print("In tsm_infusion_to_flow_cell(): STOP")     
    #         self.gui_dict['Scale_dict']['set_pump_1_IntVar'].set(value = 1)    # Set pump 1 RPM to OFF  
    #         self.gui_dict['Scale_dict']['set_pump_2_IntVar'].set(value = 1)    # Set pump 2 RPM to OFF  
    #         self.update()    
    #         self.gui_dict['Check_dict']['process_sample_IntVar'].set(0)     # Setting a value of 1 in a checkbox != actually clicking the checkbox.
    #         self.gui_dict['Check_dict']['process_water_IntVar'].set(0)      # Setting a value of 1 in a checkbox != actually clicking the checkbox.            
    #         self.set_to_normal()

    def tsm_plot_sample_rec_temp(self):        
        # Get data.
        time = dt.datetime.now().minute + (dt.datetime.now().second/100)
        self.time_temperature_list.append(time)
        # self.time_temperature_list.append(dt.datetime.now().strftime('%H:%M:%S.%f'))

        self.withdrawal_point_T_list.append(self.ardu_mega_slave.input_reg_list[7])
        self.rec_point_T_list.append(self.ardu_mega_slave.input_reg_list[8])
        self.cutoff_point_T_list.append(self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_DoubleVar'].get())        
        
        # limit the axis
        self.time_temperature_list = self.time_temperature_list[-20:]

        self.withdrawal_point_T_list = self.withdrawal_point_T_list[-20:]
        self.rec_point_T_list = self.rec_point_T_list[-20:]
        self.cutoff_point_T_list = self.cutoff_point_T_list[-20:]

        # plotting the graph
        self.ax1.plot(self.time_temperature_list, self.withdrawal_point_T_list,'b')
        self.ax1.plot(self.time_temperature_list, self.rec_point_T_list,'g')
        self.ax1.plot(self.time_temperature_list, self.cutoff_point_T_list,'r')
        self.ax1.legend(['withdrawal','recirculation','cutoff'])   

        self.draw_canvas.draw()            

    def tsm_clear_plots(self):
        self.ax1.clear()
        self.ax2.clear()  
        self.ax1.grid()
        self.ax2.grid()           
      
    # Function that runs when the update button is pressed.
    # It gets the values from the gui and send it to two slaves, 1 - TSM, 2 - The peristatic pumps.
    def update(self):   
        self.pumps_slave.update_slave_via_reg_list()    # update the pumps slave.
        # self.pumps_slave.update_gui()       # there's no GUI for the slave. 

        # For Ardu-mega's valves
        self.ardu_mega_slave.coils_list[3] = 1
        self.ardu_mega_slave.update_slave_via_reg_list()
        self.ardu_mega_slave.update_gui()
        self.window.update()

        self.get_temperatures()

        self.tsm_plot_sample_rec_temp()
        
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
    root_window.geometry(str(window_width) + "x" + str(window_height))     # Set window size width x height 1600x1000, Eg: root_window.geometry("1600x1000")     
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
    slave_2 = ardu_mega_slave(window = root_window,
                                slave_number = 2,
                                modbus_interface = mi,
                                slaves_mcfg = slaves_mcfg,
                                color="white", 
                                canvas_height=500, 
                                canvas_width=850)

    pumps_slave = ardu_mega_slave(window = root_window, slave_number = 1, modbus_interface = mi, slaves_mcfg = slaves_mcfg, color="white")
    pumps_slave.gen_slave_modbus_gui() 
    #pumps_slave.gen_slave_modbus_gui() # No need to display the gui for pumps.      

    plots = Element()
    tsm = Temperature_stabilisation_module(window = root_window, plots=plots, color = "white")    
    tsm.canvas_main.place(x=0, y = 0)    
    # tsm.canvas_main.grid(row = 0, column = 0)

    plots.canvas.place(x=500,y=600)

    root_window.mainloop()       # Blocking function.   
