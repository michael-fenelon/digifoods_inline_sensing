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

'''
Revision 2: 

Version of code used without Class inheritance ...etc
The version was used for temperature equalisation module v2, see schematics.
Where in we had sample and water withdrawal, recirculation and a system of 5 valves.

'''

# Alias tsm = = Temperature_stabilisation_module
class Temperature_stabilisation_module():
    def __init__(self, window  = None, 
                    rs485_gui_slave = None,
                    pumps_slave = None,
                    canvas_height = 1000,
                    canvas_width = 800,
                    color = "#d9d9d9",
                    plots = None ):

        self.window = window    # root window from main.py
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.color = color # "#d9d9d9"    # Default gray color of a widget print("Default color = ", self.gui_dict['Check_dict']['enable_tsm'].cget("bg"))              

        self.rs485_gui_slave = rs485_gui_slave     
        self.pumps_slave = pumps_slave

        self.gui_dict =  {}     # A dictionary to hold all the widgets.
        self.canvas_main = tk.Canvas(self.window, bg=self.color, height = self.canvas_height, width = self.canvas_width, highlightthickness = 5)  # Main canvas to place all valves, pumps, elements...etc.
        self.frame = tk.Frame(self.canvas_main, width = self.canvas_width + 5, height = self.canvas_height + 5, background= self.color)        
        self.canvas_main.create_window( 5, 5, window = self.frame, anchor=tk.NW )   
        
        self.plots = plots      # Since plots will need a different section on the GUI, the canvas needs to be from main.py. In main.py we place the plots. 
        # self.color = "#d9d9d9"    # Default gray color of a widget print("Default color = ", self.gui_dict['Check_dict']['enable_tsm'].cget("bg"))              
        # self.row_counter = 0

        self.time_start_sample = 0
        self.time_now_sample = 0
        self.target_sample_temp = 30
        self.sample_withdraw_timeout = 30   # Maximum time for whitdrawal, in seconds.
        self.sample_rec_timeout = 60*5       # Maximum time for recirculation, in seconds

        self.time_now_water = 0
        self.time_start_water = 0
        self.target_water_temp = 30
        self.water_withdraw_timeout = 30    # Maximum time for whitdrawal, in seconds.
        self.water_rec_timeout = 60*5        # Maximum time for recirculation, in seconds

        self.sample_withdrawal_point_T_list = []
        self.sample_rec_point_T_list = []
        self.sample_cutoff_point_T_list = []
        self.sample_temp_diff_list = []
        
        self.water_withdrawal_point_T_list = []
        self.water_rec_point_T_list = []       
        self.water_cutoff_point_T_list = []    
        self.water_temp_diff_list = []

        self.time_temperature_list = []     # X axis
        self.wait_counter = 0
        self.temp_diff_tol = 1.0
        # self.sample_color = "#d9d9d9"
        # self.water_color = "#d9d9d9"
        self.sample_color = "light goldenrod"
        self.water_color = "light sky blue"
        # self.gui_dict =  {'Label_dict':{}, 'Text_dict':{}, 'Button_dict':{}, 'Scale_dict':{}, 'Check_dict':{}, 'Drop_down_dict':{}, 'Radio_dict':{}, 'Progress_bar':{}, 'Scale_dict':{} }           
        self.gen_gui()

        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(8, 4))
        self.draw_canvas = FigureCanvasTkAgg(self.fig, master = self.plots.canvas)  
        self.draw_canvas.get_tk_widget().grid(row=0, column=0, sticky="w")                
        self.ax1.set_title('Sample')
        self.ax1.set_xlabel('Time(s)')
        self.ax1.set_ylabel('T (degC)')    
        self.ax1.legend(loc="upper right")             
        self.ax1.set_ylim(15, 50)
        self.ax1.grid()

        self.ax2.set_title('Water')
        self.ax2.set_xlabel('Time(s)')
        self.ax2.set_ylabel('T (degC)')
        self.ax2.legend(loc="upper right")
        self.ax2.set_ylim(15, 50)
        self.ax2.grid()            

        self.gen_gui()

        # try:
        #     self.get_temperatures()
        # except:
        #     print("Slave TSM not connected to RS485")
          
    def gen_gui(self):
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
            # We need to specify the labels for specific temperatures. 
            # Temp 1: Sample temp at withdrawal point
            # Temp 2: Sample temp at recirculation point.
            # Temp 3: Water temp at withdrawal point
            # Temp 4: Water temp at recirculation point.
            if num_temp_sensor == 1:
                label = "Temp 1: Sample temp at withdrawal point"
            elif num_temp_sensor == 2:
                label = "Temp 2: Sample temp at recirculation point."
            elif num_temp_sensor == 3:
                label = "Temp 3: Water temp at withdrawal point"
            elif num_temp_sensor == 4:
                label = "Temp 4: Water temp at recirculation point."
            elif num_temp_sensor == 5:
                label = "NA"
            elif num_temp_sensor == 6:
                label = "NA"
            
            self.gui_dict['Label_dict']['temperature_' + str(num_temp_sensor)] = Label(self.frame, text = label)
            #self.gui_dict['Label_dict']['temperature_' + str(num_temp_sensor)] = Label(self.frame, text = 'Temperature ' + str(num_temp_sensor) + ' (deg C)')
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
            self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) + '_IntVar'] = IntVar(value = 10)
            self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) ] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['set_pump_' + str(num_pump) + '_IntVar'],
                                                                    from_ = 1, to = 100, resolution = 1, troughcolor = color,
                                                                    orient = HORIZONTAL, length = 350, border = 1, width = 20)               
       
        self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'] = StringVar(value = "withdraw")
        self.gui_dict['Radio_dict']['sample_withdraw'] = tk.Radiobutton(self.frame, text = "Sample withdraw ", variable = self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'], value = "withdraw", height = 1, width = width, bg = self.sample_color)
        self.gui_dict['Radio_dict']['sample_recirculate'] = tk.Radiobutton(self.frame, text = "Sample recirculate", variable = self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'], value = "recirculate", height = 1, width = width, bg = self.sample_color) 
        
        self.gui_dict['Check_dict']['process_sample_IntVar'] = IntVar()
        self.gui_dict['Check_dict']['process_sample'] = Checkbutton(self.frame, 
                                                                            text="Process Sample Start / Stop",
                                                                            variable=self.gui_dict['Check_dict']['process_sample_IntVar'],
                                                                            onvalue=True, 
                                                                            offvalue=False,
                                                                            height=1, 
                                                                            width = width,
                                                                            command=self.tsm_process_sample,
                                                                            bg = self.sample_color)
        self.gui_dict['Label_dict']['process_sample_timeout'] = Label(self.frame, text = 'Timer @ ', bg = self.sample_color)
        self.gui_dict['Label_dict']['process_sample_pump_1_current'] = Label(self.frame, text = 'Pump 1 current (mA)', bg = self.sample_color, wraplength=100)
                                                                    
        self.gui_dict['Label_dict']['sample_rec_temp_cutoff'] = Label(self.frame, text = 'Set sample recirculation cutoff temperature', bg = self.sample_color)
        self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_DoubleVar'] = DoubleVar(value = 25)
        self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_scale'] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_DoubleVar'] ,
                                                                from_ = 20, to = 40, resolution = 1, troughcolor = self.sample_color,
                                                                orient = HORIZONTAL, length = 350, border = 1, width = 20)
        self.gui_dict['Label_dict']['sample_rec_temp_cutoff_status'] = Label(self.frame, text = '---', bg = self.sample_color)                                                                

        self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'] = StringVar(value = "withdraw")
        self.gui_dict['Radio_dict']['water_withdraw'] = tk.Radiobutton(self.frame, text = "Water withdraw ", variable = self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'], value = "withdraw", height = 1, width = width, bg = self.water_color)
        self.gui_dict['Radio_dict']['water_recirculate'] = tk.Radiobutton(self.frame, text = "Water recirculate", variable = self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'], value = "recirculate", height = 1, width = width, bg = self.water_color) 
        
        self.gui_dict['Check_dict']['process_water_IntVar'] = IntVar()
        self.gui_dict['Check_dict']['process_water'] = Checkbutton(self.frame, 
                                                                            text="Process Water Start / Stop",
                                                                            variable=self.gui_dict['Check_dict']['process_water_IntVar'],
                                                                            onvalue=True,
                                                                            offvalue=False,
                                                                            height=1, 
                                                                            width = width,
                                                                            command=self.tsm_process_water,
                                                                            bg = self.water_color)
        self.gui_dict['Label_dict']['process_water_timeout'] = Label(self.frame, text = 'Timer @ ', bg = self.water_color)         
        self.gui_dict['Label_dict']['process_water_pump_2_current'] = Label(self.frame, text = 'Pump 2 current (mA)', bg = self.water_color, wraplength=100)
        
        self.gui_dict['Label_dict']['water_rec_temp_cutoff'] = Label(self.frame, text = 'Set water recirculation cutoff temperature', bg = self.water_color)
        self.gui_dict['Scale_dict']['water_rec_temp_cutoff_DoubleVar'] = DoubleVar(value = 25)
        self.gui_dict['Scale_dict']['water_rec_temp_cutoff_scale'] = Scale(self.frame, variable = self.gui_dict['Scale_dict']['water_rec_temp_cutoff_DoubleVar'] ,
                                                                from_ = 20, to = 40, resolution = 1, troughcolor = self.water_color,
                                                                orient = HORIZONTAL, length = 350, border = 1, width = 20)
        self.gui_dict['Label_dict']['water_rec_temp_cutoff_status'] = Label(self.frame, text = '---', bg = self.water_color)

        self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'] = StringVar(value = "sample")
        self.gui_dict['Radio_dict']['infuse_sample'] = tk.Radiobutton(self.frame, text = "Infuse Sample to Flow cell ", variable = self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'], value = "sample", height = 1, width = width, bg = "light green")
        self.gui_dict['Radio_dict']['infuse_water'] = tk.Radiobutton(self.frame, text = "Infuse Water to Flow cell", variable = self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'], value = "water", height = 1, width = width, bg = "light green") 
        self.gui_dict['Check_dict']['infuse_sample_or_water_IntVar'] = IntVar(value = False)
        self.gui_dict['Check_dict']['infuse_sample_or_water'] = Checkbutton(self.frame, 
                                                                            text="Infuse Sample / Water to Flow Cell.",
                                                                            variable=self.gui_dict['Check_dict']['infuse_sample_or_water_IntVar'],
                                                                            onvalue=True,
                                                                            offvalue=False,
                                                                            height=1, 
                                                                            width = width,
                                                                            command=self.tsm_infusion_to_flow_cell,
                                                                            bg = "light green")
        
        # self.gui_dict['Button_dict']['infuse'] = Button(self.frame, text = " Infusion to Flow Cell ", command = self.tsm_infusion_to_flow_cell, height = 1, width = width, bg = "light green")   
        # self.gui_dict['Button_dict']['infuse_stop'] = Button(self.frame, text = " STOP ", command = self.tsm_infusion_to_flow_cell_stop, height = 1, width = 10, bg = "light green")   
        
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
        self.gui_dict['Check_dict']['process_sample'].grid(row = self.row_counter + 1, column = 1, sticky = "w", pady = 2, columnspan = 1, rowspan = 1) 
        self.gui_dict['Label_dict']['process_sample_pump_1_current'].grid(row = self.row_counter + 1, column = 2, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)
        self.gui_dict['Label_dict']['process_sample_timeout'].grid(row = self.row_counter + 2, column = 1, sticky = "w", pady = 2, columnspan = 1, rowspan = 1) 
        self.gui_dict['Radio_dict']['sample_recirculate'].grid(row = self.row_counter + 2, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Label_dict']['sample_rec_temp_cutoff'].grid(row = self.row_counter + 3, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_scale'].grid(row = self.row_counter + 3, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Label_dict']['sample_rec_temp_cutoff_status'].grid(row = self.row_counter + 3, column = 2, sticky = "w", pady = 2, columnspan = 1, rowspan = 1)
        
        self.gui_dict['Radio_dict']['water_withdraw'].grid(row = self.row_counter + 4, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)        
        self.gui_dict['Check_dict']['process_water'].grid(row = self.row_counter + 4, column = 1, sticky = "w", pady = 2, columnspan = 1, rowspan = 1) 
        self.gui_dict['Label_dict']['process_water_pump_2_current'].grid(row = self.row_counter + 4, column = 2, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)
        self.gui_dict['Label_dict']['process_water_timeout'].grid(row = self.row_counter + 5, column = 1, sticky = "w", pady = 2, columnspan = 1, rowspan = 1) 
        
        self.gui_dict['Radio_dict']['water_recirculate'].grid(row = self.row_counter + 5, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Label_dict']['water_rec_temp_cutoff'].grid(row = self.row_counter + 6, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Scale_dict']['water_rec_temp_cutoff_scale'].grid(row = self.row_counter + 6, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Label_dict']['water_rec_temp_cutoff_status'].grid(row = self.row_counter + 6, column = 2, sticky = "w", pady = 2, columnspan = 1, rowspan = 1)

        self.gui_dict['Radio_dict']['infuse_sample'].grid(row = self.row_counter + 7, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Radio_dict']['infuse_water'].grid(row = self.row_counter + 8, column = 0, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        self.gui_dict['Check_dict']['infuse_sample_or_water'].grid(row = self.row_counter + 7, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 1)
        # self.gui_dict['Button_dict']['infuse'].grid(row = self.row_counter + 7, column = 1, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)
        # self.gui_dict['Button_dict']['infuse_stop'].grid(row = self.row_counter + 7, column = 2, sticky = "e", pady = 2, columnspan = 1, rowspan = 2)

    def get_temperatures(self):
        self.rs485_gui_slave.coils_list[4] = 1
        self.rs485_gui_slave.update_slave_via_reg_list()
        self.rs485_gui_slave.update_gui()

        for num_temp_sensor in range(1,7):            
            self.gui_dict['Label_dict']['temperature_' + str(num_temp_sensor) + '_value'].config(text = str(self.rs485_gui_slave.input_reg_list[num_temp_sensor + 6]))

    def tsm_process_sample(self):       
        # if True:
        if (self.gui_dict['Check_dict']['process_sample_IntVar'].get() == 1):
            print("In tsm_process_sample(): START")

            # Disable the withdraw / recirculate RadioButton until user aborts or timeout.
            self.gui_dict['Radio_dict']['sample_withdraw'].config(state = 'disabled')
            self.gui_dict['Radio_dict']['sample_recirculate'].config(state = 'disabled')
            
            self.gui_dict['Check_dict']['process_water'].config(state = 'disabled')  # Disable the Process water sections as well, since the valve 5 conflicts between sample and water. 
            
            if self.gui_dict['Check_dict']['infuse_sample_or_water_IntVar'].get() == True:
                self.gui_dict['Check_dict']['infuse_sample_or_water'].config(state = 'normal') # disable infusion section only if process sample section is being used.                
            else:
                self.gui_dict['Check_dict']['infuse_sample_or_water'].config(state = 'disabled') # disable infusion section only if process sample section is being used.
            
            # self.gui_dict['Radio_dict']['infuse_sample'].config(state = 'disabled')
            # self.gui_dict['Radio_dict']['infuse_water'].config(state = 'disabled')

            action = self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'].get()     # "withdraw" or "recirculate" 
            # We set the slider positions in the gui and call self.tsm_set_valve_positions()
            if action == "withdraw":
                self.gui_dict['Scale_dict']['set_servo_valve_1_IntVar'].set(2) 
                self.gui_dict['Scale_dict']['set_servo_valve_2_IntVar'].set(2) 
                self.gui_dict['Scale_dict']['set_servo_valve_5_IntVar'].set(1)    # Set the 5th servo valve to flowcell. 
            elif action == "recirculate":
                self.gui_dict['Scale_dict']['set_servo_valve_1_IntVar'].set(1) 
                self.gui_dict['Scale_dict']['set_servo_valve_2_IntVar'].set(1)             
                #self.gui_dict['Scale_dict']['set_servo_valve_5_IntVar'].set(2)    # Set the 5th servo valve to flowcell. Don't care condition.

            # Disable the user from changing the servo sliders until the process completes or by a timeout.
            # The slider can be "set" or "moved" from the code to a different value even when it is disabled.        
            # Even if the slider is disabled, the visuals don't seem to change and it still looks active.
            for num_servo_valve in range(1,7):
                self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) ].config(state = "disabled")
            # self.window.update()

            self.tsm_set_valve_positions()
            
            # wait a bit for the servos to move and stop, 1second.
            # self.wait(3)

            self.gui_dict['Scale_dict']['set_pump_1_IntVar'].set(value = 50)    # Set pump 1 RPM, common RPM for withdraw and recirculation.
            self.update()

            if action == "withdraw":
                # Turn on the pump for 30 seconds or until the user unchecks the button
                self.time_start_sample = copy.deepcopy(time.time())      # Start a timer            
                self.update()  
                self.tsm_clear_plots()          
                self.while_sample_withdraw()    # We need to move the while True loop to a recursive function such that TK GUI's widgets are active.
            elif action == "recirculate":                                       
                self.time_start_sample = copy.deepcopy(time.time())      # Start a timer
                self.sample_temp_diff_list = []     # reset the list to monitor temp_diff
                self.tsm_clear_plots()
                self.while_sample_recirculate()       
        else:       
            print("In tsm_process_sample(): STOP")     
            self.gui_dict['Scale_dict']['set_pump_1_IntVar'].set(value = 1)    # Set pump 1 RPM to OFF  
            self.update()   
            self.set_to_normal()                   

    # Recursive function to simulate a While True loop while widgets are active. 
    def while_sample_withdraw(self):              
        self.time_now_sample = copy.deepcopy(time.time())      # Curent time

        # If the user unchecks the button or the timer runs out we stop the motor and return.
        if (self.gui_dict['Check_dict']['process_sample_IntVar'].get() == 0) or self.sample_withdraw_timeout < (self.time_now_sample - self.time_start_sample):        
            self.gui_dict['Label_dict']['process_sample_timeout'].config(text = str(self.sample_withdraw_timeout) + 's Timer @ ' + str(round(self.time_now_sample - self.time_start_sample,2)))
            self.gui_dict['Label_dict']['process_sample_pump_1_current'].config(text = "Pump 1 current "  + str(self.pumps_slave.input_reg_list[0]) + " mA")
            self.gui_dict['Scale_dict']['set_pump_1_IntVar'].set(1) # Turn OFF pump                    
            self.update()
            self.set_to_normal()
            print("In while_sample_withdraw(): User aborted process or timeout")
            return
        else:
            #print("In while_sample_withdraw(), Timer ", round(self.time_now_sample - self.time_start_sample,2))   
            self.gui_dict['Label_dict']['process_sample_timeout'].config(text = str(self.sample_withdraw_timeout) + 's Timer @ ' + str(round(self.time_now_sample - self.time_start_sample,2)))
            self.gui_dict['Label_dict']['process_sample_pump_1_current'].config(text = "Pump 1 current "  + str(self.pumps_slave.input_reg_list[0]) + " mA")
            self.tsm_plot_sample_rec_temp()

        self.window.after(100,self.while_sample_withdraw)

    # Recursive function to monitor the temperature and keep the pump running until the temperature is achieved or timeout or the user stops recicrulation.
    def while_sample_recirculate(self):
        self.target_sample_temp = self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_DoubleVar'].get()      # Get target temp from slider (realtime update too).  
        self.time_now_sample = copy.deepcopy(time.time())      # Curent time

        # If the user unchecks the button or the 30 timer runs out we stop the motor and return.
        if (self.gui_dict['Check_dict']['process_sample_IntVar'].get() == 0) or self.sample_rec_timeout < (self.time_now_sample - self.time_start_sample):        
            self.gui_dict['Label_dict']['process_sample_timeout'].config(text = str(self.sample_rec_timeout) + 's Timer @ ' + str(round(self.time_now_sample - self.time_start_sample,2)))   
            self.gui_dict['Label_dict']['process_sample_pump_1_current'].config(text = "Pump 1 current "  + str(self.pumps_slave.input_reg_list[0]) + " mA")
            self.gui_dict['Scale_dict']['set_pump_1_IntVar'].set(1) # Turn OFF pump                    
            self.update()
            self.set_to_normal()
            print("In while_sample_recirculate(): User aborted process or timeout")           
            return
        else:  
            #print("In while_sample_recirculate(), Timer ", round(self.time_now_sample - self.time_start_sample,2))   
            self.gui_dict['Label_dict']['process_sample_timeout'].config(text = str(self.sample_rec_timeout) + 's Timer @ ' + str(round(self.time_now_sample - self.time_start_sample,2)))                      
            self.gui_dict['Label_dict']['process_sample_pump_1_current'].config(text = "Pump 1 current "  + str(self.pumps_slave.input_reg_list[0]) + " mA")
            self.update()      # This will automatically update the temperatures. 
            self.tsm_plot_sample_rec_temp()
            
            # If temperature difference between target and current is less than 3 degC we exit , else we wait until timeout or the user aborts
            temp_diff = round(abs(self.rs485_gui_slave.input_reg_list[8]- self.target_sample_temp),2)
            self.gui_dict['Label_dict']['sample_rec_temp_cutoff_status'] .config(text = str(temp_diff))
            self.sample_temp_diff_list.append(temp_diff)
            self.sample_temp_diff_list = self.sample_temp_diff_list[-10:]   # Keep only latest 10 elements of the list.
            avg = np.mean(self.sample_temp_diff_list)                       # use the average of samples to decide if the temperature is stabilised.
            if (avg <= self.temp_diff_tol):                
                print("In while_sample_recirculate(), Sample temperature is stabilised ", temp_diff)
                self.gui_dict['Scale_dict']['set_pump_1_IntVar'].set(value = 1)    # Set pump 1 RPM to OFF  
                self.update()
                self.gui_dict['Label_dict']['sample_rec_temp_cutoff_status'] .config(text = str(temp_diff), fg="green")   
                self.set_to_normal()                                        
                return            
            else:
                self.gui_dict['Label_dict']['sample_rec_temp_cutoff_status'] .config(text = str(temp_diff), fg="orange")
                print("while_sample_recirculate(): Waiting for temperature to stabilise")
                print("Target temp = ", round(self.target_sample_temp,2))
                print("Current temp = ", round(self.rs485_gui_slave.input_reg_list[8],2))

        self.window.after(100,self.while_sample_recirculate)

    def tsm_process_water(self):       
        # if True:
        if (self.gui_dict['Check_dict']['process_water_IntVar'].get() == 1):
            print("In tsm_process_water(): START")

            # Disable the withdraw / recirculate RadioButton until user aborts or timeout.
            self.gui_dict['Radio_dict']['water_withdraw'].config(state = 'disabled')
            self.gui_dict['Radio_dict']['water_recirculate'].config(state = 'disabled')
            self.gui_dict['Check_dict']['process_sample'].config(state = 'disabled')  # Disable the Process water sections as well, since the valve 5 conflicts between sample and water. 
            
            if self.gui_dict['Check_dict']['infuse_sample_or_water_IntVar'].get() == True:
                self.gui_dict['Check_dict']['infuse_sample_or_water'].config(state = 'normal') # disable infusion section only if process sample section is being used.                
            else:
                self.gui_dict['Check_dict']['infuse_sample_or_water'].config(state = 'disabled') # disable infusion section only if process sample section is being used.         
            
            action = self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'].get()     # "withdraw" or "recirculate" 
            # We set the slider positions in the gui and call self.tsm_set_valve_positions()
            if action == "withdraw":
                self.gui_dict['Scale_dict']['set_servo_valve_3_IntVar'].set(2) 
                self.gui_dict['Scale_dict']['set_servo_valve_4_IntVar'].set(2) 
                self.gui_dict['Scale_dict']['set_servo_valve_5_IntVar'].set(2)    # Set the 5th servo valve to flowcell. 
            elif action == "recirculate":
                self.gui_dict['Scale_dict']['set_servo_valve_3_IntVar'].set(1) 
                self.gui_dict['Scale_dict']['set_servo_valve_4_IntVar'].set(1)             
                #self.gui_dict['Scale_dict']['set_servo_valve_5_IntVar'].set(2)    # Set the 5th servo valve to flowcell. Don't care condition.

            self.gui_dict['Scale_dict']['set_pump_2_IntVar'].set(value = 50)    # Set pump 2 RPM, common RPM for withdraw and recirculation.

            # Disable the user from changing the servo sliders until the process completes or by a timeout.
            # The slider can be "set" or "moved" from the code to a different value even when it is disabled.        
            # Even if the slider is disabled, the visuals don't seem to change and it still looks active.
            for num_servo_valve in range(1,7):
                self.gui_dict['Scale_dict']['set_servo_valve_' + str(num_servo_valve) ].config(state = "disabled")
            # self.window.update()

            self.tsm_set_valve_positions()
            
            if action == "withdraw":
                # Turn on the pump for 30 seconds or until the user unchecks the button
                self.time_start_water = copy.deepcopy(time.time())      # Start a timer            
                self.update()    
                self.tsm_clear_plots()        
                self.while_water_withdraw()    # We need to move the while True loop to a recursive function such that TK GUI's widgets are active.
            elif action == "recirculate":                
                self.target_water_temp = self.gui_dict['Scale_dict']['water_rec_temp_cutoff_DoubleVar'].get()      # Get target temp from slider.           
                self.time_start_water = copy.deepcopy(time.time())      # Start a timer
                self.tsm_clear_plots()
                self.while_water_recirculate()     

            #self.set_to_normal()          
        else:       
            print("In tsm_process_water(): STOP")     
            self.gui_dict['Scale_dict']['set_pump_2_IntVar'].set(value = 1)    # Set pump 1 RPM to OFF              
            self.update()                      
            self.set_to_normal()

    # Recursive function to simulate a While True loop while widgets are active. 
    def while_water_withdraw(self):    
        self.time_now_water = copy.deepcopy(time.time())      # Curent time

        # If the user unchecks the button or the timer runs out we stop the motor and return.
        if (self.gui_dict['Check_dict']['process_water_IntVar'].get() == 0) or self.water_withdraw_timeout < (self.time_now_water - self.time_start_water):        
            self.gui_dict['Label_dict']['process_water_timeout'].config(text = str(self.water_withdraw_timeout) + 's Timer @ ' + str(round(self.time_now_water - self.time_start_water,2)))
            self.gui_dict['Label_dict']['process_water_pump_2_current'].config(text = "Pump 2 current "  + str(self.pumps_slave.input_reg_list[1]) + " mA")
            self.gui_dict['Scale_dict']['set_pump_2_IntVar'].set(1) # Turn OFF pump                    
            self.update()
            self.set_to_normal()
            print("In while_water_withdraw(): User aborted process or timeout")
            return
        else:
            #print("In while_water_withdraw(), Timer ", round(self.time_now_water - self.time_start_water,2))   
            self.gui_dict['Label_dict']['process_water_timeout'].config(text = str(water_withdraw_timeout) + 's Timer @ ' + str(round(self.time_now_water - self.time_start_water,2)))
            self.gui_dict['Label_dict']['process_water_pump_2_current'].config(text = "Pump 2 current "  + str(self.pumps_slave.input_reg_list[1]) + " mA")
            self.tsm_plot_sample_rec_temp()

        self.window.after(100,self.while_water_withdraw)

    # Recursive function to monitor the temperature and keep the pump running until the temperature is achieved or timeout or the user stops recicrulation.
    def while_water_recirculate(self):
        self.target_sample_temp = self.gui_dict['Scale_dict']['water_rec_temp_cutoff_DoubleVar'].get()      # Get target temp from slider (realtime update too)  
        self.time_now_water = copy.deepcopy(time.time())      # Curent time

        # If the user unchecks the button or the timer runs out we stop the motor and return.
        if (self.gui_dict['Check_dict']['process_water_IntVar'].get() == 0) or self.water_rec_timeout < (self.time_now_water - self.time_start_water):        
            self.gui_dict['Label_dict']['process_water_timeout'].config(text = str(self.water_rec_timeout) + 's Timer @ ' + str(round(self.time_now_water - self.time_start_water,2)))      
            self.gui_dict['Label_dict']['process_water_pump_2_current'].config(text = "Pump 2 current "  + str(self.pumps_slave.input_reg_list[1]) + " mA")                
            self.gui_dict['Scale_dict']['set_pump_2_IntVar'].set(1) # Turn OFF pump                    
            self.update()
            self.set_to_normal()
            print("In while_water_recirculate(): User aborted process or timeout")           
            return
        else:  
            #print("In while_water_recirculate(), Timer ", round(self.time_now_water - self.time_start_water,2))   
            self.gui_dict['Label_dict']['process_water_timeout'].config(text = str(self.water_rec_timeout) + 's Timer @ ' + str(round(self.time_now_water - self.time_start_water,2)))    
            self.gui_dict['Label_dict']['process_water_pump_2_current'].config(text = "Pump 2 current "  + str(self.pumps_slave.input_reg_list[1]) + " mA")                  
            self.update()      # This will automatically update the temperatures. 
            self.tsm_plot_sample_rec_temp()
            
            # If temperature difference between target and current is less than 3 degC we exit , else we wait until timeout or the user aborts
            temp_diff = round(abs(self.rs485_gui_slave.input_reg_list[10]- self.target_water_temp),2)
            self.gui_dict['Label_dict']['water_rec_temp_cutoff_status'] .config(text = str(temp_diff))
            self.water_temp_diff_list.append(temp_diff)
            self.water_temp_diff_list = self.water_temp_diff_list[-10:]     # Keep only latest 10 elements of the list.
            avg = np.mean(self.water_temp_diff_list)                        # use the average of samples to decide if the temperature is stabilised.
            if (avg <= self.temp_diff_tol):
                print("In while_water_recirculate(), water temperature is stabilised ", temp_diff)
                self.gui_dict['Scale_dict']['set_pump_2_IntVar'].set(value = 1)    # Set pump 1 RPM to OFF  
                self.update()
                self.gui_dict['Label_dict']['water_rec_temp_cutoff_status'] .config(text = str(temp_diff), fg="green")        
                self.set_to_normal()                                   
                return            
            else:
                self.gui_dict['Label_dict']['water_rec_temp_cutoff_status'] .config(text = str(temp_diff), fg="orange")
                print("while_water_recirculate(): Waiting for temperature to stabilise.")
                print("Target temp = ", round(self.target_sample_temp,2))
                print("Current temp = ", round(self.rs485_gui_slave.input_reg_list[10],2))                

        self.window.after(100,self.while_water_recirculate)

    def tsm_infusion_to_flow_cell(self):
        if self.gui_dict['Check_dict']['infuse_sample_or_water_IntVar'].get() == True:
            print("In tsm_infusion_to_flow_cell(): START")

            # Disable the infuse sample / water RadioButton until user aborts or timeout.
            self.gui_dict['Radio_dict']['infuse_sample'].config(state = 'disabled')
            self.gui_dict['Radio_dict']['infuse_water'].config(state = 'disabled')
            self.gui_dict['Check_dict']['process_sample'].config(state = 'disabled')
            self.gui_dict['Check_dict']['process_water'].config(state = 'disabled')
            
            # When we want to infuse the sample to the flow cell, 
            # We can set the sample section to "withdraw" and set the Process Sample check box to True.            
            if self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'].get() == "sample":
                self.gui_dict['Radio_dict']['sample_withdraw_recirculate_StringVar'].set("withdraw") 
                self.gui_dict['Check_dict']['process_sample_IntVar'].set(1)     # Setting a value of 1 in a checkbox != actually clicking the checkbox.
                self.gui_dict['Check_dict']['process_water_IntVar'].set(0)      # Setting a value of 1 in a checkbox != actually clicking the checkbox.
                self.tsm_process_sample()              
            
            # When we want to infuse the water to the flow cell, 
            # We can set the water section to "withdraw" and set the Process water check box to True.            
            elif self.gui_dict['Radio_dict']['infuse_sample_water_StringVar'].get() == "water":
                self.gui_dict['Radio_dict']['water_withdraw_recirculate_StringVar'].set("withdraw") 
                self.gui_dict['Check_dict']['process_sample_IntVar'].set(0)     # Setting a value of 1 in a checkbox != actually clicking the checkbox.
                self.gui_dict['Check_dict']['process_water_IntVar'].set(1)      # Setting a value of 1 in a checkbox != actually clicking the checkbox.
                self.tsm_process_water()               
        else:
            print("In tsm_infusion_to_flow_cell(): STOP")     
            self.gui_dict['Scale_dict']['set_pump_1_IntVar'].set(value = 1)    # Set pump 1 RPM to OFF  
            self.gui_dict['Scale_dict']['set_pump_2_IntVar'].set(value = 1)    # Set pump 2 RPM to OFF  
            self.update()    
            self.gui_dict['Check_dict']['process_sample_IntVar'].set(0)     # Setting a value of 1 in a checkbox != actually clicking the checkbox.
            self.gui_dict['Check_dict']['process_water_IntVar'].set(0)      # Setting a value of 1 in a checkbox != actually clicking the checkbox.            
            self.set_to_normal()

    def tsm_plot_sample_rec_temp(self):        

        # Get data.
        time = dt.datetime.now().minute + (dt.datetime.now().second/100)
        self.time_temperature_list.append(time)
        # self.time_temperature_list.append(dt.datetime.now().strftime('%H:%M:%S.%f'))

        self.sample_withdrawal_point_T_list.append(self.rs485_gui_slave.input_reg_list[7])
        self.sample_rec_point_T_list.append(self.rs485_gui_slave.input_reg_list[8])
        self.sample_cutoff_point_T_list.append(self.gui_dict['Scale_dict']['sample_rec_temp_cutoff_DoubleVar'].get())        
        
        self.water_withdrawal_point_T_list.append(self.rs485_gui_slave.input_reg_list[9])
        self.water_rec_point_T_list.append(self.rs485_gui_slave.input_reg_list[10])   
        self.water_cutoff_point_T_list.append(self.gui_dict['Scale_dict']['water_rec_temp_cutoff_DoubleVar'].get())

        # limit the axis
        self.time_temperature_list = self.time_temperature_list[-20:]

        self.sample_withdrawal_point_T_list = self.sample_withdrawal_point_T_list[-20:]
        self.sample_rec_point_T_list = self.sample_rec_point_T_list[-20:]
        self.sample_cutoff_point_T_list = self.sample_cutoff_point_T_list[-20:]

        self.water_withdrawal_point_T_list = self.water_withdrawal_point_T_list[-20:]
        self.water_rec_point_T_list = self.water_rec_point_T_list[-20:]
        self.water_cutoff_point_T_list = self.water_cutoff_point_T_list[-20:]

        # plotting the graph
        self.ax1.plot(self.time_temperature_list, self.sample_withdrawal_point_T_list,'b')
        self.ax1.plot(self.time_temperature_list, self.sample_rec_point_T_list,'g')
        self.ax1.plot(self.time_temperature_list, self.sample_cutoff_point_T_list,'r')
        self.ax1.legend(['withdrawal','recirculation','cutoff'])   
        
        self.ax2.plot(self.time_temperature_list, self.water_withdrawal_point_T_list,'b')
        self.ax2.plot(self.time_temperature_list, self.water_rec_point_T_list,'g')
        self.ax2.plot(self.time_temperature_list, self.water_cutoff_point_T_list,'r')   
        self.ax2.legend(['withdrawal','recirculation','cutoff'])   

        self.draw_canvas.draw()            

    def tsm_clear_plots(self):
        self.ax1.clear()
        self.ax2.clear()  
        self.ax1.grid()
        self.ax2.grid()           
      
    def set_to_normal(self):
        self.gui_dict['Radio_dict']['sample_withdraw'].config(state = 'normal')     # Enable the withdraw / recirculate RadioButton for future use.
        self.gui_dict['Radio_dict']['sample_recirculate'].config(state = 'normal')  # Enable the withdraw / recirculate RadioButton for future use.
        self.gui_dict['Radio_dict']['water_withdraw'].config(state = 'normal')
        self.gui_dict['Radio_dict']['water_recirculate'].config(state = 'normal')     
        self.gui_dict['Check_dict']['process_sample'].config(state = 'normal')
        self.gui_dict['Check_dict']['process_water'].config(state = 'normal')
        self.gui_dict['Check_dict']['infuse_sample_or_water'].config(state = 'normal')
        self.gui_dict['Radio_dict']['infuse_water'].config(state = 'normal')
        self.gui_dict['Radio_dict']['infuse_sample'].config(state = 'normal')

        self.gui_dict['Check_dict']['process_sample_IntVar'].set(0)
        self.gui_dict['Check_dict']['process_water_IntVar'].set(0)
        self.gui_dict['Check_dict']['infuse_sample_or_water_IntVar'].set(0)
        self.window.update()

    def tsm_enable(self):
        print("In tsm_enable(): ...")        

    def tsm_start(self):
        print("In tsm_start(): ...")       
          
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
        self.window.update()

    # Function that runs when the update button is pressed.
    # It gets the values from the gui and send it to two slaves, 1 - TSM, 2 - The peristatic pumps.
    def update(self):               
        self.rs485_gui_slave.holding_reg_list[9] = copy.deepcopy(self.gui_dict['Scale_dict']['set_pump_1_IntVar'].get())
        self.rs485_gui_slave.holding_reg_list[10] = copy.deepcopy(self.gui_dict['Scale_dict']['set_pump_2_IntVar'].get())

        # self.pumps_slave.coils_list[0] = 1  # Enable the pumps module, not required for now.
        self.pumps_slave.holding_reg_list[0] = self.rs485_gui_slave.holding_reg_list[9]     # Set motor rpm for pump 1
        self.pumps_slave.holding_reg_list[1] = self.rs485_gui_slave.holding_reg_list[10]    # Set motor rpm for pump 2
        self.pumps_slave.update_slave_via_reg_list()    # update the pumps slave.
        # self.pumps_slave.update_gui()       # there's no GUI for the slave. 

        self.tsm_set_valve_positions()

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
    slave_2 = rs485_gui_slave(window = root_window,
                                slave_number = 2,
                                modbus_interface = mi,
                                slaves_mcfg = slaves_mcfg,
                                color="white", 
                                canvas_height=500, 
                                canvas_width=850)

    pumps_slave = rs485_gui_slave(window = root_window, slave_number = 1, modbus_interface = mi, slaves_mcfg = slaves_mcfg, color="white")
    pumps_slave.gen_slave_modbus_gui() 
    #pumps_slave.gen_slave_modbus_gui() # No need to display the gui for pumps.      

    plots = Element()
    tsm = Temperature_stabilisation_module(window = root_window, plots=plots, color = "white")    
    tsm.canvas_main.place(x=0, y = 0)    
    # tsm.canvas_main.grid(row = 0, column = 0)

    plots.canvas.place(x=500,y=600)

    root_window.mainloop()       # Blocking function.   
