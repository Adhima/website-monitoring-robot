#include <WiFi.h>
#include <HTTPClient.h>

// ===========================
// KONFIGURASI WIFI & SERVER
// ===========================
const char* ssid = "Redmi";
const char* password = "12345678";
const char* server = "http://192.168.160.106:8000"; // Ganti dengan IP/domain Flask kamu

// ===========================
// KONFIGURASI PIN BTS7960
// ===========================
const int RPWM_PIN = 5;    // PWM kanan (gerak maju)
const int LPWM_PIN = 18;   // PWM kiri (gerak mundur, set 0 untuk maju)
const int R_EN = 21;
const int L_EN = 22;
// ===========================
// VARIABEL
// ===========================
float targetSpeedKmh = 0;
unsigned long lastSpeedCheck = 0;
unsigned long checkInterval = 1000; // cek setiap 1 detik

void setup() {
  Serial.begin(115200);

  // Setup pin enable
  pinMode(R_EN, OUTPUT);
  pinMode(L_EN, OUTPUT);
  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);
  //pinMode(pinRelayMotor, OUTPUT);
  //pinMode(pinRelayLampu, OUTPUT);
  //digitalWrite(pinRelayMotor, LOW); // Pastikan motor mati saat awal
  //digitalWrite(pinRelayLampu, LOW);

  // Setup PWM ESP32
  ledcSetup(0, 5000, 8); // channel 0 untuk RPWM
  ledcSetup(1, 5000, 8); // channel 1 untuk LPWM

  ledcAttachPin(RPWM_PIN, 0);
  ledcAttachPin(LPWM_PIN, 1);

  // Koneksi WiFi
  WiFi.begin(ssid, password);
  Serial.print("Menghubungkan ke WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nTerhubung ke WiFi!");
}

void loop() {
  if (millis() - lastSpeedCheck >= checkInterval) {
    cekMotorTargetSpeed();
    lastSpeedCheck = millis();
  }
}

void cekMotorTargetSpeed() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/motor_speed_status");
    int responseCode = http.GET();

    if (responseCode == 200) {
      String payload = http.getString();
      int idx = payload.indexOf("speed");
      if (idx >= 0) {
        int pos = payload.indexOf(":", idx);
        float speed = payload.substring(pos + 1).toFloat();
        targetSpeedKmh = speed;
      }

      // Mapping ke PWM (max 6 km/h → PWM 255)
      int duty = map(targetSpeedKmh * 10, 0, 60, 0, 127);
      duty = constrain(duty, 0, 255);

      // Gerak maju → RPWM = duty, LPWM = 0
      ledcWrite(0, duty);  // RPWM
      ledcWrite(1, 0);     // LPWM

      Serial.println("[ESP32] Speed: " + String(targetSpeedKmh) + " km/h → PWM: " + String(duty));
    } else {
      Serial.print("HTTP Error: ");
      Serial.println(responseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi tidak terhubung!");
  }
}
