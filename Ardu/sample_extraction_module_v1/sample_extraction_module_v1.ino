// Sample extraction module.
// Arduino UNO to control:
//   HX711: Load cell amplifier and measure weight of fluid in realtime. The calibration factor needs to be precomputed. see HX711_load_call.ino
//   DHT22: Temperature and Humidity sensor over one wire.
//   LCD 16x2  screen over I2C.
//   BTN8982A Infineon Motor driver to drive two unidirectional Brushed DC motors for the peristatic pumps.

#include "Grove_Temperature_And_Humidity_Sensor.h"
#include "HX711.h"
#include <LiquidCrystal_I2C.h>

// LCD 16x2 display over I2C
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Format -> (Address,Width,Height ) /Code to display Strings on I2C LCD by www.playwithcircuit.com

// HX711 Load cell amplifier
const int pin_LOADCELL_DOUT = 7;         //2;
const int pin_LOADCELL_SCK = 6;          //3;
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

// PUSH BUTTONS
const int pin_button_1 = 8;
const int pin_button_2 = 9;

// POTS
const int pin_pot_1 = A2;   // Pot to control Motor_1
const int pin_pot_2 = A3;   // Pot to control Motor_2

void setup() {
  Serial.begin(9600);
  Serial.println("Sample Extraction Module !");

  // LCD 16x2
  // initialize the lcd
  lcd.init();
  // Turn on the Backlight
  lcd.backlight();

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

  // TAC Buttons.
  pinMode(pin_button_1, INPUT_PULLUP);
  pinMode(pin_button_2, INPUT_PULLUP);
}

void loop() {
  get_temp_hum();
  get_weight();

  // Clear the display buffer
  lcd.clear();
  // Set cursor (Column, Row)
  // Row 0
  lcd.setCursor(0, 0);
  lcd.print("Humidity=");
  lcd.setCursor(9, 0);
  lcd.print(humidity);

  // Row 1
  lcd.setCursor(0, 1);
  lcd.print("T=");
  lcd.setCursor(2, 1);
  lcd.print(temperature);

  lcd.setCursor(8, 1);
  lcd.print("W=");
  lcd.setCursor(10, 1);
  lcd.print(weight);
  lcd.setCursor(15, 1);
  lcd.print("g");


  Serial.println(digitalRead(pin_button_1));
  Serial.println(digitalRead(pin_button_2));
  
  Serial.println(analogRead(pin_pot_1));
  Serial.println(analogRead(pin_pot_2));

  int pot_1_adc = analogRead(pin_pot_1);
  int pot_2_adc = analogRead(pin_pot_2);
  set_motor_1(map(pot_1_adc, 0, 1023, 0, 100));
  set_motor_2(map(pot_2_adc, 0, 1023, 0, 100));
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
