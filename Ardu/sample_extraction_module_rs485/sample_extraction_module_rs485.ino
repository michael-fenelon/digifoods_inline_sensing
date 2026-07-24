// Arduino UNO ove RS485 to control:
//   HX711: Load cell amplifier and measure weight of fluid in realtime. The calibration factor needs to be precomputed. see HX711_load_call.ino
//   DHT22: Temperature and Humidity sensor over one wire.
//   BTN8982A Infineon Motor driver to drive two unidirectional Brushed DC motors for the peristatic pumps.

#include "Grove_Temperature_And_Humidity_Sensor.h"
#include "HX711.h"

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
#define dePin 10   // pinsDE and RE on the MAX485 module are shorted.

// HX711 Load cell amplifier
const int pin_LOADCELL_DOUT = 7;
const int pin_LOADCELL_SCK = 6;
float calib_factor = 169240.0 / 246.37;  // 686.9342
float weight = 0.0;                      // (grams), Load cell's capacity upto 1Kg.
HX711 scale;                             // Object of type HX711

// For Infineon BTN8982TA Motor Shield.
const int pin_BTN_IN_1 = 3;    //Input bridge 1, Defines whether high- or low side switch is activated
const int pin_BTN_IN_2 = 11;   //Input bridge 2, Defines whether high- or low side switch is activated
const int pin_BTN_INH_1 = 12;  // Inhibit bridge 1, When set to low device goes in sleep mode
const int pin_BTN_INH_2 = 13;  // Inhibit bridge 2, When set to low device goes in sleep mode
const int pin_BTN_IS_1 = A0;   // Current sense
const int pin_BTN_IS_2 = A1;   // Current sense

// DHT22 Temperature - Humidity Sensor
#define DHTTYPE DHT22  // DHT 22  (AM2302)
const int pin_DHT = 5;
DHT dht(pin_DHT, DHTTYPE);  //   DHT11 DHT21 DHT22
float temp_hum_val[2] = { 0 };
float humidity = 0.0;
float temperature = 0.0;

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

  // HX711:
  // Initiate
  scale.begin(pin_LOADCELL_DOUT, pin_LOADCELL_SCK);
  Serial.println("Initalised Load-Cell HX711");
  scale.set_scale(calib_factor);
  scale.tare();  // All readings will thus be tared.

  // BTN8289A pins
  pinMode(pin_BTN_IN_1, OUTPUT);
  pinMode(pin_BTN_IN_2, OUTPUT);
  pinMode(pin_BTN_INH_1, OUTPUT);
  pinMode(pin_BTN_INH_2, OUTPUT);
  digitalWrite(pin_BTN_INH_1, HIGH);  // Enable Half bridge-1
  digitalWrite(pin_BTN_INH_2, HIGH);  // Enable Half bridge-2
  Serial.println("Initalised Motor Driver BTN8982A");

  // // DHT22
  Wire.begin();
  dht.begin();
  Serial.println("Initalised DHT22");

  Serial.println("init() completed.");
}

void loop()
{
  bool a = modbus.poll();

  //get_temp_hum();
  //get_weight();

  //set_motor_1(0);

  set_motor_2(array_holding_registers[0]);

  //  // We need to call set##Speed() before set##Brake() to avoid a glitch.
  //  // Glitch: if we call set##Brake() before set##Speed() the motors still move a bit/or jerk even if the brake is enable.
  //  // This is weird, this is eliminated when we call set##Speed() before set##Brake().
  //
  //  // Update holding registers with client's values
  //  // Set motor speeds
  //  md.setM1Speed(array_holding_registers[0]);
  //  md.setM2Speed(array_holding_registers[1]);
  //
  //  // Update coils from client
  //  // Set/Enable/Disable brake
  //  if (array_coils[0] == 1)
  //    md.setM1Brake(array_holding_registers[2]);
  //
  //  if (array_coils[1] == 1)
  //    md.setM2Brake(array_holding_registers[3]);
  //
  //  // Update discrete inputs/ switches/ status of slave
  //  // Get faults if any
  //  array_discrete_inputs[0] = md.getM1Fault();
  //  array_discrete_inputs[1] = md.getM2Fault();
  //
  //
  //
  //  // Update input registers for client to read
  //  // Get current draw from motors.
  //  array_input_registers[0] = md.getM1CurrentMilliamps();
  //  array_input_registers[1] = md.getM2CurrentMilliamps();
  //
  //  //  Serial.println(array_holding_registers[0]);

}



// Reading temperature or humidity takes about 250 milliseconds!
// Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
void get_temp_hum() {
  if (!dht.readTempAndHumidity(temp_hum_val)) {
    Serial.print("Humidity: ");
    humidity = temp_hum_val[0];
    Serial.print(humidity);
    Serial.print(" %\t");
    Serial.print("Temperature: ");
    temperature = temp_hum_val[1];
    Serial.print(temperature);
    Serial.println(" *C");
  } else {
    Serial.println("Failed to get temprature and humidity value.");
  }
}

void get_weight() {
  weight = scale.get_units(5);  // Get average of 5 values
  Serial.print("Weight (units) = ");
  Serial.println(weight, 1);
}

// Withdraw
void set_motor_1(int value) {
  analogWrite(pin_BTN_IN_1, value);
}

// Infuse
void set_motor_2(int value) {
  analogWrite(pin_BTN_IN_2, value);
}
