#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
//#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>
#include <time.h>

// ===========================
// KONFIGURASI WIFI & SERVER
// ===========================
const char* ssid = "Redmi";
const char* password = "12345678";
//const char* server = "https://luminolynx.my.id"; // Domain
const char* server = "http://192.168.225.106:8000"; // 

// ===========================
// KONFIGURASI PIN 
// ===========================
const int RPWM_PIN = 5;    // PWM kanan (gerak maju)
const int LPWM_PIN = 18;   // PWM kiri (gerak mundur, set 0 untuk maju)
const int R_EN = 21;
const int L_EN = 22;
const int pinRelayMotor = 2; // Pin relay untuk menghidupkan motor
const int pinRelayLampu = 14; // Pin relay untuk lampu
const int pinServoBrake = 23; // Pin untuk servo brake
const int pinRelayKipas = 19; // Pin relay untuk kipas
const int encoderPinA = 34; // Pin A rotary encoder

// ===========================
// VARIABEL
// ===========================
float targetSpeedKmh = 0;
bool motorAktif = false;
bool lampuNyala = false;
bool manualBrakeActive = false; // Status manual brake
volatile int pulseCount = 0; // Variabel untuk menghitung puls
unsigned long lastSpeedCheck = 0;
unsigned long lastLampuCheck = 0;
unsigned long lastMotorStatusCheck = 0;
unsigned long lastManualBrakeCheck = 0; // Waktu terakhir cek manual brake
unsigned long lastSpeedSendTime = 0; // Waktu terakhir data kecepatan dikirim
unsigned long checkInterval = 1000; // cek setiap 1 detik
const unsigned long speedSendInterval = 1000; // Interval pengiriman kecepatan (ms)
const unsigned long manualBrakeCheckInterval = 1000; // Interval cek manual brake (ms)

const float wheelCircumference = 0.2; // Ganti dengan keliling roda dalam m
const int pulsesPerRevolution = 360; // Ganti dengan jumlah pulsa per putaran penuh encoder

String motorDirection = "none";
Servo brakeServo; // Servo untuk manual brake

// Tambahkan variabel global di atas setup()
bool lastMotorAktif = false;
bool lastLampuNyala = false;
String lastMotorDirection = "none";
float lastTargetSpeedKmh = -1;
int lastDuty = -1;

void IRAM_ATTR handleEncoder() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);

  // Setup pin enable
  pinMode(R_EN, OUTPUT);
  pinMode(L_EN, OUTPUT);
  pinMode(pinRelayMotor, OUTPUT);
  pinMode(pinRelayLampu, OUTPUT);

  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);
  digitalWrite(pinRelayMotor, LOW); // Pastikan motor mati saat awal
  digitalWrite(pinRelayLampu, LOW); // Pastikan lampu mati saat awal

  // Setup PWM ESP32
  ledcSetup(0, 5000, 8); // channel 0 untuk RPWM
  ledcSetup(1, 5000, 8); // channel 1 untuk LPWM

  ledcAttachPin(RPWM_PIN, 0);
  ledcAttachPin(LPWM_PIN, 1);

  // Setup rotary encoder
  pinMode(encoderPinA, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(encoderPinA), handleEncoder, RISING);

  // Setup servo brake
  brakeServo.attach(pinServoBrake);
  brakeServo.write(0); // Posisi awal servo (tidak aktif)

  // Koneksi WiFi
  WiFi.begin(ssid, password);
  Serial.print("Menghubungkan ke WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nTerhubung ke WiFi!");

  configTime(7 * 3600, 0, "pool.ntp.org", "time.nist.gov"); // GMT+7, sesuaikan zona waktu Anda
  Serial.print("Sinkronisasi waktu NTP...");
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("OK!");
}

void loop() {
  if (millis() - lastSpeedCheck >= checkInterval) {
    cekMotorTargetSpeed();
    lastSpeedCheck = millis();
  }
  if (millis() - lastMotorStatusCheck >= checkInterval) {
    cekStatusMotor();
    lastMotorStatusCheck = millis();
  }
  if (millis() - lastLampuCheck >= checkInterval) {
    cekLampuStatus();
    lastLampuCheck = millis();
  }
  
  if (millis() - lastSpeedSendTime >= speedSendInterval) {
    kirimKecepatanKeServer();
    lastSpeedSendTime = millis();
  }
  
  if (millis() - lastManualBrakeCheck >= manualBrakeCheckInterval) {
    cekManualBrake();
    lastManualBrakeCheck = millis();
  }

  // Panggil pingServer() setiap 2 detik
  static unsigned long lastPing = 0;
  if (millis() - lastPing > 2000) {
    pingServer();
    lastPing = millis();
  }
}

//Trigger Relay Motor
void cekStatusMotor() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/motor_status");
    int code = http.GET();

    if (code == 200) {
      String payload = http.getString();
      bool requestedMotorStatus = payload.indexOf("true") >= 0;
      motorAktif = requestedMotorStatus && !manualBrakeActive;

      digitalWrite(pinRelayMotor, motorAktif ? HIGH : LOW);

      // Log hanya jika status berubah
      if (motorAktif != lastMotorAktif) {
        Serial.println("[ESP32] Motor: " + String(motorAktif ? "ON" : "OFF"));
        lastMotorAktif = motorAktif;
      }
    } else {
      Serial.print("[ESP32] HTTP Error (motor status): ");
      Serial.println(code);
    }

    http.end();
  } else {
    Serial.println("[ESP32] WiFi tidak terhubung!");
  }
}

//Trigger Relay Lampu
void cekLampuStatus() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/lamp_status");
    int code = http.GET();

    if (code == 200) {
      String payload = http.getString();
      lampuNyala = payload.indexOf("true") >= 0;

      digitalWrite(pinRelayLampu, lampuNyala ? HIGH : LOW);

      // Log hanya jika status berubah
      if (lampuNyala != lastLampuNyala) {
        Serial.println("[ESP32] Lampu: " + String(lampuNyala ? "ON" : "OFF"));
        lastLampuNyala = lampuNyala;
      }
    } else {
      Serial.print("[ESP32] HTTP Error (lampu status): ");
      Serial.println(code);
    }

    http.end();
  } else {
    Serial.println("[ESP32] WiFi tidak terhubung!");
  }
}

//Trigger R_EN atau L_EN
void cekMotorDirection() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/motor_direction_status");
    int responseCode = http.GET();

    if (responseCode == 200) {
      String payload = http.getString();
      int idx = payload.indexOf("direction");
      if (idx >= 0) {
        int pos = payload.indexOf(":", idx);
        int quoteStart = payload.indexOf("\"", pos);
        int quoteEnd = payload.indexOf("\"", quoteStart + 1);
        String newDirection = payload.substring(quoteStart + 1, quoteEnd);

        // Log hanya jika arah berubah
        if (newDirection != lastMotorDirection) {
          Serial.println("[ESP32] Direction: " + newDirection);
          lastMotorDirection = newDirection;
        }
        motorDirection = newDirection;
      }
    } else {
      Serial.print("HTTP Error (direction): ");
      Serial.println(responseCode);
    }
    http.end();
  }
}

//Trigger Pulse Motor Drive
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

      int duty = map(targetSpeedKmh * 10, 0, 60, 0, 150);
      duty = constrain(duty, 0, 150);

      // Ambil arah motor sebelum mengatur PWM
      cekMotorDirection();

      // Hanya update PWM dan log jika duty berubah
      if (duty != lastDuty || targetSpeedKmh != lastTargetSpeedKmh) {
        if (motorDirection == "forward") {
          ledcWrite(0, duty);  // RPWM
          ledcWrite(1, 0);     // LPWM
        } else if (motorDirection == "reverse") {
          ledcWrite(0, 0);     // RPWM
          ledcWrite(1, duty);  // LPWM
        } else {
          ledcWrite(0, 0);
          ledcWrite(1, 0);
        }
        Serial.println("[ESP32] Speed: " + String(targetSpeedKmh) +
                       " km/h → PWM: " + String(duty) +
                       " | Direction: " + motorDirection);
        lastDuty = duty;
        lastTargetSpeedKmh = targetSpeedKmh;
      }
    } else {
      Serial.print("HTTP Error (speed): ");
      Serial.println(responseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi tidak terhubung!");
  }
}

// Kirim Kecepatan ke Server
void kirimKecepatanKeServer() {
  static int lastPulseCount = 0;
  int pulseDelta = pulseCount - lastPulseCount;
  lastPulseCount = pulseCount;

  // Hitung kecepatan (m/s)
  float speed = (pulseDelta * wheelCircumference) / pulsesPerRevolution;

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/speed");
    http.addHeader("Content-Type", "application/json");

    // Kirim data kecepatan dalam format JSON
    String payload = "{\"speed\": " + String(speed, 2) + "}";
    int httpResponseCode = http.POST(payload);

    if (httpResponseCode == 200) {
      Serial.println("Kecepatan berhasil dikirim: " + String(speed, 2) + " m/s");
    } else {
      Serial.print("Gagal mengirim data. HTTP Error: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("[ESP32] WiFi tidak terhubung!");
  }
}

void cekManualBrake() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/manual_brake_status");
    int responseCode = http.GET();

    if (responseCode == 200) {
      String payload = http.getString();
      bool brakeStatus = payload.indexOf("true") >= 0; // Sudah benar jika payload JSON mengandung "true"

      if (brakeStatus != manualBrakeActive) {
        manualBrakeActive = brakeStatus;

        if (manualBrakeActive) {
          // Aktifkan manual brake
          brakeServo.write(90); // Posisi servo untuk mengaktifkan brake
          digitalWrite(pinRelayMotor, LOW); // Matikan motor
          Serial.println("[ESP32] Manual Brake: Aktif");
        } else {
          // Nonaktifkan manual brake
          brakeServo.write(0); // Posisi servo untuk menonaktifkan brake
          Serial.println("[ESP32] Manual Brake: Nonaktif");
        }
      }
    } else {
      Serial.print("[ESP32] HTTP Error (manual brake status): ");
      Serial.println(responseCode);
    }

    http.end();
  } else {
    Serial.println("[ESP32] WiFi tidak terhubung!");
  }
}

void pingServer() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(server) + "/esp_ping");
    http.addHeader("Content-Type", "application/json");
    http.POST("{}");
    http.end();
  }
}