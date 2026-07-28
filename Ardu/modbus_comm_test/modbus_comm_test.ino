
// A basic program to test with pymodbus for -negative numbers and floats.

// RS485
// We use the official arduino repo:
//https://github.com/CMB27/ModbusRTUSlave/tree/main/examples/ModbusRTUSlaveExample
//https://github.com/CMB27/ModbusSlaveLogic/tree/main/src
#include <ModbusRTUSlave.h>
#include <SoftwareSerial.h>

#define RS485_TX 8
#define RS485_RX 9
#define SLAVE_ADDRESS 10
#define SLAVE_BAUD_RATE 9600
#define SLAVE_SERIAL_CONFIG SERIAL_8N1
#define DE_PIN 10   // pinsDE and RE on the MAX485 module are shorted.

SoftwareSerial RS485_serial(RS485_RX, RS485_TX);  // Create a serial port with the software serial pins.
ModbusRTUSlave modbus(RS485_serial, DE_PIN);       // Create a modbus object that uses the software serial port.

const uint8_t num_coils = 6;                        // Number of digital outputs, W only
bool array_coils[num_coils] = {1, 1, 1, 0, 0, 0};   // array holding all the digital outputs, W only

const uint8_t num_discrete_inputs = 2;              // Number of digital inputs, R only
bool array_discrete_inputs[num_discrete_inputs] = {true, false};

const uint8_t num_holding_registers = 4;            // Number of holding registers, R + W
int16_t array_holding_registers[num_holding_registers] = {0, 0, 4, -52}; // Array holding N holding registers. R+W
//uint16_t array_holding_registers[num_holding_registers] = {6, 7, 8, 9}; // Array holding N holding registers. R+W

const uint8_t num_input_registers = 5;              // Number of input registers, R only
int16_t array_input_registers[num_input_registers] = {100, -200, 300, -400, 500};  // Array for input registers, R only.
//uint16_t array_input_registers[num_input_registers] = {1, 2, 3, 4, 5};  // Array for input registers, R only.

void setup()
{
  Serial.begin(9600);
  Serial.println("Slave 10; Sample extraction module");
  RS485_serial.begin(9600);
  modbus.begin(SLAVE_ADDRESS, SLAVE_BAUD_RATE, SLAVE_SERIAL_CONFIG);  // Slave address = 1, Baud rate = 9600, Serial parameters = 8bit, no parity, 1 stop bit.
  modbus.configureCoils(array_coils, num_coils);
  modbus.configureDiscreteInputs(array_discrete_inputs, num_discrete_inputs);
  modbus.configureHoldingRegisters(array_holding_registers, num_holding_registers);
  modbus.configureInputRegisters(array_input_registers, num_input_registers);

  Serial.println("init() completed.");
}

void loop()
{
  bool a = modbus.poll();
  Serial.println("Content of holding registers:");
  Serial.println(array_holding_registers[0]);
  Serial.println(array_holding_registers[1]);
  Serial.println(array_holding_registers[2]);
  Serial.println(array_holding_registers[3]);
  Serial.println("Content of input registers:");
  Serial.println(array_input_registers[0]);
  Serial.println(array_input_registers[1]);
  Serial.println(array_input_registers[2]);
  Serial.println(array_input_registers[3]);
  Serial.println(array_input_registers[4]);
  Serial.println();
    
  delay(1000);
  

    
}
