#include <Arduino.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.hpp>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

#include "config.h"
#include "wifi.h"
#include "server.h"

#define rx_pin 1
#define tx_pin 2
#define button_pin 4
#define red_rgb_led 7
#define green_rgb_led 5
#define blue_rgb_led 6

SoftwareSerial sds(rx_pin, tx_pin);

unsigned long buttonPressStart = 0;
unsigned long ledFlashingStart = 0;
bool buttonPressed = false;
bool is_wifi_on = false;



void setup() {
  Serial.begin(9600);
  sds.begin(9600);
  
  pinMode(button_pin, INPUT_PULLUP);
  pinMode(red_rgb_led, OUTPUT);
  pinMode(green_rgb_led, OUTPUT);
  pinMode(blue_rgb_led, OUTPUT);

  digitalWrite(red_rgb_led, LOW);
  digitalWrite(green_rgb_led, LOW);
  digitalWrite(blue_rgb_led, LOW);
}

void loop() {
  if (state == states[1]) {
    redLightFlashing(millis() - ledFlashingStart);
    is_wifi_on = init_WIFI(false);
    if (is_wifi_on) {
      state = states[2];
    }
  } else if (state == states[2]) {
    yellowLight();
  } else if (state == states[3]) {
    greenLight();
    if (sds.available() >= 10) {
      uint8_t buf[10];
      sds.readBytes(buf, 10);
      if (buf[0] == 0xAA && buf[1] == 0xC0) {
        String pm25 = String((buf[3] * 256 + buf[2]) / 10);
        String pm10 = String((buf[5] * 256 + buf[4]) / 10);
        post(pm25, pm10);
      }
    }
  } else {
    redLight();
    if (!APconnect) {
      is_wifi_on = init_WIFI(true);
      if (is_wifi_on) {
        server_init();
        APconnect = true;
      }
    } else {
      server.handleClient();
    }
  }
  
  if (digitalRead(button_pin) == LOW) {
    if (!buttonPressed) {
      buttonPressed = true;
      buttonPressStart = millis();
    }
  } else {
    if (buttonPressed) {
      buttonPressed = false;
      if (millis() - buttonPressStart < 3000) {
        if (state == states[2]) state = states[3];
        else if (state == states[3]) state = states[2];
      } else {
        state = states[0];
      }
    }
  }
  
  delay(50);
}



void post(String pm25, String p10){
  HTTPClient http;

  http.begin(wifiClient, "http://" + ip + ":8005/submit_air");
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST("{\"pm25\":\"" + pm25 + "\", \"pm10\":\"" + pm10 + "\", \"esp_name\":\"" + AP_NAME + "\", \"esp_id\":\"" + ESP_ID + "\"}");

  if (httpCode > 0) {
    Serial.printf("POST code: %d\n", httpCode);
    Serial.println(http.getString());
  } else {
    Serial.printf("ERROR: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void redLight() {
  digitalWrite(red_rgb_led, HIGH);
  digitalWrite(green_rgb_led, LOW);
  digitalWrite(blue_rgb_led, LOW);
}
void redLightFlashing(int time) {
  if (time > 500) {
  digitalWrite(red_rgb_led, HIGH);
  digitalWrite(green_rgb_led, LOW);
  digitalWrite(blue_rgb_led, LOW);
  } else {
  digitalWrite(red_rgb_led, LOW);
  digitalWrite(green_rgb_led, LOW);
  digitalWrite(blue_rgb_led, LOW);
  }
  if (time > 1000) ledFlashingStart = millis();
}
void yellowLight() {
  digitalWrite(red_rgb_led, HIGH);
  digitalWrite(green_rgb_led, HIGH);
  digitalWrite(blue_rgb_led, LOW);
}
void greenLight() {
  digitalWrite(red_rgb_led, LOW);
  digitalWrite(green_rgb_led, HIGH);
  digitalWrite(blue_rgb_led, LOW);
}