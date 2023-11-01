//Arduino RC CAR + LINE FOLLOWING
//Author: Mario Carbone

int ENA = 9; //ENA connected to digital pin 9 @LEFT GEAR
int ENB = 3; //ENB connected to digital pin 3 @RIGHT GEAR
int MOTOR_A1 = 7; // MOTOR_A1 connected to digital pin 7 @IN1
int MOTOR_A2 = 6; // MOTOR_A2 connected to digital pin 6 @IN2
int MOTOR_B1 = 5; // MOTOR_B1 connected to digital pin 5 @IN3
int MOTOR_B2 = 4; // MOTOR_B2 connected to digital pin 4 @IN4

int LEFT = A0; // LEFT sensor connected to analog pin A1
int CENTER= A1; //CENTER sensor connected to analog pin A3
int RIGHT = A2; // RIGHT sensor connected to analog pin A0

int ingressoSeriale = 0;
String data = "";

int velocita = 0;
int velSinistra = 0;
int velDestra = 0;
int angolo = 0;
int lastAngolo = 0;
int brake = 0;

int leftSpeed = 0;
int rightSpeed = 0;
int speed = 0;
int maxSpeed = 254;
int steeringValue = 0;
int lastSteeringValue = 0;


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

  if (steeringValue == 0 || steeringValue == 100){
    return 0;
  }
  else if(steeringValue == 10 || steeringValue == 90){
     return round(speed*0.2);
  }  
  else if(steeringValue == 20 || steeringValue == 80){
     return round(speed*0.4);
  } 
  else if(steeringValue == 30 || steeringValue == 70){
     return round(speed*0.6);
  }  
  else if(steeringValue == 40 || steeringValue == 60){
     return round(speed*0.8);
  }  
  else return speed;
}
 
void loop() {

  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim(); // Rimuovi eventuali spazi iniziali o finali


    if (comando.startsWith("TRN")) {
        
      lastSteeringValue = steeringValue;
      steeringValue = comando.substring(3).toInt();
      
      if (steeringValue < 50){ //Decremento la velocità del Lato Sinistro
        leftSpeed = getSideSpeed(steeringValue,speed);
        rightSpeed = speed; 
      }
      else if (steeringValue > 50){ //Decremento la veloctià del Lato Destro
        leftSpeed = speed;
        rightSpeed = getSideSpeed(steeringValue,speed);

      }
      else{
          leftSpeed = speed;
          rightSpeed = speed;
      }
     
      
      analogWrite(ENA, leftSpeed);
      analogWrite(ENB, rightSpeed);

      Serial.println("speed:" + String(velocita) + ",speed_left_side:" + String(leftSpeed)
                      + ",speed_right_side:" + String(rightSpeed) + ",steer_angle:" + String(steeringValue) + ",last_angle:" 
                      + String(lastSteeringValue) + ",ir_left:" + String(sx) + ",ir_center:" + String(center) + ",ir_right:"
                      + String(dx) + ",last_command:" + last_command);
      
      
      /*
      lastAngolo = angolo;
      angolo = comando.substring(3).toInt();
      last_command = (String)"TURN("+angolo+")";
      //int angoloAssoluto = abs(angolo);
    
      // Calcolo la differenza di velocità tra i due motori per sterzare
      float percentualeDecremento = map(angoloAssoluto, 0, 45, 0, 100);
      float percentualeVelocita = 1.0 - (percentualeDecremento / 100.00);
      //Serial.println(percentualeDecremento);
      //Serial.println(percentualeVelocita);

      if (angolo <50){
        
        velSinistra = (int)(velocita * percentualeVelocita);
        //Serial.println(velSinistra);
        velDestra = velocita;
        analogWrite(ENA, velSinistra);
        analogWrite(ENB, velocita);

      } else if (angolo==0){
        int velocitaTMP = 0;
        if ( velocita > velDestra ){
          velDestra = velocita;
        }else{
          velSinistra = velocita;
        }
      }
      else{
        
        velDestra= (int)(velocita * percentualeVelocita);
        velSinistra = velocita;
        analogWrite(ENA, velocita);
        analogWrite(ENB, velDestra);
      }

        /*Serial.println("speed:" + String(velocita) + ",speed_left_side:" + String(velSinistra)
                      + ",speed_right_side:" + String(velDestra) + ",steer_angle:" + String(angolo) + ",last_angle:" 
                      + String(lastAngolo) + ",ir_left:" + String(sx) + ",ir_center:" + String(center) + ",ir_right:"
                      + String(dx) + ",last_command:" + last_command);
        */
      
    } else if (comando.startsWith("SPD")) {

      if (comando.length() >= 4){
        speed = comando.substring(3).toInt();
      }
      last_command = (String)"SPEED("+comando.substring(3).toInt()+")";
      speed = comando.substring(3).toInt();
      leftSpeed = speed;
      rightSpeed = speed;
      analogWrite(ENA, leftSpeed);
      analogWrite(ENB, rightSpeed);

      digitalWrite(MOTOR_A1, HIGH);
      digitalWrite(MOTOR_A2, LOW);
      digitalWrite(MOTOR_B1, LOW);
      digitalWrite(MOTOR_B2, HIGH);

      /*Serial.println("speed:" + String(velocita) + ",speed_left_side:" + String(velSinistra)
                    + ",speed_right_side:" + String(velDestra) + ",steer_angle:" + String(angolo) + ",last_angle:" 
                    + String(lastAngolo) + ",ir_left:" + String(sx) + ",ir_center:" + String(center) + ",ir_right:"
                    + String(dx) + ",last_command:" + last_command);
*/
     } else if (comando.startsWith("BAK")) {
      speed = comando.substring(3).toInt();

      last_command = (String)"BACKWARD("+comando.substring(3).toInt()+")";
      leftSpeed = speed;
      rightSpeed = speed;
      analogWrite(ENA, leftSpeed);  
      analogWrite(ENB, rightSpeed);

      digitalWrite(MOTOR_A1, LOW);
      digitalWrite(MOTOR_A2, HIGH);
      digitalWrite(MOTOR_B1, HIGH);
      digitalWrite(MOTOR_B2, LOW);
/*
      Serial.println("speed:" + String(velocita) + ",speed_left_side:" + String(velSinistra)
                    + ",speed_right_side:" + String(velDestra) + ",steer_angle:" + String(angolo) + ",last_angle:" 
                    + String(lastAngolo) + ",ir_left:" + String(sx) + ",ir_center:" + String(center) + ",ir_right:"
                    + String(dx) + ",last_command:" + last_command);               
*/
    } else if (comando.startsWith("STP")){
        last_command = "STOP";
        speed = 0;
        leftSpeed = speed;
        rightSpeed = speed;
        analogWrite(ENA, leftSpeed);
        analogWrite(ENB, rightSpeed);
      }
      
      else if (comando.startsWith("STA")){
        
        last_command = "STATUS";
        sx=analogRead(LEFT);
        dx=analogRead(RIGHT);
        center=analogRead(CENTER);
        
        Serial.println("{\"speed\":" + String(velocita) + ",\"speed_left_side\":" + String(velSinistra)
                      + ",\"speed_right_side\":" + String(velDestra) + ",\"steer_angle\":" + String(angolo) + ",\"last_angle\":" 
                      + String(lastAngolo) + ",\"ir_left\":" + String(sx) + ",\"ir_center\":" + String(center) + ",\"ir_right\":"
                      + String(dx) + ",\"last_command\":\"" + "\""+last_command + "\"}");

        //Serial.println(status);   
      
      }
      else {
      Serial.println("Comando non riconosciuto");
    }

  }
  


  
}