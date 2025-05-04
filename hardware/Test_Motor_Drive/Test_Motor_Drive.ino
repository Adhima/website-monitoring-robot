// Pin koneksi ESP32 ke BTS7960
#define RPWM  A5     // Pin PWM untuk maju
#define LPWM  A4     // Pin PWM untuk mundur
#define R_EN  2     // Enable kanan
#define L_EN  3    // Enable kiri

void setup() {
  Serial.begin(115200);
  
  pinMode(RPWM, OUTPUT);
  pinMode(LPWM, OUTPUT);
  pinMode(R_EN, OUTPUT);
  pinMode(L_EN, OUTPUT);

  // Aktifkan driver
  digitalWrite(R_EN, HIGH);
  digitalWrite(L_EN, HIGH);

  Serial.println("Mulai Tes Motor BTS7960");
}

void loop() {
  Serial.println("Motor MAJU");
  analogWrite(RPWM, 200);  // PWM kecepatan maju
  analogWrite(LPWM, 0);
  delay(2000);

  Serial.println("BERHENTI");
  analogWrite(RPWM, 0);
  analogWrite(LPWM, 0);
  delay(1000);

  Serial.println("Motor MUNDUR");
  analogWrite(RPWM, 0);
  analogWrite(LPWM, 200);  // PWM kecepatan mundur
  delay(2000);

  Serial.println("BERHENTI");
  analogWrite(RPWM, 0);
  analogWrite(LPWM, 0);
  delay(1000);
}
