/* Copyright (c) 2021-2023 Connor McMillan <connor@mcmillan.website>. All rights reserved.
 * 
 * This work is licensed under the terms of the MIT license.
 * For a copy, see <https://opensource.org/licenses/MIT>
 */

// Libraries
#include <CmdParser.hpp>
#include <DallasTemperature.h>
#include <ds_external_eeprom_i2c.h>
#include <OneWire.h>
#include <Wire.h>

// Definitions

// Versions
#define HARDWARE_VERSION "2"
#define FIRMWARE_VERSION "200"

// Pins
#define ONE_WIRE_BUS 4
const int TWELVE_V_RELAY_PIN = 2;
const int VAC_RELAY_PIN = 3;

// Addresses
#define EEPROM_ADDR 0x50

// Buffers
String incomingMessage;


// Global objects/variables

// The number of interation of the loop() function before cutting off power.
// We're trying to keep it at ~10 seconds. It should be siginificantly less than
// the time required to reboot the CPU.
int TTL = 30;

// Initiate OneWire for the DS18B20 probe.
// The sensors object is needed in loop(), hence its placement is here.
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Command parser
CmdParser cmdParser;

// EEPROM
ds_external_eeprom_i2c eeprom(32,16,EEPROM_ADDR);

void setup() {
  // Initiate pin modes for the relays
  pinMode(TWELVE_V_RELAY_PIN, OUTPUT);
  pinMode(VAC_RELAY_PIN, OUTPUT);

  // Initiate the DallasTemperature library for the DS18B20 probe
  sensors.begin();

  // Initiate the Wire library
  Wire.begin();
  
  // Initiate the serial console
  Serial.begin(115200);
  Serial.setTimeout(500);
}

void loop() {
  // Get temperature from the DS18B20 probe
  sensors.requestTemperatures();
  // Activate relay to power fans if the temperature from the probe is higher than the temperature stored in EEPROM
  if (double(sensors.getTempFByIndex(0)) > eepromReadTemperature()){
    digitalWrite(VAC_RELAY_PIN, HIGH);
  } else {
    // Turn off the fans
    digitalWrite(VAC_RELAY_PIN, LOW);
  }
  
  CmdBuffer<32> myBuffer;

  if (Serial.available()) {
    if (myBuffer.readFromSerial(&Serial)) {
      if (cmdParser.parseCmd(&myBuffer) != CMDPARSER_ERROR) {
        if (cmdParser.equalCommand_P(PSTR("?")) || cmdParser.equalCommand_P(PSTR("HELP"))) {
          help();
        } else if (cmdParser.equalCommand_P(PSTR("GET_TEMP"))) {
          getTemp();
        } else if (cmdParser.equalCommand_P(PSTR("GET_E_TEMP"))) {
          getETemp();
        } else if (cmdParser.equalCommand_P(PSTR("HEARTBEAT"))) {
          heartBeat();
        } else if (cmdParser.equalCommand_P(PSTR("HARDWARE_VERSION"))) {
          hardwareVersion();
        } else if (cmdParser.equalCommand_P(PSTR("SET_E_TEMP"))) {
          setETemp(atoi(cmdParser.getCmdParam(1)));
        } else if (cmdParser.equalCommand_P(PSTR("FIRMWARE_VERSION"))) {
          ver();
        } else {
          Serial.print("ERROR: Unknown command ");
          Serial.println(cmdParser.getCommand());
        }
      } else {
        Serial.println("Parser error!");
      }
    }
  } else {
    TTL--;
    if (TTL <= 0){
      // Turn off power to the USB hubs
      digitalWrite(TWELVE_V_RELAY_PIN, LOW);
      // Reset TTL if it's about to choke the Arduino to death.
    if (TTL <= -32000)
      TTL = 30;
    }
  }
}

// Additional methods and functions
void help() {
    Serial.println("Copyright (c) 2021-2023 Connor McMillan <connor@mcmillan.website>. All rights reserved.");
    Serial.print("Hardware Version: ");
    Serial.println(HARDWARE_VERSION);
    Serial.print("Firmware Version: ");
    Serial.println(FIRMWARE_VERSION);
    Serial.print("EEPROM: ");
    Serial.println(eeprom.check() ? "OK":"ERROR");
    Serial.println("Available Commands:");
    Serial.println("? - Prints this");
    Serial.println("HELP - Prints this");
    Serial.println("HARDWARE_VERSION - Display the hardware version");
    Serial.println("FIRMWARE_VERSION - Display the firmware version");
    Serial.println("GET_E_TEMP - Get the temperature value stored in the EEPROM");
    Serial.println("GET_TEMP - Get the temperature from the probe");
    Serial.println("SET_E_TEMP <0-255> - Set the temperature (°F) value stored in the EEPROM");
}
void getTemp() {
  Serial.println(sensors.getTempFByIndex(0));
}
void getETemp() {
  Serial.println(eepromReadTemperature());
}
void heartBeat() {
  // Reset TTL on each heartbeat
  TTL = 30;
  Serial.println("ACK");
  Serial.flush();
  // Allow power to flow to the USB hubs.
  digitalWrite(TWELVE_V_RELAY_PIN, HIGH);
  delay(500);
}
void hardwareVersion() {
  Serial.println(HARDWARE_VERSION);
}
void setETemp(int temp) {
  if (temp < 0 || temp > 255){
    Serial.println("ERROR: Position 1 is not in range <0-255>");
    return;
  }
  eepromWriteTemperature(temp);
}
void ver() {
  Serial.println(FIRMWARE_VERSION);
}


// EEPROM reading and writing specific functions
// These are to ensure that data is written and read from the same
// location through out the entire code block. Update the table below when
// implementing new functions.
int eepromReadTemperature(){
  return eeprom.readByte(0x00);
}
void eepromWriteTemperature(int temp){
  eeprom.writeByte(0x00, byte(temp));
}

/*                          EEPROM Value Table
 * +--------------------------------------------------------------------------------+
 * |         Name         |    Address    |   Size   |   Unit   |       Range       |
 * |                      |               |  (Bytes) |          |                   |
 * +--------------------------------------------------------------------------------+
 * |  Cabinet Temperature |      0x0      |     1    |    °F    |      0 - 255      |
 * |       Threshold      |               |          |          |                   |
 * +--------------------------------------------------------------------------------+
 * |                      |               |          |          |                   |
 * |                      |               |          |          |                   |
 * +--------------------------------------------------------------------------------+
 * |                      |               |          |          |                   |
 * |                      |               |          |          |                   |
 * +--------------------------------------------------------------------------------+
 */
