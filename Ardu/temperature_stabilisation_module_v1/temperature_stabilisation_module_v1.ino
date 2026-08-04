
// RS485
// We use the official arduino repo:
//https://github.com/CMB27/ModbusRTUSlave/tree/main/examples/ModbusRTUSlaveExample
//https://github.com/CMB27/ModbusSlaveLogic/tree/main/src
#include <ModbusRTUSlave.h>
#include <SoftwareSerial.h>
#include <SPI.h>
#include "Adafruit_MAX31855.h"
#include <Servo.h>

// RS485 stuff
#define RS485_TX 14   // Serial 3's TX
#define RS485_RX 15   // Serial 3's Rx 
#define SLAVE_ADDRESS 5
#define SLAVE_BAUD_RATE 9600
#define SLAVE_SERIAL_CONFIG SERIAL_8N1
#define dePin 48   // pinsDE and RE on the MAX485 module are shorted.
#define LED_pin 13

// Thermocouple's SPI stuff:
#define MAXDO   50    // MISO of Mega
#define MAXCLK  52    // SCLK of Mega
#define MAXCS_1   28   // Chip select pin for sensor 1
#define MAXCS_2   30   // Chip select pin for sensor 2
#define MAXCS_3   36   // Chip select pin for sensor 3
#define MAXCS_4   38   // Chip select pin for sensor 4
#define MAXCS_5   44   // Chip select pin for sensor 5
#define MAXCS_6   42   // Chip select pin for sensor 6
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

ModbusRTUSlave modbus(Serial3, dePin);       // Create a modbus object that uses the software serial port.

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

void setup() {
  // Default serial comm for debugging
  Serial.begin(9600);
  Serial.println("Temperature stabilisation module");

  pinMode(LED_pin, OUTPUT);

  servo_1.attach(8);
  servo_2.attach(9);
  servo_3.attach(10);
  servo_4.attach(11);

  // Using Serial 3 for RS485 communication
  Serial3.begin(9600);
  modbus.begin(SLAVE_ADDRESS, SLAVE_BAUD_RATE, SLAVE_SERIAL_CONFIG);  // Slave address = 1, Baud rate = 9600, Serial parameters = 8bit, no parity, 1 stop bit.
  modbus.configureCoils(array_coils, num_coils);
  modbus.configureDiscreteInputs(array_discrete_inputs, num_discrete_inputs);
  modbus.configureHoldingRegisters(array_holding_registers, num_holding_registers);
  modbus.configureInputRegisters(array_input_registers, num_input_registers);

  init_thermocouples();
}

void loop() {

  bool a = modbus.poll();
  digitalWrite(LED_pin, array_coils[0]);

  servo_1.writeMicroseconds(1000);
  servo_2.writeMicroseconds(1000);
  servo_3.writeMicroseconds(1000);
  servo_4.writeMicroseconds(1000);
  delay(1000);

  servo_1.writeMicroseconds(2000);
  servo_2.writeMicroseconds(2000);
  servo_3.writeMicroseconds(2000);
  servo_4.writeMicroseconds(2000);
  delay(1000);

  //  get_temperatures();

}

void init_thermocouples()
{
  // wait for MAX chip to stabilize
  delay(500);
  Serial.print("Sensor 1: Initializing sensor ...");
  if (!thermocouple_1.begin()) {
    Serial.println("Sensor 1: ERROR.");
    while (1) delay(10);
  }
  Serial.println("Sensor 1: initalised.");

  delay(500);
  Serial.print("Sensor 2: Initializing sensor ...");
  if (!thermocouple_2.begin()) {
    Serial.println("Sensor 2: ERROR.");
    while (1) delay(10);
  }
  Serial.println("Sensor 2: initalised.");

  // wait for MAX chip to stabilize
  delay(500);
  Serial.print("Sensor 3: Initializing sensor ...");
  if (!thermocouple_3.begin()) {
    Serial.println("Sensor 3: ERROR.");
    while (1) delay(10);
  }
  Serial.println("Sensor 3: initalised.");

  delay(500);
  Serial.print("Sensor 4: Initializing sensor ...");
  if (!thermocouple_4.begin()) {
    Serial.println("Sensor 4: ERROR.");
    while (1) delay(10);
  }
  Serial.println("Sensor 4: initalised.");

  // wait for MAX chip to stabilize
  delay(500);
  Serial.print("Sensor 5: Initializing sensor ...");
  if (!thermocouple_5.begin()) {
    Serial.println("Sensor 5: ERROR.");
    while (1) delay(10);
  }
  Serial.println("Sensor 5: initalised.");

  delay(500);
  Serial.print("Sensor 6: Initializing sensor ...");
  if (!thermocouple_6.begin()) {
    Serial.println("Sensor 6: ERROR.");
    while (1) delay(10);
  }
  Serial.println("Sensor 6: initalised.");

}

void get_temperatures()
{

  // SENSOR 1
  c_1 = thermocouple_1.readCelsius();
  if (isnan(c_1)) {
    Serial.println("Sensor 1 : fault(s) detected!");
    uint8_t e = thermocouple_1.readError();
    if (e & MAX31855_FAULT_OPEN) Serial.println("Sensor 1: FAULT: thermocouple is open - no connections.");
    if (e & MAX31855_FAULT_SHORT_GND) Serial.println("Sensor 1: FAULT: thermocouple is short-circuited to GND.");
    if (e & MAX31855_FAULT_SHORT_VCC) Serial.println("Sensor 1: FAULT: thermocouple is short-circuited to VCC.");
  } else {
    //     Serial.print("C = ");
    // Serial.print("Sensor 1 ");
    Serial.print(c_1);
    Serial.print(",");    // separator for serial plotter
  }

  // SENSOR 2
  c_2 = thermocouple_2.readCelsius();
  if (isnan(c_2)) {
    Serial.println("Sensor 2 : fault(s) detected!");
    uint8_t e = thermocouple_1.readError();
    if (e & MAX31855_FAULT_OPEN) Serial.println("Sensor 2: FAULT: thermocouple is open - no connections.");
    if (e & MAX31855_FAULT_SHORT_GND) Serial.println("Sensor 2: FAULT: thermocouple is short-circuited to GND.");
    if (e & MAX31855_FAULT_SHORT_VCC) Serial.println("Sensor 2: FAULT: thermocouple is short-circuited to VCC.");
  } else {
    //     Serial.print("C = ");
    // Serial.print("Sensor 2 ");
    Serial.print(c_2);
    Serial.print(",");    // separator for serial plotter
  }

  // SENSOR 3
  c_3 = thermocouple_3.readCelsius();
  if (isnan(c_3)) {
    Serial.println("Sensor 3 : fault(s) detected!");
    uint8_t e = thermocouple_3.readError();
    if (e & MAX31855_FAULT_OPEN) Serial.println("Sensor 3: FAULT: thermocouple is open - no connections.");
    if (e & MAX31855_FAULT_SHORT_GND) Serial.println("Sensor 3: FAULT: thermocouple is short-circuited to GND.");
    if (e & MAX31855_FAULT_SHORT_VCC) Serial.println("Sensor 3: FAULT: thermocouple is short-circuited to VCC.");
  } else {
    //     Serial.print("C = ");
    // Serial.print("Sensor 3 ");
    Serial.print(c_3);
    Serial.print(",");    // separator for serial plotter
  }

  // SENSOR 4
  c_4 = thermocouple_4.readCelsius();
  if (isnan(c_4)) {
    Serial.println("Sensor 4 : fault(s) detected!");
    uint8_t e = thermocouple_4.readError();
    if (e & MAX31855_FAULT_OPEN) Serial.println("Sensor 4: FAULT: thermocouple is open - no connections.");
    if (e & MAX31855_FAULT_SHORT_GND) Serial.println("Sensor 4: FAULT: thermocouple is short-circuited to GND.");
    if (e & MAX31855_FAULT_SHORT_VCC) Serial.println("Sensor 4: FAULT: thermocouple is short-circuited to VCC.");
  } else {
    //     Serial.print("C = ");
    // Serial.print("Sensor 4 ");
    Serial.print(c_4);
    Serial.print(",");    // separator for serial plotter
  }

  // SENSOR 5
  c_5 = thermocouple_5.readCelsius();
  if (isnan(c_5)) {
    Serial.println("Sensor 5 : fault(s) detected!");
    uint8_t e = thermocouple_5.readError();
    if (e & MAX31855_FAULT_OPEN) Serial.println("Sensor 5: FAULT: thermocouple is open - no connections.");
    if (e & MAX31855_FAULT_SHORT_GND) Serial.println("Sensor 5: FAULT: thermocouple is short-circuited to GND.");
    if (e & MAX31855_FAULT_SHORT_VCC) Serial.println("Sensor 5: FAULT: thermocouple is short-circuited to VCC.");
  } else {
    //     Serial.print("C = ");
    // Serial.print("Sensor 5 ");
    Serial.print(c_5);
    Serial.print(",");    // separator for serial plotter
  }

  // SENSOR 6
  c_6 = thermocouple_6.readCelsius();
  if (isnan(c_6)) {
    Serial.println("Sensor 6 : fault(s) detected!");
    uint8_t e = thermocouple_6.readError();
    if (e & MAX31855_FAULT_OPEN) Serial.println("Sensor 6: FAULT: thermocouple is open - no connections.");
    if (e & MAX31855_FAULT_SHORT_GND) Serial.println("Sensor 6: FAULT: thermocouple is short-circuited to GND.");
    if (e & MAX31855_FAULT_SHORT_VCC) Serial.println("Sensor 6: FAULT: thermocouple is short-circuited to VCC.");
  } else {
    //     Serial.print("C = ");
    // Serial.print("Sensor 6 ");
    Serial.println(c_6);
    //    Serial.print(",");    // separator for serial plotter
  }
}
