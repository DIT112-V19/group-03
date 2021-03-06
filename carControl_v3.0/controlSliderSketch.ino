#include <Smartcar.h> 
const unsigned int MAX_DISTANCE = 50;

//Pins
const int TRIGGER_PIN = 6; //D6
const int ECHO_PIN = 7; //D7

//Controls
// All of these are changable depending on preference
int slowSpeed = 20;
int medSpeed = 40;
int highSpeed = 60;
int slowBackSpeed = -30;
int medBackSpeed = -50;
int standStill = 0;
const int beginDegrees = 0;
const int lDegrees = -75; //degrees to turn left
const int rDegrees = 75; //degrees to turn right
int distance = 1;
boolean obstacleFlag;
int counter = 0;

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

  if (counter > 0){
  counter--;
  }
  if(distance > 20 || distance < 1){
    obstacleFlag = true;
  }

  if(counter == 0 && obstacleFlag && distance < 20 && distance > 0){ 
    car.setSpeed(0); // Car will stop and let the user drive away from the obstacle
    car.setAngle(0);
    obstacleFlag = false;
    counter = 1500;
  }
  
  if (Serial.available()) {
   
    char input = Serial.read(); //read everything that has been received so far and log down the last entry
    Serial.print(input);
  
    switch (input) {
      // Decided to make the buttons purely directional instead and use a slider for speed.
      case 'w': // Set angle to zero for going backwards or forward
       car.setAngle(beginDegrees);
        break;
        
      case 'a': // Turning left
        car.setAngle(lDegrees);
        break;
        
      case 'd': //turning right  
        car.setAngle(rDegrees);
        break;
      
      case 's': // Backwards angle, not really nessecary but will keep for clarity
        car.setAngle(beginDegrees);
        break;
      
      case 'r': //stop (Car can now also be stopped with the slider but stop button is kept for security measures.)
        car.setSpeed(0);
        break;
        
      case '1':
        if(obstacleFlag){                  
        car.setSpeed(highSpeed);  // Moving forward with slow speed
        }
        break;
    
      case '2':
        if(obstacleFlag){
        car.setSpeed(medSpeed); // Moving forward with medium speed
        }
        break;
    
      case '3':
        if(obstacleFlag){
        car.setSpeed(slowSpeed); // Moving forward with high speed
        }
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
