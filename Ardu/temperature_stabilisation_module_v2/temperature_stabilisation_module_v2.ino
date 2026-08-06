
// RS485
// We use the official arduino repo:
// https://github.com/CMB27/ModbusRTUSlave/tree/main/examples/ModbusRTUSlaveExample
// https://github.com/CMB27/ModbusSlaveLogic/tree/main/src
#include <avr/wdt.h>
#include <ModbusRTUSlave.h>
#include <SoftwareSerial.h>
#include <SPI.h>
#include "Adafruit_MAX31855.h"
#include <Servo.h>

// RS485 stuff
#define RS485_TX 14 // Serial 3's TX
#define RS485_RX 15 // Serial 3's Rx
#define SLAVE_ADDRESS 5
#define SLAVE_BAUD_RATE 9600
#define SLAVE_SERIAL_CONFIG SERIAL_8N1
#define DE_PIN 48 // pinsDE and RE on the MAX485 module are shorted.
#define LED_pin 13

// Thermocouple's SPI stuff:
#define MAXDO 50   // MISO of Mega
#define MAXCLK 52  // SCLK of Mega
#define MAXCS_1 28 // Chip select pin for sensor 1
#define MAXCS_2 30 // Chip select pin for sensor 2
#define MAXCS_3 36 // Chip select pin for sensor 3
#define MAXCS_4 38 // Chip select pin for sensor 4
#define MAXCS_5 42 // Chip select pin for sensor 5
#define MAXCS_6 44 // Chip select pin for sensor 6
Adafruit_MAX31855 thermocouple_1(MAXCLK, MAXCS_1, MAXDO);
Adafruit_MAX31855 thermocouple_2(MAXCLK, MAXCS_2, MAXDO);
Adafruit_MAX31855 thermocouple_3(MAXCLK, MAXCS_3, MAXDO);
Adafruit_MAX31855 thermocouple_4(MAXCLK, MAXCS_4, MAXDO);
Adafruit_MAX31855 thermocouple_5(MAXCLK, MAXCS_5, MAXDO);
Adafruit_MAX31855 thermocouple_6(MAXCLK, MAXCS_6, MAXDO);

// globals
double c_1 = 0.0;
double c_2 = 0.0;
double c_3 = 0.0;
double c_4 = 0.0;
double c_5 = 0.0;
double c_6 = 0.0;

// Servos for valves
Servo servo_1;
Servo servo_2;
Servo servo_3;
Servo servo_4;
Servo servo_5;
Servo servo_6;

// command position of each servo.
uint16_t servo_1_cmd_pos = 0;
uint16_t servo_2_cmd_pos = 0;
uint16_t servo_3_cmd_pos = 0;
uint16_t servo_4_cmd_pos = 0;
uint16_t servo_5_cmd_pos = 0;
uint16_t servo_6_cmd_pos = 0;

// Current position of each servo.
uint16_t servo_1_cur_pos = 0;
uint16_t servo_2_cur_pos = 0;
uint16_t servo_3_cur_pos = 0;
uint16_t servo_4_cur_pos = 0;
uint16_t servo_5_cur_pos = 0;
uint16_t servo_6_cur_pos = 0;

ModbusRTUSlave modbus(Serial3, DE_PIN); // Create a modbus object that uses the software serial port.

//  Coils = Digital outputs/writes, Eg: LED, Relays
//  Coil_0  Enable module/ Emergency Power OFF
//  Coil_1  Water relay ON/OFF
//  Coil_2  Get valve positions
//  Coil_3  Set valve positions
//  Coil_4  Get temperatures
//  Coil_5  Reset Slave
//NOTE: The array size from python and arduino needs to be identical, if not the array_* will not update and will remain with 0s
const uint8_t num_coils = 6;                      // Number of digital outputs, W only
bool array_coils[num_coils] = {0, 0, 0, 0, 0, 0}; // array holding all the digital outputs, W only

// Discrete Inputs = Digital inputs/reads, Eg: Switches
//NOTE: The array size from python and arduino needs to be identical, if not the array_* will not update and will remain with 0s
const uint8_t num_discrete_inputs = 1; // Number of digital inputs, R only
bool array_discrete_inputs[num_discrete_inputs] = {false};

//  Holding registers = 16bit variable values, R+W
//  Holding_register_0  NA
//  Holding_register_1  Set valve 1 (A) position, pulse:900:1900
//  Holding_register_2  Set valve 2 (B) position, pulse:900:1900
//  Holding_register_3  Set valve 3 (A) position, pulse:900:1900
//  Holding_register_4  Set valve 4 (B) position, pulse:900:1900
//  Holding_register_5  Set valve 5 position, pulse:900:1900
//  Holding_register_6  Set valve 6 position, pulse:900:1900
//  Holding_register_7  Set water cut off temperature, range:20:50:0.1
//  Holding_register_8  Set sample cut off temperature, range:20:50:0.1
//  Holding_register_9  Set water pump, range:0:100
//  Holding_register_10 Set sample pump, range:0:100
//  Holding_register_11 NA
//  Holding_register_12 NA
//NOTE: The array size from python and arduino needs to be identical, if not the array_* will not update and will remain with 0s
const uint8_t num_holding_registers = 13;               // Number of holding registers, R + W
int16_t array_holding_registers[num_holding_registers]; //= {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // Array holding N holding registers. R+W

//  Input_registers = 16bit variable values, R only.
//  Input_register_0  NA
//  Input_register_1  Valve 1 position
//  Input_register_2  Valve 2 position
//  Input_register_3  Valve 3 position
//  Input_register_4  Valve 4 position
//  Input_register_5  Valve 5 position
//  Input_register_6  Valve 6 position
//  Input_register_7  Temperature 1 :
//  Input_register_8  Temperature 2 :
//  Input_register_9  Temperature 3 :
//  Input_register_10 Temperature 4 :
//  Input_register_11 Temperature 5 :
//  Input_register_12 Temperature 6 :
//NOTE: The array size from python and arduino needs to be identical, if not the array_* will not update and will remain with 0s
const uint8_t num_input_registers = 13;                                                                    // Number of input registers, R only
int16_t array_input_registers[num_input_registers] = { -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1}; // Array for input registers, R only.

void setup()
{
  // Default serial comm for debugging
  Serial.begin(9600);
  Serial.println("Temperature stabilisation module");

  servo_1.attach(8);
  servo_2.attach(9);
  servo_3.attach(10);
  servo_4.attach(11);
  servo_5.attach(12);
  servo_6.attach(13);

  // Using Serial 3 for RS485 communication
  Serial3.begin(9600);
  modbus.begin(SLAVE_ADDRESS, SLAVE_BAUD_RATE, SLAVE_SERIAL_CONFIG); // Slave address = 1, Baud rate = 9600, Serial parameters = 8bit, no parity, 1 stop bit.
  modbus.configureCoils(array_coils, num_coils);
  modbus.configureDiscreteInputs(array_discrete_inputs, num_discrete_inputs);
  modbus.configureHoldingRegisters(array_holding_registers, num_holding_registers);
  modbus.configureInputRegisters(array_input_registers, num_input_registers);

  init_thermocouples();
  Serial.println("Init completed");
}

void loop()
{
  bool a = modbus.poll();
  // Serial.println(a);  // debug

  //get_valve_positions();

  set_valve_positions();

  get_temperatures();

  //reset_slave();

  //print_array_coils();
  //print_array_discrete_inputs();
  //print_array_holding_registers();
  //print_array_input_registers();
}

// Debug prints for registers.
void print_array_coils()
{
  Serial.println("Coils: array_coils");
  for (int i = 0; i <= num_coils; i++)
  {
    Serial.println(array_coils[i]);
  }
}

void print_array_discrete_inputs()
{
  Serial.println("Discrete inputs: array_discrete_inputs");
  for (int i = 0; i <= num_discrete_inputs; i++)
  {
    Serial.println(array_discrete_inputs[i]);
  }
}

void print_array_holding_registers()
{
  Serial.println("Holding registers: array_holding_registers");
  for (int i = 0; i <= num_holding_registers; i++)
  {
    Serial.println(array_holding_registers[i]);
  }
}


void print_array_input_registers()
{
  Serial.println("Input registers: array_input_registers");
  for (int i = 0; i <= num_input_registers; i++)
  {
    Serial.println(array_input_registers[i]);
  }
}

// Get status of valves.
// We don't need to set A0---An as INPUT pins, it is overriden inside analogRead()
void get_valve_positions()
{
  if (array_coils[2] == 1)
  {
    array_coils[2] = 0; // Reset the flag until master changes the value.
    servo_1_cur_pos = analogRead(A0);
    servo_2_cur_pos = analogRead(A1);
    servo_3_cur_pos = analogRead(A2);
    servo_4_cur_pos = analogRead(A3);
    servo_5_cur_pos = analogRead(A4);
    servo_6_cur_pos = analogRead(A5);
  }
}

void set_valve_positions()
{
  if (array_coils[3] == 1)
  {
    servo_1.writeMicroseconds(array_holding_registers[1]);
    servo_2.writeMicroseconds(array_holding_registers[2]);
    servo_3.writeMicroseconds(array_holding_registers[3]);
    servo_4.writeMicroseconds(array_holding_registers[4]);
    //servo_5.writeMicroseconds(array_holding_registers[5]);
    //servo_6.writeMicroseconds(array_holding_registers[6]);

    //delay(500);
    //array_coils[3] = 0; // Reset the flag until master changes the value. This seems to cause the servos to only move every 2nd iteration.
  }
}

void init_thermocouples()
{
  // wait for MAX chip to stabilize
  delay(500);
  Serial.print("Sensor 1: Initializing sensor ...");
  if (!thermocouple_1.begin())
  {
    Serial.println("Sensor 1: ERROR.");
    while (1)
      delay(10);
  }
  Serial.println("Sensor 1: initalised.");

  delay(500);
  Serial.print("Sensor 2: Initializing sensor ...");
  if (!thermocouple_2.begin())
  {
    Serial.println("Sensor 2: ERROR.");
    while (1)
      delay(10);
  }
  Serial.println("Sensor 2: initalised.");

  // wait for MAX chip to stabilize
  delay(500);
  Serial.print("Sensor 3: Initializing sensor ...");
  if (!thermocouple_3.begin())
  {
    Serial.println("Sensor 3: ERROR.");
    while (1)
      delay(10);
  }
  Serial.println("Sensor 3: initalised.");

  delay(500);
  Serial.print("Sensor 4: Initializing sensor ...");
  if (!thermocouple_4.begin())
  {
    Serial.println("Sensor 4: ERROR.");
    while (1)
      delay(10);
  }
  Serial.println("Sensor 4: initalised.");

  // wait for MAX chip to stabilize
  delay(500);
  Serial.print("Sensor 5: Initializing sensor ...");
  if (!thermocouple_5.begin())
  {
    Serial.println("Sensor 5: ERROR.");
    while (1)
      delay(10);
  }
  Serial.println("Sensor 5: initalised.");

  delay(500);
  Serial.print("Sensor 6: Initializing sensor ...");
  if (!thermocouple_6.begin())
  {
    Serial.println("Sensor 6: ERROR.");
    while (1)
      delay(10);
  }
  Serial.println("Sensor 6: initalised.");
}

void get_temperatures()
{
  if (array_coils[4] == 1)
  {
    array_coils[4] = 0; // Reset the flag until master changes the value.
    // SENSOR 1
    c_1 = thermocouple_1.readCelsius();
    if (isnan(c_1))
    {
      Serial.println("Sensor 1 : fault(s) detected!");
      uint8_t e = thermocouple_1.readError();
      if (e & MAX31855_FAULT_OPEN)
        Serial.println("Sensor 1: FAULT: thermocouple is open - no connections.");
      if (e & MAX31855_FAULT_SHORT_GND)
        Serial.println("Sensor 1: FAULT: thermocouple is short-circuited to GND.");
      if (e & MAX31855_FAULT_SHORT_VCC)
        Serial.println("Sensor 1: FAULT: thermocouple is short-circuited to VCC.");
    }
    else
    {
      Serial.print("Sensor 1 ");
      array_input_registers[7] = c_1 * 10;
      Serial.print(c_1);
      Serial.print(","); // separator for serial plotter
    }

    // SENSOR 2
    c_2 = thermocouple_2.readCelsius();
    if (isnan(c_2))
    {
      Serial.println("Sensor 2 : fault(s) detected!");
      uint8_t e = thermocouple_1.readError();
      if (e & MAX31855_FAULT_OPEN)
        Serial.println("Sensor 2: FAULT: thermocouple is open - no connections.");
      if (e & MAX31855_FAULT_SHORT_GND)
        Serial.println("Sensor 2: FAULT: thermocouple is short-circuited to GND.");
      if (e & MAX31855_FAULT_SHORT_VCC)
        Serial.println("Sensor 2: FAULT: thermocouple is short-circuited to VCC.");
    }
    else
    {
      Serial.print("Sensor 2 ");
      array_input_registers[8] = c_2 * 10;
      Serial.print(c_2);
      Serial.print(","); // separator for serial plotter
    }

    // SENSOR 3
    c_3 = thermocouple_3.readCelsius();
    if (isnan(c_3))
    {
      Serial.println("Sensor 3 : fault(s) detected!");
      uint8_t e = thermocouple_3.readError();
      if (e & MAX31855_FAULT_OPEN)
        Serial.println("Sensor 3: FAULT: thermocouple is open - no connections.");
      if (e & MAX31855_FAULT_SHORT_GND)
        Serial.println("Sensor 3: FAULT: thermocouple is short-circuited to GND.");
      if (e & MAX31855_FAULT_SHORT_VCC)
        Serial.println("Sensor 3: FAULT: thermocouple is short-circuited to VCC.");
    }
    else
    {
      Serial.print("Sensor 3 ");
      array_input_registers[9] = c_3 * 10;
      Serial.print(c_3);
      Serial.print(","); // separator for serial plotter
    }

    // SENSOR 4
    c_4 = thermocouple_4.readCelsius();
    if (isnan(c_4))
    {
      Serial.println("Sensor 4 : fault(s) detected!");
      uint8_t e = thermocouple_4.readError();
      if (e & MAX31855_FAULT_OPEN)
        Serial.println("Sensor 4: FAULT: thermocouple is open - no connections.");
      if (e & MAX31855_FAULT_SHORT_GND)
        Serial.println("Sensor 4: FAULT: thermocouple is short-circuited to GND.");
      if (e & MAX31855_FAULT_SHORT_VCC)
        Serial.println("Sensor 4: FAULT: thermocouple is short-circuited to VCC.");
    }
    else
    {
      Serial.print("Sensor 4 ");
      array_input_registers[10] = c_4 * 10;
      Serial.print(c_4);
      Serial.print(","); // separator for serial plotter
    }

    // SENSOR 5
    c_5 = thermocouple_5.readCelsius();
    if (isnan(c_5))
    {
      Serial.println("Sensor 5 : fault(s) detected!");
      uint8_t e = thermocouple_5.readError();
      if (e & MAX31855_FAULT_OPEN)
        Serial.println("Sensor 5: FAULT: thermocouple is open - no connections.");
      if (e & MAX31855_FAULT_SHORT_GND)
        Serial.println("Sensor 5: FAULT: thermocouple is short-circuited to GND.");
      if (e & MAX31855_FAULT_SHORT_VCC)
        Serial.println("Sensor 5: FAULT: thermocouple is short-circuited to VCC.");
    }
    else
    {
      Serial.print("Sensor 5 ");
      array_input_registers[11] = c_5 * 10;
      Serial.print(c_5);
      Serial.print(","); // separator for serial plotter
    }

    // SENSOR 6
    c_6 = thermocouple_6.readCelsius();
    if (isnan(c_6))
    {
      Serial.println("Sensor 6 : fault(s) detected!");
      uint8_t e = thermocouple_6.readError();
      if (e & MAX31855_FAULT_OPEN)
        Serial.println("Sensor 6: FAULT: thermocouple is open - no connections.");
      if (e & MAX31855_FAULT_SHORT_GND)
        Serial.println("Sensor 6: FAULT: thermocouple is short-circuited to GND.");
      if (e & MAX31855_FAULT_SHORT_VCC)
        Serial.println("Sensor 6: FAULT: thermocouple is short-circuited to VCC.");
    }
    else
    {
      Serial.print("Sensor 6 ");
      array_input_registers[12] = c_6 * 10;
      Serial.println(c_6);
      //    Serial.print(",");    // separator for serial plotter
    }
  }
}

// Software reset
// https://forum.arduino.cc/t/soft-reset-and-arduino/367284/7
void reset_slave()
{
  if (array_coils[5] == 1)
  {
    Serial.println("Reseting slave...");
    delay(100);
    array_coils[5] = 0;
    wdt_disable();         // Disable watchdog to clear existing configurations
    wdt_enable(WDTO_15MS); // Enable watchdog with a ultra-short 15ms timeout
    while (1)
    {
    } // Enter infinite loop to let the timer expire and force reset
  }
}

// DUMP
/*
  void set_valve_positions()
  {
  if (array_coils[3] == 1)
  {
    array_coils[3] = 0; // Reset the flag until master changes the value.

    // Valve 1
    if (array_holding_registers[1] == 1)
    {
      servo_1.writeMicroseconds(1000);
    }
    else if (array_holding_registers[1] == 2)
    {
      servo_1.writeMicroseconds(2000);
    }

    // Valve 2
    if (array_holding_registers[2] == 1)
    {
      servo_2.writeMicroseconds(1000);
    }
    else if (array_holding_registers[2] == 2)
    {
      servo_2.writeMicroseconds(2000);
    }

    // Valve 3
    if (array_holding_registers[3] == 1)
    {
      servo_3.writeMicroseconds(1000);
    }
    else if (array_holding_registers[3] == 2)
    {
      servo_3.writeMicroseconds(2000);
    }

    // Valve 4
    if (array_holding_registers[4] == 1)
    {
      servo_4.writeMicroseconds(1000);
    }
    else if (array_holding_registers[4] == 2)
    {
      servo_4.writeMicroseconds(2000);
    }

    // Valve 5
    if (array_holding_registers[5] == 1)
    {
      servo_5.writeMicroseconds(1000);
    }
    else if (array_holding_registers[5] == 2)
    {
      servo_5.writeMicroseconds(2000);
    }

    // Valve 6
    if (array_holding_registers[6] == 1)
    {
      servo_6.writeMicroseconds(1000);
    }
    else if (array_holding_registers[6] == 2)
    {
      servo_6.writeMicroseconds(2000);
    }
  }


  //for(int i = 1, i<7, i++ )
  //{
    //  int value = 1000 * array_holding_registers[i];
      //servo_1.writeMicroseconds(value);
  //}
  }
*/
