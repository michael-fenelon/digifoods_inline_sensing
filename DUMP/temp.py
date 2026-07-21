
        # Input registers, read upto 100 INput registers
        for input_reg_num in range(0, 100):
            # # If the slave_dict has the Nth input_register we create and place a check button on the frame, else, we break out of the for loop.
            if "slave_" + str(self.slave_number) + "_Input_register_" + str(input_reg_num) in slaves_mcfg.dict:  
                self.input_reg_list.append(0)

                # Display what is in the XLSX sheet
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)] = Label(self.frame, 
                                                                                                    text = "Input_register " + str(input_reg_num) + ": " + slaves_mcfg.dict['slave_' + str(self.slave_number) + "_Input_register_" + str(input_reg_num)], 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num)].grid(row = 4 + coil_num + discrete_inputs_num + input_reg_num * 2 + 1, column = 0, sticky = "w", pady = 2, columnspan = 2)

                # Display current value
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"] = Label(self.frame, 
                                                                                                    text = "current value = " + str(100), 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_current"].grid(row = 4 + coil_num + discrete_inputs_num + input_reg_num * 2 + 2, column = 0, sticky = "e", pady = 2, columnspan = 1)

                

                # # Display the desired value.
                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_target"] = Label(self.frame, 
                                                                                                    text = "target value = ", 
                                                                                                    bg = "white", wraplength = self.canvas_width - 10)

                self.gui_dict['Label_dict']['input_register_' + str(input_reg_num) + "_target"].grid(row = 4 + coil_num + discrete_inputs_num + input_reg_num * 2 + 2, column = 3, sticky = "w", pady = 2, columnspan = 1)
                
                # Create Entry box and place it.
                self.gui_dict['Entry_dict']['input_register_' + str(input_reg_num) + "_target_StringVar"] = tk.StringVar()
                self.gui_dict['Entry_dict']['input_register_' + str(input_reg_num) + "_target"] = Entry(self.frame, 
                                                                                                                    textvariable = self.gui_dict['Entry_dict']['input_register_' + str(input_reg_num) + "_target_StringVar"],
                                                                                                                    border=1, width=10)
                self.gui_dict['Entry_dict']['input_register_' + str(input_reg_num) + "_target"].grid(row = 4 + coil_num + discrete_inputs_num + input_reg_num * 2 + 2, column = 4, sticky = "e", pady = 2, columnspan = 1)                                                                                                          

            else:
                print("No more input_registers !")
                break


