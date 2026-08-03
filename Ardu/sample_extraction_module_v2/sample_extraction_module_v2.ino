// Arduino UNO over RS485 to control:
//   HX711: Load cell amplifier and measure weight of fluid in realtime. The calibration factor needs to be precomputed. see HX711_load_call.ino
//   DHT22: Temperature and Humidity sensor over one wire.
//   BTN8982A Infineon Motor driver to drive two unidirectional Brushed DC motors for the peristatic pumps and current sense.

#include <avr/wdt.h>
#include "Grove_Temperature_And_Humidity_Sensor.h"
#include "HX711.h"

// RS485
// We use the official arduino repo:
//https://github.com/CMB27/ModbusRTUSlave/tree/main/examples/ModbusRTUSlaveExample
//https://github.com/CMB27/ModbusSlaveLogic/tree/main/src

#include <ModbusRTUSlave.h>
#include <SoftwareSerial.h>

#define RS485_TX_PIN 8
#define RS485_RX_PIN 9
#define SLAVE_ADDRESS 10
#define SLAVE_BAUD_RATE 9600 
#define SLAVE_SERIAL_CONFIG SERIAL_8N1
#define DE_PIN 10   // pinsDE and RE on the MAX485 module are shorted.
#define RELAY_PIN 4

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

SoftwareSerial RS485_serial(RS485_RX_PIN, RS485_TX_PIN);  // Create a serial port with the software serial pins.
ModbusRTUSlave modbus(RS485_serial, DE_PIN);       // Create a modbus object that uses the software serial port.

/*
  The array_coils[i] is used either as a state or as a trigger.
  In some case like in set_motor_1(), it is used as a state.
  In function get_sample_weight(), it is used as a trigger.  
  
  NOTE:
  Modbus is natively uin16_t, but TX and RX of negative integers is just intepretation with 2's complement.
  In Pymodbus we convert the uint16_t back to int16_t values.
  So: array_holding_registers and array_input_registers can hold negative numbers.
 *** For float, we need to scale and divide to obtain a floating point value in Arduino and Python.
  

*/
//  Coil_0  Enable module/ Emergency Power OFF
//  Coil_1  Get humidity & Temperature
//  Coil_2  Get sample weight (1 value, not avg) 
//  Coil_3  Enable pump 1
//  Coil_4  Enable pump 2
//  Coil_5  Tare load cell
//  Coil_6  Reset Slave

const uint8_t num_coils = 7;                        // Number of digital outputs, W only
bool array_coils[num_coils] = {0, 0, 0, 0, 0, 0, 0};   // array holding all the digital outputs, W only

// Discrete Inputs = Digital inputs/reads, Eg: Switches
//  Discrete_input_0  Humidity & Temperature sensor error
//  Discrete_input_1  NA
const uint8_t num_discrete_inputs = 2;              // Number of digital inputs, R only
bool array_discrete_inputs[num_discrete_inputs] = {false, false};

//  Holding registers = 16bit variable values, R+W
//  Holding_register_0  Set pump 1 flow rate, range:0:100
//  Holding_register_1  Set pump 2 flow rate, range:0:100
//  Holding_register_2  NA
//  Holding_register_3  NA
const uint8_t num_holding_registers = 4;            // Number of holding registers, R + W

int16_t array_holding_registers[num_holding_registers] = {0, 0, 0, 0}; // Array holding N holding registers. R+W
// The brakes are NOT ON/OFF but are from 0 to 400, so we use a holding register to implement brakes

//  Input_registers = 16bit variable values, R only.
//  Input_register_0  Humidity (RH)
//  Input_register_1  Temperature (deg C)
//  Input_register_2  Weight (grams)
//  Input_register_3  Un-tared weight(grams)
//  Input_register_4  Motor 1 current sense (mA)
//  Input_register_5  Motor 2 current sense (mA)
const uint8_t num_input_registers = 6;              // Number of input registers, R only
int16_t array_input_registers[num_input_registers] = {0, 0, 0, 0, 0, 0};  // Array for input registers, R only.

void setup()
{
  Serial.begin(9600);
  Serial.println("\nSlave 10; Sample extraction module");
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

  get_untared_weight(); // Get the value of the un-tared weight when the code initalises.
  // scale.tare();  // All readings will thus be tared. This is only done from master/client

  // BTN8289A pins
  pinMode(pin_BTN_IN_1, OUTPUT);
  pinMode(pin_BTN_IN_2, OUTPUT);
  pinMode(pin_BTN_INH_1, OUTPUT);
  pinMode(pin_BTN_INH_2, OUTPUT);
  digitalWrite(pin_BTN_INH_1, HIGH);  // Enable Half bridge-1
  digitalWrite(pin_BTN_INH_2, HIGH);  // Enable Half bridge-2

  pinMode(A0, INPUT); // Current sense for Half bridge-1 on pin A0
  pinMode(A1, INPUT); // Current sense for Half bridge-2 on pin A1
  Serial.println("Initalised Motor Driver BTN8982A");

  // A GPIO that drives a relay module ON/OFF
  pinMode(RELAY_PIN, OUTPUT);

  // DHT22
  Wire.begin();
  dht.begin();
  Serial.println("Initalised DHT22");

  Serial.println("init() completed.");
}

void loop()
{
  bool a = modbus.poll();
  Serial.println("Modbus poll = ");
  Serial.println(a);

  get_temp_hum();

  get_sample_weight();

  set_motor_1(array_holding_registers[0]);

  set_motor_2(array_holding_registers[1]);

  //tare_load_cell();

  reboot();
}

// Reading temperature or humidity takes about 250 milliseconds!
// Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
// Multiplying the humidity and temperature values by a scale of 10 since modbus cannot handle floats.
// The scaled values must divided by 10 to obtain a floating point value
void get_temp_hum() {

  // if Coil_1 : Get DHT22 (Humidity & Temperature)
  if (array_coils[1] == 1)
  {
    if (!dht.readTempAndHumidity(temp_hum_val))
    {
      Serial.print("Humidity: ");
      array_input_registers[0] = temp_hum_val[0] * 10;
      humidity = array_input_registers[0];
      Serial.print(humidity);
      Serial.print(" %\t");
      Serial.print("Temperature: ");

      array_input_registers[1] = temp_hum_val[1] * 10;
      temperature = array_input_registers[1];
      Serial.print(temperature);
      Serial.println(" *C");
      array_discrete_inputs[0] = 0;   // No error in obtaining Humidity and temperature, sensor OK
    }
    else
    {
      array_discrete_inputs[0] = 1;   // Error in obtaining Humidity and temperature, sensor NOT OK
      Serial.println("Failed to get temprature and humidity value.");
    }
  }
}


void get_untared_weight()
{
  weight = scale.get_units(1);  // Get average of 5 values
  Serial.print("Un-tared weight (units) = ");
  Serial.println(weight, 1);
  array_input_registers[3] = weight * 10;
}

void get_sample_weight()
{
  if (array_coils[2] == 1)
  {
    weight = scale.get_units(1);  // Get average of 5 values
    Serial.print("Weight (units) = ");
    Serial.println(weight, 1);
    array_input_registers[2] = weight * 10;
    array_coils[2] = 0;   // Reset the coil list value until master triggers it.
  }
}


void tare_load_cell()
{
  if (array_coils[5] == 1)
  {
    scale.tare();         // All readings will thus be tared.
    array_coils[5] = 0;   // Reset it and only execute the function if the master enables it.
  }
}

void set_motor_1(int value)
{
  if (array_coils[3] == 1)
  {
    analogWrite(pin_BTN_IN_1, value);
    array_input_registers[4] = analogRead(A0);    // Current sense
  }
  else
  {
    analogWrite(pin_BTN_IN_1, 0);
    array_input_registers[4] = analogRead(A0);    // Current sense
  }
  //
  //  Serial.print("Current sense motor 1 = ");
  //  Serial.println(array_input_registers[4]);
}

// Infuse
void set_motor_2(int value)
{
  if (array_coils[4] == 1)
  {
    analogWrite(pin_BTN_IN_2, value);
    array_input_registers[5] = analogRead(A1);    // Current sense
  }
  else
  {
    analogWrite(pin_BTN_IN_2, 0);
    array_input_registers[5] = analogRead(A1);    // Current sense

  }
  //  Serial.print("Current sense motor 2 = ");
  //  Serial.println(array_input_registers[5]);
}

// Enable the entire module by powering ON/OFF using a relay.
void enable_module()
{
  if (array_coils[0] == 1)
    digitalWrite(RELAY_PIN, HIGH );
  else if (array_coils[0] == 0)
    digitalWrite(RELAY_PIN, LOW );
}



// Software reset
// https://forum.arduino.cc/t/soft-reset-and-arduino/367284/7
void reboot() {
  if (array_coils[6] == 1)
  {
    Serial.println("Rebooting...");
    delay(100);
    array_coils[6] = 0;
    wdt_disable();        // Disable watchdog to clear existing configurations
    wdt_enable(WDTO_15MS); // Enable watchdog with a ultra-short 15ms timeout
    while (1) {}          // Enter infinite loop to let the timer expire and force reset
  }
}
