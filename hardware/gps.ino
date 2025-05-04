#include <SoftwareSerial.h>
#include <TinyGPS++.h>

TinyGPSPlus gps;
SoftwareSerial gpsSerial(4, 3); // RX, TX ke GPS module

void setup() {
  Serial.begin(9600);
  gpsSerial.begin(9600);
}

void loop() {
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  if (gps.location.isUpdated()) {
    Serial.print("LAT:");
    Serial.print(gps.location.lat(), 6);
    Serial.print(",LON:");
    Serial.println(gps.location.lng(), 6);
  }
}
