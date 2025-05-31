// ===== KONFIGURASI PIN & ENCODER =====
const int encoderPinA = 25;            // Gunakan pin dengan pull-up internal (misal GPIO 25)
const int pulsesPerRevolution = 360;   // Encoder Anda: 360 PPR

volatile int pulseCount = 0;
volatile unsigned long lastInterruptTime = 0;
unsigned long lastReportTime = 0;

// ===== ISR dengan Debounce =====
void IRAM_ATTR handleEncoder() {
  unsigned long now = micros();
  if (now - lastInterruptTime > 1000) { // Debounce: 1 ms
    pulseCount++;
    lastInterruptTime = now;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(encoderPinA, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(encoderPinA), handleEncoder, RISING);
  Serial.println("⏱️  Mulai pembacaan RPM dari encoder...");
}

void loop() {
  unsigned long now = millis();
  if (now - lastReportTime >= 1000) { // Hitung per 1 detik
    noInterrupts();
    int pulses = pulseCount;
    pulseCount = 0;
    interrupts();

    float revolutions = pulses / (float)pulsesPerRevolution;
    float rpm = revolutions * 60.0;

    Serial.print("RPM: ");
    Serial.println(rpm);

    lastReportTime = now;
  }
}
