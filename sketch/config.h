int ESP_ID = 0;

// WIFI access point
String AP_NAME = "Nanomachines";
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

String ip = "";
String state = states[0];

bool APconnect = false;