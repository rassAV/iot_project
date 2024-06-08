#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.hpp>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>

int rx_pin = D3;
int tx_pin = D4;
int button_pin = D1;
int red_rgb_led = D5;
int green_rgb_led = D6;
int blue_rgb_led = D7;

SoftwareSerial sds(rx_pin, tx_pin);

ESP8266WiFiMulti wifiMulti;
ESP8266WebServer server(80);

String IP_SERVER = "192.168.247.201";

const char* ESP_NAME = "AirQuality_id0";
const char* ESP_PASSWORD = "12345678";

const char* CLI_SSID = "";
const char* CLI_PASS = "";

long buttonPressStart = 0;
long delayStart = 0;
int state = 0;
bool APconnect = false;
bool buttonPressed = false;

void setup() {
  Serial.begin(9600);
  sds.begin(9600);

  pinMode(button_pin, INPUT_PULLUP);
  pinMode(red_rgb_led, OUTPUT);
  pinMode(green_rgb_led, OUTPUT);
  pinMode(blue_rgb_led, OUTPUT);
}

void loop() {
  if (state == 1) {
    lamp(true, true, false);
    start_client_mode();
    state = 2;
  } else if (state == 2) {
    if (millis() - delayStart > 500) lamp(false, false, true);
    else lamp(true, true, true);
    if (millis() - delayStart > 1000) delayStart = millis();
  } else if (state == 3) {
    lamp(true, false, true);
    if ((wifiMulti.run() == WL_CONNECTED)) {
      if (sds.available() >= 10 && millis() - delayStart > 1000) {
        uint8_t buf[10];
        sds.readBytes(buf, 10);
        if (buf[0] == 0xAA && buf[1] == 0xC0) {
          uint16_t pm25 = (buf[3] * 256 + buf[2]) / 10;
          uint16_t pm10 = (buf[5] * 256 + buf[4]) / 10;
          if (pm25 < 1000 && pm10 < 1000) post(String(pm25), String(pm10));
        } else {
          sds.read();
        }
        delayStart = millis();
      }
    } else {
      state = 1;
    }
  } else {
    lamp(false, true, true);
    if (!APconnect) {
      start_AP_mode();
      server_init();
      APconnect = true;
    } else {
      if (APconnect) server.handleClient();
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
        if (state == 2) state = 3;
        else if (state == 3) state = 2;
      } else {
        state = 0;
      }
    }
  }
}

void lamp(bool r, bool g, bool b) {
  digitalWrite(red_rgb_led, r ? HIGH : LOW);
  digitalWrite(green_rgb_led, g ? HIGH : LOW);
  digitalWrite(blue_rgb_led, b ? HIGH : LOW);
}

void post(String pm25, String pm10) {
  WiFiClient client;
  HTTPClient http;
  http.begin(client, "http://" + IP_SERVER + ":8005/submit_air");
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST("{\"pm25\":\"" + pm25 + "\", \"pm10\":\"" + pm10 + "\", \"esp_name\":\"" + String(ESP_NAME) + "\"}");
  if (httpCode > 0) Serial.println(http.getString());
  http.end();
}

void handle_root() {
  String page_code = "<form action=\"/PROCESS\" method=\"POST\">";
  page_code += "CLI_SSID:<input type=\"text\" name=\"cli_ssid\" placeholder=\"Input wifi name\"><br>";
  page_code += "CLI_PASS:<input type=\"text\" name=\"cli_pass\" placeholder=\"Input wifi name\"><br>";
  page_code += "<input type=\"submit\" value=\"Send\"></form>";
  server.send(200, "text/html", page_code);
}

void handle_process() {
  CLI_SSID = server.arg("cli_ssid").c_str();
  CLI_PASS = server.arg("cli_pass").c_str();
  APconnect = false;
  state = 1;
  server.sendHeader("Location", "/");
  server.send(303);
}

void handle_not_found() {
  server.send(404, "text/html", "404: check URL");
}

void server_init() {
  server.on("/", HTTP_GET, handle_root);
  server.on("/PROCESS", HTTP_POST, handle_process);
  server.onNotFound(handle_not_found);
  server.begin();
}

void start_AP_mode() {
  IPAddress ap_IP(192, 168, 99, 34);
  WiFi.disconnect();
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(ap_IP, ap_IP, IPAddress(255, 255, 255, 0));
  WiFi.softAP(ESP_NAME, ESP_PASSWORD);
}

void start_client_mode() {
  WiFi.softAPdisconnect(true);
  wifiMulti.addAP(CLI_SSID, CLI_PASS);
  while(wifiMulti.run() != WL_CONNECTED) {
    delay(10);
  }
}