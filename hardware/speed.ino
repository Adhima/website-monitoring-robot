#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "WIFI_NAME";
const char* password = "PASSWORD";
const char* serverURL = "http://<IP_FLASK>:5000/speed";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
}

void loop() {
  int speed = hitungKecepatan(); // hasil dari rotary encoder kamu

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");
  String body = "{\"speed\":" + String(speed) + "}";
  http.POST(body);
  http.end();

  delay(500); // kirim tiap 0.5 detik
}