//Arduino RC CAR + LINE FOLLOWING
//Author: Mario Carbone
#include <HCSR04.h>

int ENA = 9; //ENA connected to digital pin 9 @LEFT GEAR
int ENB = 3; //ENB connected to digital pin 3 @RIGHT GEAR
int MOTOR_A1 = 7; // MOTOR_A1 connected to digital pin 7 @IN1
int MOTOR_A2 = 6; // MOTOR_A2 connected to digital pin 6 @IN2
int MOTOR_B1 = 5; // MOTOR_B1 connected to digital pin 5 @IN3
int MOTOR_B2 = 4; // MOTOR_B2 connected to digital pin 4 @IN4

int LEFT = A0; // LEFT sensor connected to analog pin A1
int CENTER= A1; //CENTER sensor connected to analog pin A3
int RIGHT = A2; // RIGHT sensor connected to analog pin A0

HCSR04 hc(10, 11);
int lastAngle = 0;
int brake = 0;
int leftSpeed = 0;
int rightSpeed = 0;
int speed = 0;
int maxSpeed = 254;
int steeringValue = 50;
String steer_side = "CENTER";
int lastSteeringValue = 0;
int distance = 0;
bool stopped = true;
bool braking = false;
bool moving = false;
bool objectDetected = false;
String last_command;
String status;
int sx=analogRead(LEFT);
int dx=analogRead(RIGHT);
int center=analogRead(CENTER);

void setup() {
  
pinMode(ENA, OUTPUT); // initialize ENA pin as an output
pinMode(ENB, OUTPUT); // initialize ENB pin as an output
pinMode(MOTOR_A1, OUTPUT); // initialize MOTOR_A1 pin as an output
pinMode(MOTOR_A2, OUTPUT); // initialize MOTOR_A2 pin as an output
pinMode(MOTOR_B1, OUTPUT); // initialize MOTOR_B1 pin as an output
pinMode(MOTOR_B2, OUTPUT); // initialize MOTOR_B2 pin as an output

pinMode(RIGHT, INPUT); // initialize RIGHT SENSOR pin as an input
pinMode(LEFT, INPUT); // initialize LEFT SENSOR pin as an input
pinMode(CENTER,INPUT); //initialize CENTER SENSOR pin as an input

Serial.begin(9600);

}

int getSideSpeed(int steeringValue, int speed){
  if (steeringValue == 5){
    return 0;
  }
  else if(steeringValue == 4){
     return round(speed*0.2);
  }  
  else if(steeringValue == 3){
     return round(speed*0.4);
  }
  else if(steeringValue == 2){
     return round(speed*0.6);
  }  
  else if(steeringValue == 1){
     return round(speed*0.8);
  }  
  else return speed;
}


bool isMoving(int speed){
  if (speed>0){
    return true;
  }
  else{
    return false;
  }
}

bool isBraking(bool braking){
  return braking;
}

 
void loop() {

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Rimuovi eventuali spazi iniziali o finali

    if (command.startsWith("LEFT")) {
      lastSteeringValue = steeringValue;
      steeringValue = command.substring(4).toInt();
      last_command = command;
      steer_side = command;

      leftSpeed = speed; 
      rightSpeed = getSideSpeed(steeringValue,speed);
     
      analogWrite(ENA, leftSpeed);
      analogWrite(ENB, rightSpeed);
      
    } //TURNING RIGHT

    if (command.startsWith("CENTER")) {
      lastSteeringValue = steeringValue;
      steeringValue = command.substring(6).toInt();
      last_command = command;
      steer_side = command;

      leftSpeed = speed; 
      rightSpeed = speed;
     
      analogWrite(ENA, leftSpeed);
      analogWrite(ENB, rightSpeed);
      
    } //RETURN TO CENTER

    if (command.startsWith("RIGHT")) {
      lastSteeringValue = steeringValue;
      steeringValue = command.substring(5).toInt();
      last_command = command;
      steer_side = command;
      
      leftSpeed = getSideSpeed(steeringValue,speed);
      rightSpeed = speed; 
     
      analogWrite(ENA, leftSpeed);
      analogWrite(ENB, rightSpeed);
      
    } //TURNING LEFT

    else if (command.startsWith("SPEED")) {
      
      tmp_speed = 0;
      if (command.length() >= 5){
        tmp_speed = command.substring(5).toInt();
        if(tmp_speed > maxSpeed){
          tmp_speed = maxSpeed
        }
      }
      last_command = command;
      speed = tmp_speed;
 
      leftSpeed = speed;
      rightSpeed = speed;
      analogWrite(ENA, leftSpeed);
      analogWrite(ENB, rightSpeed);

      digitalWrite(MOTOR_A1, HIGH);
      digitalWrite(MOTOR_A2, LOW);
      digitalWrite(MOTOR_B1, LOW);
      digitalWrite(MOTOR_B2, HIGH);

    } //SPEED
    
    else if (command.startsWith("BACK")) {
      speed = command.substring(4).toInt();

      last_command = command;//(String)"BACKWARD("+command.substring(8).toInt()+")";
      leftSpeed = speed;
      rightSpeed = speed;
      analogWrite(ENA, leftSpeed);  
      analogWrite(ENB, rightSpeed);

      digitalWrite(MOTOR_A1, LOW);
      digitalWrite(MOTOR_A2, HIGH);
      digitalWrite(MOTOR_B1, HIGH);
      digitalWrite(MOTOR_B2, LOW);

    } //BACKWARD

    else if (command.startsWith("STOP")){
        last_command = command;
        speed = 0;
        leftSpeed = speed;
        rightSpeed = speed;
        braking = true;
        stopped = true;
        analogWrite(ENA, leftSpeed);
        analogWrite(ENB, rightSpeed); 

    } //STOP
    
    else if (command.startsWith("STATUS")){
        //last_command = command;
        sx=analogRead(LEFT);
        dx=analogRead(RIGHT);
        center=analogRead(CENTER);
        distance = hc.dist();
        moving = isMoving(speed);
        braking = false;

        Serial.println("{\"speed\":" + String(speed) + ",\"speed_left_side\":" + String(leftSpeed)
                      + ",\"speed_right_side\":" + String(rightSpeed) + ",\"steer_angle\":" + String(steeringValue) 
                      + ",\"last_angle\":" + String(lastAngle) + ",\"ir_left\":" + String(sx) 
                      + ",\"ir_center\":" + String(center) + ",\"ir_right\":" + String(dx) 
                      + ",\"distance\":" + String(distance) + ",\"braking\":" + String(braking) 
                      + ",\"moving\":" + String(moving) + ",\"last_command\":\"" +last_command + "\"}");
      } //STATUS
      
    else {
      Serial.println("Command not recognized");
    }

  }//serial avaiable

} //loop
  