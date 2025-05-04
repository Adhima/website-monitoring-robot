const int pinRelayMotor = 4;

void setup() {
  // ...
  pinMode(pinRelayMotor, OUTPUT);
  // ...
}

void cekStatusMotor() {
  HTTPClient http;
  http.begin(String(server) + "/motor_status");
  int responseCode = http.GET();

  if (responseCode == 200) {
    String payload = http.getString();
    bool motorNyala = payload.indexOf("true") >= 0;

    digitalWrite(pinRelayMotor, motorNyala ? HIGH : LOW);
    Serial.println("[ESP32] Motor: " + String(motorNyala ? "ON" : "OFF"));
  }

  http.end();
}
