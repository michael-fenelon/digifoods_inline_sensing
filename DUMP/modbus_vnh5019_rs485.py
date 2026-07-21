## Demo code of Modbus master to control a modbus_arduino_slave.
# library: https://pymodbus.readthedocs.io/en/latest/

import time
from pymodbus.client import ModbusSerialClient

# 1. Set up your client (RS-485 / RTU)
client = ModbusSerialClient(
    port='/dev/ttyUSB0',  # Change this to your COM port (e.g., 'COM3' on Windows)
    baudrate=9600,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=1            # Wait up to 1 second for a response
)

# 2. Open the connection
connection = client.connect()

if connection:
    print("Serial port connected. Starting polling...")
    try:
        while True:
            # 3. Poll the device (Read 10 Holding Registers)
            # address=0 is the starting register
            # count=10 is the number of registers to read
            # slave=1 is the target device ID
            result = client.read_holding_registers(address=0, count=1, device_id=1)            
            
            # 4. Check for errors and print data
            if result.isError():
                print("Device returned a Modbus error.")
            # else:
            #     print(f"Register Values: {result.registers}")

            # Write a value to the holding register
            result = client.write_register(address=0, value=10, device_id=1)
            
            result = client.read_input_registers(address=0, count=1, device_id=1)  # Get milliamps from motor 1
            # decoded = result.decode()
            # print(result)
            print("milliamps", result)

            # Write a HIGH/LOW to the coil
            # result = client.write_coil(address=0, value=1, device_id=1)
            # result = client.write_coil(address=1, value=1, device_id=1)
                
            # 5. Wait before polling again
            time.sleep(1)  # Poll every 2 seconds
            
    except KeyboardInterrupt:
        print("Polling stopped. Closing connection.")
        client.close()
else:
    print("Failed to connect to the serial port.")
