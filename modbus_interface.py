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

        # 2. Open the connection
        self.connection = self.client.connect()
        print("Connection ", self.connection)

    def test(self):
        if self.connection:
            print("Serial port connected. Starting polling...")
            toggle = True
            try:
                while True:
                    print("\n")
                    # 3. Poll the device (Read 10 Holding Registers)
                    # address=0 is the starting register
                    # count=10 is the number of registers to read
                    # slave=1 is the target device ID
                    # result = self.client.read_holding_registers(address=0, count=1, device_id=5)            
                    
                    # 4. Check for errors and print data
                    # if result.isError():
                    #     print("Device returned a Modbus error.")
                    # else:
                    #     print(f"Register Values: {result.registers}")

                    # Write a HIGH/LOW to the coil
                    toggle = not toggle
                    result = self.client.write_coil(address=0, value=toggle, device_id=5)   # Just to flash an led. 
                    # result = self.client.write_coil(address=0, value=0, device_id=5)
                    print("Write coils : ", result)
                    
                    # Write HIGH/LOW to all coils with a list
                    # result = self.client.write_coils(address=0, values=[0,0], device_id=5)     # Pass a list of bools 
                    # print("Write coils : ", result)

                    # # Read discrete inputs
                    # result = self.client.read_discrete_inputs(address = 0, count = 2, device_id=5) # It will return a default of 8 bits, even if count = 2
                    # print("Discrete input : ", result)
                    # print("bits : ", result.bits)
                    

                    # # Write a value to the holding register
                    # # result = self.client.write_register(address=0, value=100, device_id=5)
                    # print("Write register : ", result)

                    # # Write values to the holding registers with a integer list.
                    # result = self.client.write_registers(address=0, values=[100,100,0,0], device_id=5)    # Pass list of integers
                    # print("Write registers : ", result)
                    
                    # result = self.client.read_input_registers(address=0, count=2, device_id=5)  # Get milliamps from motor 1                
                    # print("Input registers : ", result)
                    # print("registers : ", result.registers)
                        
                    # 5. Wait before polling again
                    time.sleep(0.1)  # Poll every 2 seconds
                    
            except KeyboardInterrupt:
                print("Polling stopped. Closing connection.")
                self.client.close()
        else:
            print("Failed to connect to the serial port.")

if __name__ == '__main__':    
    mi = Modbus_Interface()
    mi.test()
    











