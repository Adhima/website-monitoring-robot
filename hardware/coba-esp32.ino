#include <WiFi.h>
#include <HTTPClient.h>

// ===========================
// KONFIGURASI
// ===========================
const char* ssid = "WIFI_NAME";
const char* password = "PASSWORD_WIFI";
const char* server = "http://123.45.67.89:5000"; // Ganti dengan IP/domain Flask 

const int pinEncoderA = 34;
const int pinEncoderB = 35;
const int pinLamp = 2;
const int pinRelayMotor = 4;
const int pinMotorPWM = 5; // GPIO PWM output ke driver motor

// Kalibrasi speed
const float tick_per_rev = 600.0;           // Tick per putaran rotary encoder
const float keliling_roda = 0.314;          // Keliling roda (m), contoh: 10cm diameter

volatile int encoderTicks = 0;
unsigned long lastSpeedSend = 0;
unsigned long lastLampCheck = 0;
unsigned long lastSpeedCheck = 0;
float targetSpeedKmh = 0;

// ===========================
// INTERRUPT UNTUK ENCODER
// ===========================
void IRAM_ATTR encoderISR() {
  if (digitalRead(pinEncoderA) == digitalRead(pinEncoderB)) {
    encoderTicks++;
  } else {
    encoderTicks--;
  }
}

// ===========================
// SETUP
// ===========================
void setup() {
  Serial.begin(115200);
  pinMode(pinEncoderA, INPUT_PULLUP);
  pinMode(pinEncoderB, INPUT_PULLUP);
  pinMode(pinLamp, OUTPUT);
  pinMode(pinRelayMotor, OUTPUT);
  ledcSetup(0, 5000, 8);             // Channel 0, 5kHz, 8-bit
  ledcAttachPin(pinMotorPWM, 0);     // PWM keluar di pin 5

  attachInterrupt(digitalPinToInterrupt(pinEncoderA), encoderISR, CHANGE);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n[ESP32] WiFi Connected! IP: " + WiFi.localIP().toString());
}

// ===========================
// LOOP
// ===========================
void loop() {
  unsigned long now = millis();

  // Kirim kecepatan tiap 500ms
  if (now - lastSpeedSend > 500) {
    int ticks = encoderTicks;
    encoderTicks = 0;

    float mps = (ticks / tick_per_rev) * keliling_roda / 0.5;  // sampling tiap 0.5 detik
    float kmh = mps * 3.6;

    kirimKecepatan(kmh);
    lastSpeedSend = now;
  }

  // Cek status lampu tiap 1 detik
  if (now - lastLampCheck > 1000) {
    cekStatusLampu();
    lastLampCheck = now;
  }

  // Cek status motor tiap 1 detik
  if (now - lastSpeedCheck > 1000) {
    cekMotorTargetSpeed();
    lastSpeedCheck = now;
  }
}

// ===========================
// FUNGSI: Kirim kecepatan ke Flask
// ===========================
void kirimKecepatan(float speed) {
  HTTPClient http;
  http.begin(String(server) + "/speed");
  http.addHeader("Content-Type", "application/json");

  String body = "{\"speed\":" + String(speed, 2) + "}"; // 2 angka desimal
  int responseCode = http.POST(body);
  Serial.println("[ESP32] Kirim speed: " + body + " → HTTP " + String(responseCode));

  http.end();
}

// ===========================
// FUNGSI: Cek status lampu dari Flask
// ===========================
void cekStatusLampu() {
  HTTPClient http;
  http.begin(String(server) + "/lamp_status");
  int responseCode = http.GET();

  if (responseCode == 200) {
    String payload = http.getString();
    bool lampuNyala = payload.indexOf("true") >= 0;

    digitalWrite(pinLamp, lampuNyala ? HIGH : LOW);
    Serial.println("[ESP32] Lampu: " + String(lampuNyala ? "ON" : "OFF"));
  } else {
    Serial.println("[ESP32] Gagal ambil status lampu: HTTP " + String(responseCode));
  }

  http.end();
}

// ===========================
// FUNGSI: Cek status motor dari Flask
// ===========================
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

//============================
// FUNGSI: Cek target speed dari Flask
//============================
void cekMotorTargetSpeed() {
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

    // Mapping target speed ke duty PWM (0–255)
    int duty = map(targetSpeedKmh * 10, 0, 60, 0, 255); // 6 km/h = max
    duty = constrain(duty, 0, 255);
    ledcWrite(0, duty);

    Serial.println("[ESP32] Target Speed: " + String(targetSpeedKmh) + " km/h → PWM: " + String(duty));
  }

  http.end();
}