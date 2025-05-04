#include <WiFi.h>
#include <HTTPClient.h>

// ----------- KONFIGURASI WIFI & SERVER -----------
const char* ssid = "Redmi";
const char* password = "12345678";
const char* server = "http://192.168.47.106:5000";

// ----------- PIN SETUP -----------
const int pinREn          = 21; // Arah maju BTS7960
const int pinLEn          = 22; // Arah mundur BTS7960 (tidak dipakai)
const int pinPWM_R        = 5;  // PWM arah maju BTS7960
const int pinPWM_L        = 18; // PWM arah mundur BTS7960 (tidak dipakai)
const int pinRelayMotor   = 4;  // Relay motor utama (start/stop)
const int pinRelayLampu   = 14; // Relay untuk kontrol lampu

// ----------- VARIABEL KONTROL -----------
unsigned long lastMotorStatusCheck = 0;
unsigned long lastSpeedCheck = 0;
unsigned long lastLampuCheck = 0;

bool motorAktif = false;
bool lampuNyala = false;
float targetSpeedKmh = 0;

void setup() {
  Serial.begin(115200);

  pinMode(pinREn, OUTPUT);
  pinMode(pinLEn, OUTPUT);
  pinMode(pinRelayMotor, OUTPUT);
  pinMode(pinRelayLampu, OUTPUT);

  digitalWrite(pinREn, LOW);
  digitalWrite(pinLEn, LOW);
  digitalWrite(pinRelayMotor, LOW);
  digitalWrite(pinRelayLampu, LOW);

  ledcSetup(0, 5000, 8);
  ledcAttachPin(pinPWM_R, 0);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi.");
}

void loop() {
  unsigned long now = millis();

  if (now - lastMotorStatusCheck > 1000) {
    cekStatusMotor();
    lastMotorStatusCheck = now;
  }

  if (now - lastSpeedCheck > 1000) {
    cekTargetKecepatan();
    lastSpeedCheck = now;
  } 

  if (now - lastLampuCheck > 1000) {
    cekStatusLampu();
    lastLampuCheck = now;
  }
}

void cekStatusMotor() {
  HTTPClient http;
  http.begin(String(server) + "/motor_status");
  int code = http.GET();

  if (code == 200) {
    String payload = http.getString();
    motorAktif = payload.indexOf("true") >= 0;

    digitalWrite(pinRelayMotor, motorAktif ? HIGH : LOW);
    digitalWrite(pinREn, motorAktif ? HIGH : LOW);
    digitalWrite(pinLEn, LOW); // arah mundur tidak digunakan

    if (!motorAktif) {
      ledcWrite(0, 0);
    }

    Serial.println("[ESP32] Motor " + String(motorAktif ? "ON" : "OFF"));
  }

  http.end();
}

void cekTargetKecepatan() {
  if (!motorAktif) return;

  HTTPClient http;
  http.begin(String(server) + "/motor_speed_status");
  int code = http.GET();

  if (code == 200) {
    String payload = http.getString();
    int idx = payload.indexOf("speed");
    if (idx >= 0) {
      int pos = payload.indexOf(":", idx);
      float speed = payload.substring(pos + 1).toFloat();
      targetSpeedKmh = speed;
    }

    int duty = map(targetSpeedKmh * 10, 0, 60, 0, 255);
    duty = constrain(duty, 0, 255);
    ledcWrite(0, duty);

    Serial.println("[ESP32] Target Speed: " + String(targetSpeedKmh) + " km/h → PWM: " + String(duty));
  }

  http.end();
}

void cekStatusLampu() {
  HTTPClient http;
  http.begin(String(server) + "/lampu_status");
  int code = http.GET();

  if (code == 200) {
    String payload = http.getString();
    lampuNyala = payload.indexOf("true") >= 0;

    digitalWrite(pinRelayLampu, lampuNyala ? HIGH : LOW);
    Serial.println("[ESP32] Lampu: " + String(lampuNyala ? "ON" : "OFF"));
  }

  http.end();
}
