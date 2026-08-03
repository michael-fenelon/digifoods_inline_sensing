## Demo code of Modbus master to control a modbus_arduino_slave.
# library: https://pymodbus.readthedocs.io/en/latest/
import time
from pymodbus.client import ModbusSerialClient

class Modbus_Interface():
    def __init__(self):
        # 1. Set up your self.client (RS-485 / RTU)
        self.client = ModbusSerialClient(
            port='/dev/ttyUSB0',  # Change this to your COM port (e.g., 'COM3' on Windows)
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1            # Wait up to 1 second for a response
        ) 

        # https://stackoverflow.com/questions/55662896/how-should-negative-numbers-be-represented-in-the-pymodbus-input-register
        # This has been removed and changed to https://pymodbus.readthedocs.io/en/latest/source/client.html#pymodbus.client.mixin.ModbusClientMixin.convert_from_registers

        # 2. Open the connection
        self.connection = self.client.connect()
        print("Connection ", self.connection)

    def test(self):
        if self.connection:
            print("Serial port connected. Starting polling...")
            toggle = True
            device_id = 10
            try:
                while True:
                    print("\n")
                    # 3. Poll the device (Read 10 Holding Registers)
                    # address=0 is the starting register
                    # count=10 is the number of registers to read
                    # slave=1 is the target device ID
                    # result = self.client.read_holding_registers(address=0, count=1, device_id = device_id)            
                    
                    # 4. Check for errors and print data
                    # if result.isError():
                    #     print("Device returned a Modbus error.")
                    # else:
                    #     print(f"Register Values: {result.registers}")

                    # Write a HIGH/LOW to the coil
                    toggle = not toggle
                    result = self.client.write_coil(address=0, value=toggle, device_id = device_id)   # Just to flash an led. 
                    # result = self.client.write_coil(address=0, value=0, device_id = device_id)
                    print("Write coils : ", result)
                    
                    # Write HIGH/LOW to all coils with a list
                    # result = self.client.write_coils(address=0, values=[1,1,1,1,1,0], device_id = device_id)     # Pass a list of bools 
                    # print("Write coils : ", result)

                    # # Read discrete inputs
                    # result = self.client.read_discrete_inputs(address = 0, count = 2, device_id = device_id) # It will return a default of 8 bits, even if count = 2
                    # print("Discrete input : ", result)
                    # print("bits : ", result.bits)                    

                    # # Write a value to the holding register
                    # result = self.client.write_register(address=0, value=10, device_id = device_id)
                    # print("Write register : ", result)

                    # # Write values to the holding registers with a integer list.
                    # result = self.client.write_registers(address=0, values=[100,100,0,0], device_id = device_id)    # Pass list of integers
                    # print("Write registers : ", result)

                    # # Convert -ve numbers from Arduino's int16_t list -> receive it as uint16_t -> convert to int16 in python. 
                    # print("Convert from Arduino's INT16_T list -> Pymodbus's default UINT16 list -> Actual INT16 list")
                    # result = self.client.read_holding_registers(address=0, count= 4, device_id = device_id)    
                    # print("Before conversion = ", result.registers)                    
                    # res = self.client.convert_from_registers(result.registers, self.client.DATATYPE.INT16, 'little')    #  little endian since arduino uses little endian
                    # print("After conversion", res)

                    # # Write -ve values to the holding registers of arduino with a signed integer list.                    
                    # print("Convert a generic INT16_t list to Pymodbus' default UINT16_t list -> Arduino's INT16_T list")
                    # reg_list = self.client.convert_to_registers(value=[-100, 100, 0, 0], data_type=self.client.DATATYPE.INT16, word_order="little")
                    # print("reg_list ", reg_list)
                    # result = self.client.write_registers(address=0, values=reg_list, device_id = device_id)    # Pass list of integers
                    # print("Write registers : ", result)

                    # # R+W of Floats to Arduino directly is not possible.
                    # # Instead we scale and divide the values before transmisstion. 
                    # # Eg of writing float values from Pymodbus to Arduino
                    # # SEE: ~/modbus_comm_test/modbus_comm_test.ino 
                    # print("Writing floats to Arduino from Pymodbus")
                    # f_list = [1.23, -0.5]
                    # f_list = [int(v * 10)  for v in f_list]  
                    # print(f_list)   # [12, -5]
                    # # Now convert the INT16_T values to UINT16_T values. 
                    # reg_list = self.client.convert_to_registers(value=f_list, data_type=self.client.DATATYPE.INT16, word_order="little")
                    # # Now, send the data to Arduino. 
                    # res = self.client.write_registers(address=0, values=reg_list, device_id = device_id) 
                    # # Then, on the arduino side we need to divide by 10. The Arduino has INT16_T arrays. 

                    # # Similarily to Read float data from Arduino to Pymodbus. 
                    # # Lets say the Arduino's array_holding_reg = [0.4 * 10, -5.2 * 10, 0.0, 0.0] = [4, -52, 0, 0]
                    # print("Reading floats from Arduino to Pymodbus")
                    # result = self.client.read_holding_registers(address=0, count= 4, device_id = device_id) 
                    # reg_list = self.client.convert_from_registers(result.registers, self.client.DATATYPE.INT16, 'little')
                    # print("reg_list ", reg_list)
                    # print("float list ", [v/10 for v in reg_list])

                    # result = self.client.read_input_registers(address=0, count=5, device_id = device_id) # Read the input register from Arduino
                    # print("Convert from UINT16 -> INT16")
                    # print("Before conversion: ", result.registers)
                    # res = self.client.convert_from_registers(result.registers, self.client.DATATYPE.INT16, 'little')
                    # print("After conversion", res)
                        
                    # 5. Wait before polling again
                    time.sleep(2)  
                    
            except KeyboardInterrupt:
                print("Polling stopped. Closing connection.")
                self.client.close()
        else:
            print("Failed to connect to the serial port.")

if __name__ == '__main__':    
    # print("Pymodbus version = ", pymodbus.__version__)  #  3.14.0
    mi = Modbus_Interface()
    mi.test()
    











