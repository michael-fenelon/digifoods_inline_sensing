
// We use the official arduino repo:
//https://github.com/CMB27/ModbusRTUSlave/tree/main/examples/ModbusRTUSlaveExample
#include <ModbusRTUSlave.h>
#include <SoftwareSerial.h>

#define RS485_TX 10 
#define RS485_RX 11
#define LED_PIN 13
const byte dePin = 2;

SoftwareSerial RS485_serial(RS485_RX, RS485_TX);  // Create a serial port with the software serial pins.
ModbusRTUSlave modbus(RS485_serial, dePin);       // Create a modbus object that uses the software serial port.

//This should also work, but we won't be able to print to screen since there is only one serial port.
//ModbusRTUSlave modbus(Serial, dePin);     

const uint8_t numCoils = 2;   // Number of digital outputs
bool coils[numCoils];         // array holding all the digital outputs

uint16_t holdingRegisters[2]; // Number of read-write registers in the slave

void setup() {
  Serial.begin(9600);
  Serial.println("Modbus Slave");

  pinMode(LED_PIN, OUTPUT);

  RS485_serial.begin(9600);         
  modbus.begin(1, 9600, SERIAL_8N1);  // Slave address = 1, Baud rate = 9600, Serial parameters = 8bit, no parity, 1 stop bit.
  modbus.configureCoils(coils, numCoils);
  modbus.configureHoldingRegisters(holdingRegisters, 2);
}

void loop() {
  int a = modbus.poll(); // Each time this function runs, it updates the values of the coils, holding registers...etc based on the data it receives in the RS485_serial lines.
  //  Serial.println(a);

  //  modbus.processPdu();  // Unsure
  Serial.println("holdingRegisters: ");
  Serial.println(holdingRegisters[0]);
  Serial.println(holdingRegisters[1]);
  Serial.println("coils: ");
  Serial.println(coils[0]);
  Serial.println(coils[1]);
  Serial.println();
  delay(100);

  digitalWrite(LED_PIN, coils[0]);    // Update the output pin with value of the coi register.
}
