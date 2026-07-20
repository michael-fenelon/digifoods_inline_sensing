        for holding_register_num in range(0, 100):
            self.gui_dict['Label_dict']['holding_register_' + str(holding_register_num)] = Label(self.frame, text = "holding_register " + str(holding_register_num) + ": " + slaves_modbus_config.dict['slave_' + str(self.slave_number) + "_holding_register_" + str(holding_register_num)], bg = "white", wraplength = 200)
            self.gui_dict['Label_dict']['holding_register_' + str(holding_register_num)].grid(row = 4 + holding_register_num, column = 0, sticky = "w", pady = 2, columnspan = 3)

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

            #     self.gui_dict['Entry_dict']['holding_register_' + str(holding_register_num)].grid(row = 4 + holding_register_num, column = 0, sticky = "w", pady = 2, columnspan = 3)                              
            # else:
            #     print("No more holding_registers !")
            #     break