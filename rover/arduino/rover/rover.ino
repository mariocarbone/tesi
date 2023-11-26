//Arduino RC CAR + LINE FOLLOWING
//Author: Mario Carbone
#include <HCSR04.h>
#define LINE HIGH
#define NOLINE LOW
#define GO_AHEAD 1
#define GO_LEFT 2
#define GO_RIGHT 3
#define STOP 4
#define GO_POWERLEFT 5
#define GO_POWERRIGHT 6
#define LAST_RIGHT 7
#define LAST_LEFT 8
#define LAST_CENTER 9   
#define LAST_ALL 10

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
int brake = 0;
int leftSpeed = 0;
int rightSpeed = 0;
int speed = 0;
int last_speed = 0;
int maxSpeed = 254;
int steeringValue = 0;
String steer_side = "CENTER";
int lastSteeringValue = 0;
int distance = 0;
bool stopped = true;
bool braking = false;
bool moving = false;
bool on_track = false;
bool objectDetected = false;
bool object_in_front = true;
String last_command = "STATUS";
String status;
int sx=analogRead(LEFT);
int dx=analogRead(RIGHT);
int center=analogRead(CENTER);

//Nuova Linea
byte leftSensor = digitalRead(LEFT);
byte centerSensor = digitalRead(CENTER);
byte rightSensor = digitalRead(RIGHT);
bool lineFollowingMode = false;
byte lastSensorLine = LAST_CENTER;
byte prevSensorLine = LAST_CENTER; 

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

byte determineDirection(byte lastLine, byte prevLine) {
  if (lastLine == LAST_CENTER) {
    return GO_AHEAD;

  } else if (lastLine == LAST_LEFT) {
    if (prevLine == LAST_CENTER) {
      return GO_RIGHT;
    } else {
      return GO_LEFT;
    }

  } else if (lastLine == LAST_RIGHT) {
    if (prevLine == LAST_CENTER) {
      return GO_LEFT;
    } else {
      return GO_RIGHT;
    }
  } else {
    if (prevLine == LAST_LEFT) {
      return GO_RIGHT;
    } else if (prevLine == LAST_RIGHT) {
      return GO_LEFT;
    } else {
      return STOP; 
    }
  }
}
void loop() {

  distance = hc.dist();

  if (distance < 15) {
      // Se la distanza è minore di 15 cm, ferma il veicolo
      speed = 0;
      leftSpeed = 0;
      rightSpeed = 0;
      braking = true;
      stopped = true;
      object_in_front = true;
      analogWrite(ENA, leftSpeed);
      analogWrite(ENB, rightSpeed);

      if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim(); 
        if (command.startsWith("STATUS")) {
          
          //Rispondo solo al comando STATUS
          sx=digitalRead(LEFT);
          dx=digitalRead(RIGHT);
          center=digitalRead(CENTER);
          on_track = center == HIGH;
          //distance = hc.dist();
          moving = isMoving(speed);
          braking = false;
          //speed_ms = ;
          
          Serial.println("{\"speed\":" + String(speed) + ",\"speed_left_side\":" + String(leftSpeed)
                        + ",\"speed_right_side\":" + String(rightSpeed) + ",\"steer_side_value\":" + String(steeringValue) 
                        + ",\"steer_side\":\""+ String(steer_side) + "\",\"line_following_mode\":" + lineFollowingMode
                        + ",\"ir_left\":" + String(sx) + ",\"ir_center\":" + String(center) + ",\"on_track\":" + on_track
                        + ",\"ir_right\":" + String(dx) + ",\"distance\":" + String(distance) + ",\"stopped\":" + stopped
                        + ",\"braking\":" + braking + ",\"moving\":" + moving + ",\"object_in_front\":" + object_in_front 
                        + ",\"last_command\":\"" +String(last_command)+ "\"}");         
          }
      }
      return; // Ritorno all'inizio del loop
  } //distance < 20s

  if (lineFollowingMode) {
      
      // Aggiorno il valore dei sensori
      leftSensor = digitalRead(LEFT);
      centerSensor = digitalRead(CENTER);
      rightSensor = digitalRead(RIGHT);
    
      prevSensorLine = lastSensorLine; // Memorizza l'ultima lettura

      if (leftSensor == LINE && centerSensor == NOLINE && rightSensor == NOLINE) {
        lastSensorLine = LAST_LEFT;
      } else if (centerSensor == LINE && leftSensor == NOLINE && rightSensor == NOLINE) {
        lastSensorLine = LAST_CENTER;
      } else if (rightSensor == LINE && leftSensor == NOLINE && centerSensor == NOLINE) {
        lastSensorLine = LAST_RIGHT;
      } else if (rightSensor == LINE && leftSensor == LINE && centerSensor == LINE) {
        lastSensorLine = LAST_ALL;
      } else {
        // Nessuna linea rilevata, mantenere l'ultima lettura
      }

      //Calcolo la direzione
      byte goDirection = determineDirection(lastSensorLine, prevSensorLine);

      //Interpreto la direzione ottenuta
      switch (goDirection) {
        case GO_AHEAD:
          leftSpeed = speed;
          rightSpeed = speed; 
          steer_side = "CENTER";
          analogWrite(ENA, leftSpeed);
          analogWrite(ENB, rightSpeed);
          break;
        case GO_LEFT:
          leftSpeed = getSideSpeed(5,speed);
          rightSpeed = speed; 
          steer_side = "LEFT5";
          analogWrite(ENA, leftSpeed);
          analogWrite(ENB, rightSpeed);
          break;
        case GO_RIGHT:
          leftSpeed = speed;
          rightSpeed = getSideSpeed(5,speed); 
          steer_side = "RIGHT5";
          analogWrite(ENA, leftSpeed);
          analogWrite(ENB, rightSpeed);
          break;
        case STOP:
          speed = 0;
          leftSpeed = speed;
          rightSpeed = speed;
          braking = true;
          stopped = true;
          analogWrite(ENA, leftSpeed);
          analogWrite(ENB, rightSpeed); 
          break;
        case GO_POWERLEFT:
          leftSpeed = getSideSpeed(5,speed);
          rightSpeed = speed; 
          steer_side = "LEFT5";
          analogWrite(ENA, leftSpeed);
          analogWrite(ENB, rightSpeed);
          break;
        case GO_POWERRIGHT:
          leftSpeed = speed;
          rightSpeed = getSideSpeed(5,speed); 
          steer_side = "RIGHT5";
          analogWrite(ENA, leftSpeed);
          analogWrite(ENB, rightSpeed);
          break;
      }

    }//Line Following Mode 

    //Comandi Seriale
    if (Serial.available() > 0) {
      String command = Serial.readStringUntil('\n');
      command.trim(); // Rimuovi eventuali spazi iniziali o finali
      //Serial.println("COMANDO RICEVUTO: "+command);

      if (command.startsWith("LEFT")) {
        lastSteeringValue = steeringValue;
        steeringValue = command.substring(4).toInt();
        last_command = command;
        steer_side = command;

        leftSpeed = getSideSpeed(steeringValue,speed);
        rightSpeed = speed; 
      
        analogWrite(ENA, leftSpeed);
        analogWrite(ENB, rightSpeed);
        
      } //TURNING LEFT

      else if (command.startsWith("CENTER")) {
        lastSteeringValue = steeringValue;
        steeringValue = command.substring(6).toInt();
        last_command = command;
        steer_side = command;

        leftSpeed = speed; 
        rightSpeed = speed;
      
        analogWrite(ENA, leftSpeed);
        analogWrite(ENB, rightSpeed);
        
      } //RETURN TO CENTER

      else if (command.startsWith("RIGHT")) {
        lastSteeringValue = steeringValue;
        steeringValue = command.substring(5).toInt();
        last_command = command;
        steer_side = command;
        

        leftSpeed = speed;
        rightSpeed = getSideSpeed(steeringValue,speed);

        analogWrite(ENA, leftSpeed);
        analogWrite(ENB, rightSpeed);
        
      } //TURNING LEFT

      else if (command.startsWith("SPEED")) {
        
        int tmp_speed = 0;
        if (command.length() >= 5){
          tmp_speed = command.substring(5).toInt();
          if(tmp_speed > maxSpeed){
            tmp_speed = maxSpeed;
          }
          else if(tmp_speed == 0){
            stopped = true;
          }
        }
        last_command = command;
        last_speed = speed;
        speed = tmp_speed;

        if(last_command.startsWith("SPEED") && tmp_speed < last_speed){
          if(speed < last_speed){
            braking = true;
          }
          else{
            braking = false;
          }
        }

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
          //braking = true;
          stopped = true;
          analogWrite(ENA, leftSpeed);
          analogWrite(ENB, rightSpeed); 

      } //STOP
      
      else if (command.startsWith("STATUS")){
          //last_command = command;
          //sx=analogRead(LEFT);
          //dx=analogRead(RIGHT);
          //center=analogRead(CENTER);
          //distance = hc.dist();
          sx=digitalRead(LEFT);
          dx=digitalRead(RIGHT);
          center=digitalRead(CENTER);
          moving = isMoving(speed);
          //braking = false;
          //speed_ms = ;


          Serial.println("{\"speed\":" + String(speed) + ",\"speed_left_side\":" + String(leftSpeed)
                        + ",\"speed_right_side\":" + String(rightSpeed) + ",\"steer_side_value\":" + String(steeringValue) 
                        + ",\"steer_side\":\""+ String(steer_side) + "\",\"line_following_mode\":" + lineFollowingMode
                        + ",\"ir_left\":" + String(sx) + ",\"ir_center\":" + String(center) + ",\"on_track\":" + on_track
                        + ",\"ir_right\":" + String(dx) + ",\"distance\":" + String(distance) + ",\"stopped\":" + stopped
                        + ",\"braking\":" + braking + ",\"moving\":" + moving + ",\"object_in_front\":" + object_in_front 
                        + ",\"last_command\":\"" +String(last_command)+ "\"}");  
      } //STATUS

      else if (command.startsWith("STARTSELF")) {
        
        int tmp_speed = 0;
        if (command.length() >= 9){
          tmp_speed = command.substring(9).toInt();
          if(tmp_speed > maxSpeed){
            tmp_speed = maxSpeed;
          }
          else if(tmp_speed == 0){
            stopped = true;
          }
        }
        last_command = command;
        last_speed = speed;
        speed = tmp_speed;

        lineFollowingMode = true;

        leftSpeed = speed;
        rightSpeed = speed;
        analogWrite(ENA, leftSpeed);
        analogWrite(ENB, rightSpeed);

        digitalWrite(MOTOR_A1, HIGH);
        digitalWrite(MOTOR_A2, LOW);
        digitalWrite(MOTOR_B1, LOW);
        digitalWrite(MOTOR_B2, HIGH);

      } //SELF DRIVING

      else if (command.startsWith("STOPSELF")){
          last_command = command;
          speed = 0;
          leftSpeed = speed;
          rightSpeed = speed;
          lineFollowingMode = false;
          //braking = true;
          stopped = true;
          analogWrite(ENA, leftSpeed);
          analogWrite(ENB, rightSpeed); 

      } //STOPSELF
        
      //else {
      //  Serial.println("Command not recognized");
      //}

    }//serial avaiable

} //loop
  