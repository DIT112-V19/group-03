#include <Smartcar.h> 
const unsigned int MAX_DISTANCE = 50;
const int MAX_SPEED = 60; // Max speed for the car forward
const int MIN_SPEED = -40; // Max speed for the car going backwards

//Pins
const int TRIGGER_PIN = 6; //D6
const int ECHO_PIN = 7; //D7

//Controls
int slowSpeed = 20;
int medSpeed = 40;
int highSpeed = 60;
int slowBackSpeed = -30;
int medBackSpeed = -50;
int standStill = 0;
const int beginDegrees = 0;
const int lBigDegrees = -75; //degrees to turn left
const int rBigDegrees = 75; //degrees to turn right
const int lSmallDegrees = -45;
const int rSmallDegrees = 45;
int distance;

SR04 front(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);
BrushedMotor leftMotor(8, 10, 9);
BrushedMotor rightMotor(12, 13, 11);
DifferentialControl control(leftMotor, rightMotor);
SimpleCar car(control);

void setup() {
  Serial.begin(9600);
}

void loop() {
  distance = front.getDistance();
  //Serial.print(front.getDistance());

  if(distance < 20 && distance > 0){ 
    car.setSpeed(-30); // Car will move backwards so that the user can start controlling it again
    
    car.setAngle(0);
  }
  
  if (Serial.available()) {
   
    char input = Serial.read(); //read everything that has been received so far and log down the last entry
    Serial.print(input);
  
    switch (input) {
      // Decided to make the buttons purely directional instead and use a slider for speed.
      case 'w': // Set angle to zero for going backwards or forward
       car.setAngle(beginDegrees);
        break;
        
      case 'a': // Turn left with a 75 degrees angle
        car.setAngle(lBigDegrees);
        break;
        
      case 'd': //turn right with a 75 degrees angle 
        car.setAngle(rBigDegrees);
        break;
      
      case 's': // Backwards angle, not really nessecary but will keep for clarity
        car.setAngle(beginDegrees);
        break;
      
      case 'q': 
        car.setAngle(lSmallDegrees); // Turning right, but only 45 degrees
        break;
      case 'e':
        car.setAngle(rSmallDegrees); // Turning left, but but only 45 degrees
        break;
        
      case 'z':
        car.setAngle(lSmallDegrees); // Turning left backwards
        break;

      case 'x': // Turning right backwards
        car.setAngle(rSmallDegrees);
        break;
      
      case 'r': //stop (Car can now also be stopped with the slider but stop button is kept for security measures.)
        car.setSpeed(0);
        break;
        
      case '1':                    
        car.setSpeed(highSpeed);  // Moving forward with slow speed
        break;
    
      case '2':
        car.setSpeed(medSpeed); // Moving forward with medium speed
        break;
    
      case '3':
        car.setSpeed(slowSpeed); // Moving forward with high speed
        break;

      case '4':
        car.setSpeed(standStill); // Set's the speed to 0
        break;
        
      case '5':
        car.setSpeed(slowBackSpeed); // Moving backwards with slow speed
        break;
    
      case '6':
        car.setSpeed(medBackSpeed); // Moving backwards with high speed
        break;
    }
  }
}
