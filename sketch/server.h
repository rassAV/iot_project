#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

ESP8266WebServer server(WEB_SERVER_PORT);

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
  state = states[1];
  Serial.print("CLI_SSID: ");
  Serial.println(CLI_SSID);
  Serial.print("CLI_PASS: ");
  Serial.println(CLI_PASS);
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
  Serial.print("Server started on ");
  Serial.println(WEB_SERVER_PORT);
}