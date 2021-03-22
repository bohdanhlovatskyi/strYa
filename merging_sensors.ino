#include <Wire.h>
// gyroscope libraries
#include <Adafruit_Sensor.h>
#include <Adafruit_L3GD20_U.h>

// compass and ax libraries
#include <LSM303.h>


/* Assign a unique ID to this sensor at the same time */
Adafruit_L3GD20_Unified gyro = Adafruit_L3GD20_Unified(20);

// compass variables
LSM303 compass;
// these should be specified after calibration, so perhaps there is a point to make calibrations sometimes
LSM303::vector<int16_t> running_min = {32767, 32767, 32767}, running_max = {-32768, -32768, -32768};
char report[80];


void setup(void) 
{
  Serial.begin(9600);
  Wire.begin();
  
  gyro_setup();
  compass_setup();

}

void compass_setup(void) {
  compass.init();
  compass.enableDefault();
}

void compass_event(void) {
  float heading = compass.heading();
  compass.read();

  snprintf(report, sizeof(report), "A: %6d %6d %6d    M: %6d %6d %6d",
    compass.a.x, compass.a.y, compass.a.z,
    compass.m.x, compass.m.y, compass.m.z);

  Serial.print("H: "); Serial.print(heading); Serial.print("  ");
  Serial.print(report); Serial.print(" ");
}

void gyro_setup(void) {
  /* Enable auto-ranging */
  gyro.enableAutoRange(true);
  
  /* Initialise the sensor */
  if(!gyro.begin())
  {
    /* There was a problem detecting the L3GD20 ... check your connections */
    Serial.println("Ooops, no L3GD20 detected ... Check your wiring!");
    while(1);
  }
  
  /* Display some basic information on this sensor */
  // displaySensorDetails();
}

void gyro_event(void) {
  /* Get a new sensor event */ 
  sensors_event_t event; 
  gyro.getEvent(&event);
 
  /* Display the results (speed is measured in rad/s) */

  Serial.print("G: "); Serial.print(event.gyro.x); Serial.print("  ");
  Serial.print(event.gyro.y); Serial.print("  ");
  Serial.print(event.gyro.z); Serial.print("  ");
  Serial.println("rad/s ");
}

void loop(void) 
{
  gyro_event();
  compass_event();
  delay(250);
}