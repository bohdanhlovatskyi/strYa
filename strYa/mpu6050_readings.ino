// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

int led = 13;
int state = 0;

Adafruit_MPU6050 mpu;
Adafruit_MPU6050 mpu1;

void setup(void) {
  Serial.begin(115200);
  while (!Serial)
    delay(10);

   pinMode(led, OUTPUT);

  // Try to initialize!
  if (!mpu.begin(0b1101000)) {
    Serial.println("Failed to find MPU6050 1 chip");
    while (1) {
      delay(10);
    }
  }

  if (!mpu1.begin(0b1101001)) {
    Serial.println("Failed to find MPU6050 2 chip");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_5_HZ);

  mpu1.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu1.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu1.setFilterBandwidth(MPU6050_BAND_5_HZ);

}

void loop() {

  if (Serial.available() > 0) {
    state = Serial.read();
  }

  if (state == '1') {
    digitalWrite(led, HIGH);
    state = 0;
  } else {
    digitalWrite(led, LOW);
    state = 0;
  }
  delay(100);

  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  /* Print out the values */
  // Acceleration - m/s^2
  //Acceleration X:
  Serial.print(a.acceleration.x);
  Serial.print(", ");
  //Acceleration Y:
  Serial.print(a.acceleration.y);
  Serial.print(", ");
  //Acceleration Z:
  Serial.print(a.acceleration.z);
  Serial.print("; ");

  // Rotation - rad/s
  // Rotation X
  Serial.print(g.gyro.x);
  Serial.print(", ");
  // Rotation Y
  Serial.print(g.gyro.y);
  Serial.print(", ");
  // Rotation Z
  Serial.print(g.gyro.z);

  // sperator between two sensors readings
  Serial.print("|");

  sensors_event_t a1, g1, temp1;
  mpu1.getEvent(&a1, &g1, &temp1);


  Serial.print(a1.acceleration.x);
  Serial.print(", ");
  Serial.print(a1.acceleration.y);
  Serial.print(", ");
  Serial.print(a1.acceleration.z);
  Serial.print("; ");

  Serial.print(g1.gyro.x);
  Serial.print(", ");
  Serial.print(g1.gyro.y);
  Serial.print(", ");
  Serial.print(g1.gyro.z);

  Serial.println("");
}