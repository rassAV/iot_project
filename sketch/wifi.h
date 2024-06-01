#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WiFiMulti.h>

ESP8266WiFiMulti wifiMulti;
WiFiClient wifiClient;

String ip = "";

String id() {
  int mac_len = WL_MAC_ADDR_LENGTH;
  uint8_t mac[mac_len];
  WiFi.softAPmacAddress(mac);
  String mac_id = String(mac[mac_len-2], HEX) + String(mac[mac_len-1], HEX);
  return mac_id;
}

bool start_AP_mode() {
  String ssid_id = ESP_NAME;
  IPAddress ap_IP(192, 168, 99, 34);
  WiFi.disconnect();
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(ap_IP, ap_IP, IPAddress(255, 255, 255, 0));
  WiFi.softAP((ESP_NAME + "_esp" + id()).c_str(), ESP_PASSWORD.c_str());
  Serial.println("\nWiFi started in AP mode " + ssid_id);
  return true;
}

bool start_client_mode() {
  WiFi.softAPdisconnect(true);
  wifiMulti.addAP(CLI_SSID, CLI_PASS);
  while(wifiMulti.run() != WL_CONNECTED) {
    delay(10);
  }
  return true;
}

bool init_WIFI(bool AP_mode) {
  if(AP_mode) {
    start_AP_mode();
    ip = WiFi.softAPIP().toString();
  } else {
    start_client_mode();
    ip = WiFi.localIP().toString();
  }
  Serial.println("IP address: " + ip);
  return true;
}