#define RPWM  32     // Pin PWM untuk maju
#define LPWM  4     // Pin PWM untuk mundur
#define R_EN  33     // Enable kanan
#define L_EN  22    // Enable kiri

void setup() {
  Serial.begin(115200);
  
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);
  pinMode(R_EN, OUTPUT);
  pinMode(L_EN, OUTPUT);

  // Aktifkan driver
  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);

  // Setup PWM ESP32
  ledcSetup(0, 5000, 8); // Channel 0, 5 kHz, 8-bit
  ledcSetup(1, 5000, 8); // Channel 1, 5 kHz, 8-bit

  ledcAttachPin(RPWM, 0);
  ledcAttachPin(LPWM, 1);

  Serial.println("Mulai Tes Motor BTS7960 (ESP32)");
}

void loop() {
  Serial.println("Motor MAJU");
  ledcWrite(0, 200);  // PWM maju
  ledcWrite(1, 0);    // PWM mundur
  delay(2000);

  Serial.println("BERHENTI");
  ledcWrite(0, 0);
  ledcWrite(1, 0);
  delay(1000);

  Serial.println("Motor MUNDUR");
  ledcWrite(0, 0);    // PWM maju
  ledcWrite(1, 200);  // PWM mundur
  delay(2000);

  Serial.println("BERHENTI");
  ledcWrite(0, 0);
  ledcWrite(1, 0);
  delay(1000);
}
