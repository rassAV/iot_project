// WIFI access point
String AP_NAME = "AirQuality_id0_esp";
String AP_PASSWORD = "12345678";

// CLI WIFI client
const char* CLI_SSID = "";
const char* CLI_PASS = "";

int WEB_SERVER_PORT = 80;

String states[] = {
  "ACCESS_POINT",
  "WIFI_CONNECTING",
  "SEND_WAITING",
  "SENDING_DATA"
};

String IP_SERVER = "192.168.247.201";
String state = states[0];

bool APconnect = false;