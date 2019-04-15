#include <Smartcar.h> 
const unsigned int MAX_DISTANCE = 50;
const int MAX_SPEED = 60; // Max speed for the car forward
const int MIN_SPEED = -40; // Max speed for the car going backwards

//Pins
const int TRIGGER_PIN = 6; //D6
const int ECHO_PIN = 7; //D7

//Controls
int currSpeed = 0;
int alterSpeed = 20; // Will alter speed backwards/forward
const int lDegrees = -75; //degrees to turn left
const int rDegrees = 75; //degrees to turn right

SR04 front(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
BrushedMotor leftMotor(8, 10, 9);
BrushedMotor rightMotor(12, 13, 11);
DifferentialControl control(leftMotor, rightMotor);
SimpleCar car(control);

void setup() {
  Serial.begin(9600);
}

void loop() {
  int distance = front.getDistance();
  Serial.print(front.getDistance());

  if(distance < 20 && distance > 0){ 
    car.setSpeed(-30); // Car will move backwards so that the user can start controlling it again
    car.setAngle(0);
  }
  
if (Serial.available()) {
    char input = ' ';
    input = Serial.read(); //read everything that has been received so far and log down the last entry
    Serial.print(input);


  
    switch (input) {
      case 'w': //go ahead
      if(currSpeed > MAX_SPEED){ // If max_speed has already been achieved, just keep that speed. 
        car.setSpeed(MAX_SPEED);
        currSpeed = MAX_SPEED; 
      }else{
       car.setSpeed(currSpeed += alterSpeed);
       car.setAngle(0);
      }
        break;
       
      case 's': //go back
      if (currSpeed < MIN_SPEED){
        car.setSpeed(MIN_SPEED);
        currSpeed = MIN_SPEED;
        }else{
        car.setSpeed(currSpeed -= alterSpeed);
        car.setAngle(0);
        }
        break;
        
      case 'a': // Turn left with a 75 degrees angle
        car.setSpeed(currSpeed);
        car.setAngle(lDegrees);
        break;
        
      case 'd': //turn right with a 75 degrees angle 
        car.setSpeed(currSpeed);
        car.setAngle(rDegrees);
        break;
        
      case 'q': //stop
        car.setSpeed(0);
        car.setAngle(0);
        currSpeed = 0;
        break;
    }
   }
}
