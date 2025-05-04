#include <WiFi.h>
#include <HTTPClient.h>
#include <BTS7960.h> // Library by Yash Herekar

// ----------- KONFIGURASI WIFI & SERVER -----------
const char* ssid = "Redmi";
const char* password = "12345678";
const char* server = "http://192.168.47.106:5000";

// ----------- PIN SETUP -----------
#define RPWM 5
#define LPWM 18
#define R_EN 21
#define L_EN 22
const int pinRelayMotor = 4;
const int pinRelayLampu = 14;
const int pinEncoder = 34;

// ----------- OBJEK LIBRARY BTS7960 -----------
BTS7960 motor(R_EN, L_EN, RPWM, LPWM);

// ----------- VARIABEL KONTROL -----------
unsigned long lastMotorStatusCheck = 0;
unsigned long lastSpeedCheck = 0;
unsigned long lastLampuCheck = 0;
unsigned long lastSpeedSend = 0;

bool motorAktif = false;
bool lampuNyala = false;
float targetSpeedKmh = 0;

// Rotary encoder
volatile int pulseCount = 0;
const float pulsesPerRevolution = 20.0;
const float wheelCircumference = 0.314;

void IRAM_ATTR countPulse() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);

  pinMode(pinRelayMotor, OUTPUT);
  pinMode(pinRelayLampu, OUTPUT);
  pinMode(pinEncoder, INPUT_PULLUP);

  digitalWrite(pinRelayMotor, LOW);
  digitalWrite(pinRelayLampu, LOW);

  motor.begin();
  attachInterrupt(digitalPinToInterrupt(pinEncoder), countPulse, RISING);

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

  if (now - lastSpeedSend > 1000) {
    hitungDanKirimSpeed();
    lastSpeedSend = now;
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

    if (!motorAktif) {
      motor.stop();
      targetSpeedKmh = 0;
    }

    Serial.println("[ESP32] Motor " + String(motorAktif ? "ON" : "OFF"));
  }

  http.end();
}

void cekTargetKecepatan() {
  if (!motorAktif) {
    motor.stop();
    targetSpeedKmh = 0;
    return;
  }

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
    motor.setSpeed(duty);
    motor.forward();

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

void hitungDanKirimSpeed() {
  noInterrupts();
  int count = pulseCount;
  pulseCount = 0;
  interrupts();

  float rotPerSec = count / pulsesPerRevolution;
  float speed = rotPerSec * wheelCircumference * 3.6;

  HTTPClient http;
  http.begin(String(server) + "/speed");
  http.addHeader("Content-Type", "application/json");

  String payload = String("{\"speed\": ") + String(speed, 2) + "}";

  int httpCode = http.POST(payload);

  if (httpCode > 0) {
    Serial.println("[ESP32] Speed sent: " + String(speed, 2) + " km/h");
  } else {
    Serial.println("[ESP32] Failed to send speed");
  }

  http.end();
}
