/* Copyright (c) 2021 Connor McMillan <connor@mcmillan.website>. All rights reserved.
 * 
 * This work is licensed under the terms of the MIT license.
 * For a copy, see <https://opensource.org/licenses/MIT>
 */
 
#define VERSION "100"

const int RELAY_PIN = 2;
String incomingMessage;
// The number of interation of the loop() function before cutting off power.
// We're trying to keep it at ~10 seconds. It should be siginificantly less than
// the time required to reboot the CPU.
int TTL = 30;

void setup() {
  // Everything in this function runs only once at power initiation.
  digitalWrite(RELAY_PIN, HIGH);
  pinMode(RELAY_PIN, OUTPUT);
  Serial.begin(115200);
  Serial.setTimeout(500);
}

void loop() {
  // Everything in this function runs on an infinte loop.
  incomingMessage = Serial.readString();
  if (incomingMessage == "HEARTBEAT" || incomingMessage == "VERSION"){
      // Reset TTL on each heartbeat
      TTL = 30;
      if (incomingMessage == "HEARTBEAT")
        Serial.println("ACK");
      else if (incomingMessage == "VERSION")
        Serial.println(VERSION);
      Serial.flush();
      digitalWrite(RELAY_PIN, HIGH);
      delay(500);
  }
  if (incomingMessage == ""){
      TTL--;
      if (TTL <= 0){
        digitalWrite(RELAY_PIN, LOW);
        // Reset TTL if it's about to choke the Arduino to death.
        if (TTL <= -32000)
          TTL = 30;
      }
  } 
}
