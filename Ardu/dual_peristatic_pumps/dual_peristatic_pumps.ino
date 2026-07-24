// Info
// https://github.com/pololu/dual-vnh5019-motor-shield/tree/master

#include "DualVNH5019MotorShield.h"

/*
  Function description
  DualVNH5019MotorShield()   Default constructor, selects the default pins as connected by the motor shield.
  DualVNH5019MotorShield(unsigned char INA1, unsigned char INB1, unsigned char PWM1, unsigned char EN1DIAG1, unsigned char CS1, unsigned char INA2, unsigned char INB2, unsigned char PWM2, unsigned char EN2DIAG2, unsigned char CS2)
  Alternate constructor for shield connections remapped by user. If PWM1 and PWM2 are remapped, it will try to use analogWrite instead of timer1.

  void init()  Initialize pinModes and timer1.
  void setM1Speed(int speed) Set speed and direction for motor 1. Speed should be between -400 and 400. 400 corresponds to motor current flowing from M1A to M1B. -400 corresponds to motor current flowing from M1B to M1A. 0 corresponds to full coast.
  void setM2Speed(int speed) Set speed and direction for motor 2. Speed should be between -400 and 400. 400 corresponds to motor current flowing from M2A to M2B. -400 corresponds to motor current flowing from M2B to M2A. 0 corresponds to full coast.
  void setSpeeds(int m1Speed, int m2Speed)   Set speed and direction for motor 1 and 2.
  void setM1Brake(int brake) Set brake for motor 1. Brake should be between 0 and 400. 0 corresponds to full coast, and 400 corresponds to full brake.
  void setM2Brake(int brake) Set brake for motor 2. Brake should be between 0 and 400. 0 corresponds to full coast, and 400 corresponds to full brake.
  void setBrakes(int m1Brake, int m2Brake)   Set brake for motor 1 and 2.
  unsigned int getM1CurrentMilliamps()   Returns current reading from motor 1 in milliamps. See the notes in the "Current readings" section below.
  unsigned int getM2CurrentMilliamps()   Returns current reading from motor 2 in milliamps. See the notes in the "Current readings" section below.
  unsigned char getM1Fault() Returns 1 if there is a fault on motor driver 1, 0 if no fault.
  unsigned char getM2Fault() Returns 1 if there is a fault on motor driver 2, 0 if no fault.

*/

// RS485
// We use the official arduino repo:
//https://github.com/CMB27/ModbusRTUSlave/tree/main/examples/ModbusRTUSlaveExample
//https://github.com/CMB27/ModbusSlaveLogic/tree/main/src

#include <ModbusRTUSlave.h>
#include <SoftwareSerial.h>

#define RS485_TX 13   //1
#define RS485_RX 11   //0
#define SLAVE_ADDRESS 1
#define SLAVE_BAUD_RATE 9600
#define SLAVE_SERIAL_CONFIG SERIAL_8N1
const byte dePin = 3;   // pinsDE and RE on the MAX485 module are shorted.

SoftwareSerial RS485_serial(RS485_RX, RS485_TX);  // Create a serial port with the software serial pins.
ModbusRTUSlave modbus(RS485_serial, dePin);       // Create a modbus object that uses the software serial port.

// Coils = Digital outputs/writes, Eg: LED, Relays
const uint8_t num_coils = 4;                        // Number of digital outputs, W only
bool array_coils[num_coils] = {0, 0};                             // array holding all the digital outputs, W only

// Discrete Inputs = Digital inputs/reads, Eg: Switches
const uint8_t num_discrete_inputs = 2;              // Number of digital inputs, R only
bool array_discrete_inputs[num_discrete_inputs] = {false, false};

// Holding registers = 16bit variable values, R+W
const uint8_t num_holding_registers = 4;            // Number of holding registers, R + W
uint16_t array_holding_registers[num_holding_registers] = {0, 0, 0, 0}; // Array holding N holding registers. R+W
// The brakes are NOT ON/OFF but are from 0 to 400, so we use a holding register to implement brakes

// Input_registers = 16bit variable values, R only.
const uint8_t num_input_registers = 2;              // Number of input registers, R only
uint16_t array_input_registers[num_input_registers];      // Array for input registers, R only.

DualVNH5019MotorShield md;

void setup()
{
  Serial.begin(9600);
  Serial.println("Slave 1; VNH5019");
  RS485_serial.begin(9600);
  modbus.begin(SLAVE_ADDRESS, SLAVE_BAUD_RATE, SLAVE_SERIAL_CONFIG);  // Slave address = 1, Baud rate = 9600, Serial parameters = 8bit, no parity, 1 stop bit.
  modbus.configureCoils(array_coils, num_coils);
  modbus.configureDiscreteInputs(array_discrete_inputs, num_discrete_inputs);
  modbus.configureHoldingRegisters(array_holding_registers, num_holding_registers);
  modbus.configureInputRegisters(array_input_registers, num_input_registers);
  md.init();  // init the motor driver
  Serial.println("init() completed.");
}

void loop()
{
  bool a = modbus.poll();

  // We need to call set##Speed() before set##Brake() to avoid a glitch.
  // Glitch: if we call set##Brake() before set##Speed() the motors still move a bit/or jerk even if the brake is enable.
  // This is weird, this is eliminated when we call set##Speed() before set##Brake().

  // Update holding registers with client's values
  // Set motor speeds
  md.setM1Speed(array_holding_registers[0]);
  md.setM2Speed(array_holding_registers[1]);

  // Update coils from client
  // Set/Enable/Disable brake
  if (array_coils[0] == 1)
    md.setM1Brake(array_holding_registers[2]);

  if (array_coils[1] == 1)
    md.setM2Brake(array_holding_registers[3]);

  // Update discrete inputs/ switches/ status of slave
  // Get faults if any
  array_discrete_inputs[0] = md.getM1Fault();
  array_discrete_inputs[1] = md.getM2Fault();



  // Update input registers for client to read
  // Get current draw from motors.
  array_input_registers[0] = md.getM1CurrentMilliamps();
  array_input_registers[1] = md.getM2CurrentMilliamps();

  //  Serial.println(array_holding_registers[0]);

}
