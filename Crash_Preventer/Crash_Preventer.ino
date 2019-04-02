#include <Smartcar.h>
const unsigned short LEFT_ODOMETER_PIN = 2;
const unsigned short RIGHT_ODOMETER_PIN = 3;
// The ultrasound sensor
const int TRIGGER_PIN = 6; //D6
const int ECHO_PIN = 7; //D7
const unsigned int MAX_DISTANCE = 50;
// The different sensor instantiated 
SR04 front(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
BrushedMotor leftMotor(8, 10, 9);
BrushedMotor rightMotor(12, 13, 11);
DifferentialControl control(leftMotor, rightMotor);
GY50 gyroscope(37);
DirectionlessOdometer leftOdometer(100);
DirectionlessOdometer rightOdometer(100);
SmartCar car(control, gyroscope, leftOdometer, rightOdometer);

void setup() {
  Serial.begin(9600);
  // Initialize the odometers (they won't work otherwise)
  leftOdometer.attach(LEFT_ODOMETER_PIN, []() {
    leftOdometer.update();
  });
  rightOdometer.attach(RIGHT_ODOMETER_PIN, []() {
    rightOdometer.update();
  });

  car.enableCruiseControl();
  car.setSpeed(1); // Maintain a speed of 1 m/sec :)
}

void loop() {
  // Maintain the speed and update the heading
  car.update();
  if (front.getDistance() < 20 && front.getDistance() > 0) {
    car.setSpeed(0);
  }
}
