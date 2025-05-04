void cekStatusLampu() {
    HTTPClient http;
    http.begin(String(server) + "/lamp_status");
    int responseCode = http.GET();
  
    if (responseCode == 200) {
      String payload = http.getString();
      bool lampuNyala = payload.indexOf("true") >= 0;
      digitalWrite(pinLamp, lampuNyala ? HIGH : LOW);
      Serial.println("Lampu: " + String(lampuNyala ? "ON" : "OFF"));
    }
  
    http.end();
  }
  