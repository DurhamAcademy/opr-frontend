/*
Arduino Mega Controller for CGBOT-OPR

** Use the flash_arduino.sh script to flash the Arduino attached.

Arduino Mega Devices and Pins:

ULTRASONIC SENSORS:
* In a top down view. Robot front at the top.
    1                              2
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
       @                        @
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    3                            4

trigger, echo
1: 48,46
2: 44,42
3: 34,36
4: 40,38

// Temperature Sensor
i2C

// Voltage Sensor
A0

Returns:
US1|US2|US3|US4|TEMP|HUMIDITY|VOLTAGE

*/

#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"

// Ultrasonics
// [ [echo, trigger] ]
int sensors[][2] = { {46, 48}, {42, 44}, {36, 34}, {38, 40} };
// int sensors[][2] = { {6, 7} };

// Temperature SHT30-D
Adafruit_SHT31 sht31 = Adafruit_SHT31();
bool enableHeater = false;

// Voltage Sensors
float voltage;

void setup()
{
  Serial.begin(9600);

  // Ultrasonic Sensors Pinmode
  for (int i = 0; i < sizeof sensors/sizeof sensors[0]; i++) {
    pinMode(sensors[i][0], INPUT);
    pinMode(sensors[i][1], OUTPUT);
    digitalWrite(sensors[i][0], HIGH);
  }

  sht31.begin(0x44);

  // Voltage Sensor
  analogReference(DEFAULT);

}

void loop()
{
      String message = "$";

      for (int i = 0; i < sizeof sensors/sizeof sensors[0]; i++) {
        int echo = sensors[i][0];
        int trig = sensors[i][1];
        digitalWrite(trig, LOW);
        delayMicroseconds(2);

        // Send a 10uS high to trigger ranging
        digitalWrite(trig, HIGH);
        delayMicroseconds(10);

        // Send pin low again
        digitalWrite(trig, LOW);

        // Read in times pulse
        int distance = pulseIn(echo, HIGH,26000);
        distance= distance/58;

        message += String(distance) + "|";

        // Add additional delay for ultrasonics per their documentation.
        // So a reading doesn't occur more than every 50 microseconds.
        // Perhaps helps with overlapping in sensors as well.
        // https://wiki.dfrobot.com/Weatherproof_Ultrasonic_Sensor_With_Separate_Probe_SKU_SEN0208
        // Double to be safe
        delayMicroseconds(100);

      }

      // Return Temperature on top/high/hot side
      float t = sht31.readTemperature();
      message += String(t) + "|";
      // Return humidity on top/high/hot side
      float h = sht31.readHumidity();
      message += String(h) + "|";
      // Return voltage reading from battery
      voltage = analogRead(A1) * 0.0252427 ;
      message += String(voltage) + "|";

      Serial.println(message);

}

