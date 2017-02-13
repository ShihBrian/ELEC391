#include <PID_v1.h>
#include <SoftwareSerial.h>
#include <math.h>

#define LEDPin 13
#define CWPinL 4
#define CCWPinL 5
#define CWPinR 6
#define CCWPinR 7

//#define DEBUG
SoftwareSerial mySerial(10,11);
/*===============================*/
//Globals for optical encoder
#define ENCODERAPIN 2 //interrupt
#define ENCODERBPIN 3 //can be interrupt for better performance Pin 2, 3, 18, 19, 20, 21
#define ENCODERAPIN2 18
#define ENCODERBPIN2 19
#define CPR 400 //400 ticks per 360 degrees
#define CLOCKWISE 1
#define COUNTERCLOCKWISE 2
volatile long encoderPos = 100.0;
volatile long encoderPos2 = 100.0;
volatile long interruptsReceived = 0;
volatile long interruptsReceived2 = 0;
short currentdirection = CLOCKWISE;
long previousPos = 0;
volatile double angle = 90.0;
short currentdirection2 = CLOCKWISE;
long previousPos2 = 0;
volatile double angle2 = 90.0;
/*===============================*/

/*===============================*/
//Communication globals
unsigned int startbyte = 0xFF;
unsigned int endbyte = 0xFE;
unsigned int incomingByte = 0;
int state = 0;

enum MsgType{
  encoderleft = 1,
  encoderright = 2,
  desiredleft = 3,
  desiredright = 4,
  debug = 5,
};
/*===============================*/

/*===============================*/
//PID globals
float Kp = 10;
float Ki = 0;
float Kd = 0;
double Desired1,PIDOutput1;
double Desired2,PIDOutput2;
double Actual1 = 90.0;
double Actual2 = 90.0;
PID PID1(&Actual1, &PIDOutput1, &Desired1, Kp, Ki, Kd, DIRECT);
PID PID2(&Actual2, &PIDOutput2, &Desired2, Kp, Ki, Kd, DIRECT);
const int sampleRate = 10; // Variable that determines how fast our PID loop runs
const long serialPing = 1000;
unsigned long now = 0;
unsigned long lastMessage = 0;
/*===============================*/

unsigned long tick_start = millis();
unsigned long tickms = 10;
unsigned long curr_tick;
unsigned long curr_time;
unsigned long start_time = millis();
bool pause = false;
bool intersect = false;
int desired_angle1 = 0;
int desired_angle2 = 0;
int direction1;
int direction2;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(10);
  pinMode(ENCODERAPIN, INPUT);
  pinMode(ENCODERBPIN, INPUT);
  pinMode(ENCODERAPIN2, INPUT);
  pinMode(ENCODERBPIN2, INPUT);
  pinMode(LEDPin, OUTPUT);
  pinMode(CCWPinL, OUTPUT);
  pinMode(CWPinL, OUTPUT);
  pinMode(CCWPinR, OUTPUT);
  pinMode(CWPinR, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(ENCODERAPIN),ISR_GPIO, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODERBPIN),ISR_GPIO2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODERAPIN2),ISR_GPIO3, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODERBPIN2),ISR_GPIO4, CHANGE);
  PID1.SetMode(AUTOMATIC);
  PID2.SetMode(AUTOMATIC);
  PID1.SetSampleTime(sampleRate);
  PID2.SetSampleTime(sampleRate);
  while(!Serial){
  }
  delay(100);
}

int get_length(long data){
  if(int(data/16) == 0){
    return 1;
  }
  else if(int(data/16) < 16){
    return 2;
  }
  else{
    return 3;
  } 
}

void Send_Message(MsgType type,long data){
  int data_length = get_length(data);
  Serial.print(startbyte, HEX);
  Serial.print(type, HEX);
  Serial.print(data_length, HEX);
  Serial.print(data, HEX);
  Serial.print(endbyte, HEX);
}

void all_off(){
  digitalWrite(CWPinL, LOW);
  digitalWrite(CCWPinL, LOW);
  digitalWrite(CWPinR, LOW);
  digitalWrite(CCWPinR, LOW);      
}

int tries = 0;

void loop() {
#ifndef DEBUG
  curr_tick = millis();
  if(!pause){
    if(curr_tick-tickms >= tick_start){
      if((previousPos != encoderPos)||(previousPos2 != encoderPos2)){
        if(tries == 2){
          Send_Message(encoderleft, encoderPos); 
          previousPos = encoderPos;
          Send_Message(encoderright, encoderPos2); 
          previousPos2 = encoderPos2; 
          tries = 0;
        }
        else{
          tries++;
        }
      }
      tick_start = millis();
    }
  }

  if(Serial.available()>0){
    incomingByte = Serial.read();
    if(incomingByte == 0xFF){     
      intersect = true;
    }
    else if(incomingByte == 0xFD){
      intersect = false;
      state = 0;
      all_off();   
    }
    else if(incomingByte == 0xFE){
      pause = !pause;
    }
    if(intersect){
        if (state == 0){
          if(incomingByte == 0xFB){
            state = 1;
          }
        }
        else if(state == 1){
          desired_angle1 = incomingByte;
          state = 2;
        }
        else if(state == 2){
          desired_angle2 = incomingByte;
          state = 3;
        }
        else if(state == 3){
          if(incomingByte == 0xFA){
            state = 0;
          }
        }
      }
    }

    if(angle > desired_angle1){
      Actual1 = 180-angle;
      Desired1 = 180-desired_angle1;
      direction1 = CLOCKWISE;
    }
    else{
      Actual1 = angle;
      Desired1 = desired_angle1; 
      direction1 = COUNTERCLOCKWISE;
    }
    if(angle2 > desired_angle2){
      Actual2 = 180-angle2;
      Desired2 = 180-desired_angle2;
      direction2 = COUNTERCLOCKWISE;
    }
    else{
      Actual2 = angle2;
      Desired2 = desired_angle2;
      direction2 = CLOCKWISE;
    } 

  if(intersect){
    PID2.Compute();
    PID1.Compute();  //Run the PID loop
    if (direction1 == CLOCKWISE){
      analogWrite(CWPinL, PIDOutput1>100? 100 : PIDOutput1);  //Write out the output from the PID loop to our LED pin
      digitalWrite(CCWPinL, LOW);
    }
    else{
      analogWrite(CCWPinL, PIDOutput1>100? 100 : PIDOutput1);
      digitalWrite(CWPinL, LOW);
    }
    if (direction2 == CLOCKWISE){
      analogWrite(CWPinR, PIDOutput2>100? 100 : PIDOutput2);  //Write out the output from the PID loop to our LED pin
      digitalWrite(CCWPinR, LOW);
    }
    else{
      analogWrite(CCWPinR, PIDOutput2>100? 100 : PIDOutput2);
      digitalWrite(CWPinR, LOW);
    }
    
    if(encoderPos > 199 || encoderPos < 1 || encoderPos2 > 199 || encoderPos2 < 1  ){
      all_off(); 
    }
  }
  
#else  
  static int iter = 0;
  if((encoderPos != previousPos) || (encoderPos2 != previousPos2)){
    /*Serial.print(angle);
    Serial.print("\t");
    Serial.println(angle2);*/
    previousPos = encoderPos;
    previousPos2 = encoderPos2;
  }
    if(angle > desired_angle1){
      Actual1 = 180-angle;
      Desired1 = 180-desired_angle1;
      direction1 = CLOCKWISE;
    }
    else{
      Actual1 = angle;
      Desired1 = desired_angle1; 
      direction1 = COUNTERCLOCKWISE;
    }
    if(angle2 > desired_angle2){
      Actual2 = 180-angle2;
      Desired2 = 180-desired_angle2;
      direction2 = COUNTERCLOCKWISE;
    }
    else{
      Actual2 = angle2;
      Desired2 = desired_angle2;
      direction2 = CLOCKWISE;
    } 

  PID2.Compute();
  PID1.Compute();  //Run the PID loop
  if (direction1 == CLOCKWISE){
    analogWrite(CWPinL, PIDOutput1>50? 50 : PIDOutput1);  //Write out the output from the PID loop to our LED pin
  }
  else{
    analogWrite(CCWPinL, PIDOutput1>50? 50 : PIDOutput1);
  }
  if (direction2 == CLOCKWISE){
    analogWrite(CWPinR, PIDOutput2>50? 50 : PIDOutput2);  //Write out the output from the PID loop to our LED pin
  }
  else{
    analogWrite(CCWPinR, PIDOutput2>50? 50 : PIDOutput2);
  }
  now = millis(); //Keep track of time
  if(now - lastMessage > serialPing) {  //If its been long enough give us some info on serial
    if (iter== 2){
      desired_angle1 = 160;
      desired_angle2 = 68;
      all_off()
    }
    else if(iter ==4){
      desired_angle1 = 68;
      desired_angle2 = 160;     
      all_off()
    }
    else if(iter==6){
      desired_angle1 = 90;
      desired_angle2 = 90;     
      all_off()
    }
    else if(iter ==8){
      desired_angle1 = 121;
      desired_angle2 = 121;     
      all_off()
      iter = 0;
    }
    iter++;   
    // this should execute less frequently
    // send a message back to the mother ship
    Serial.print("Setpoint1 = ");
    Serial.print(Desired1);
    Serial.print(" Input1 = ");
    Serial.print(Actual1);
    Serial.print(" Output1 = ");
    Serial.print(PIDOutput1);
    Serial.print(" Direc1 = ");
    Serial.print(direction1);
    Serial.print(" Setpoint2 = ");
    Serial.print(Desired2);
    Serial.print(" Input2 = ");
    Serial.print(Actual2);
    Serial.print(" Output2 = ");
    Serial.print(PIDOutput2);
    Serial.print(" Direc2 = ");
    Serial.print(direction2);
    Serial.print("\n");
    if (Serial.available() > 0) { //If we sent the program a command deal with it
      for (int x = 0; x < 4; x++) {
        switch (x) {
          case 0:
            Kp = Serial.parseFloat();  
            break;
          case 1:
            Ki = Serial.parseFloat();
            break;
          case 2:
            Kd = Serial.parseFloat();
            break;
          case 3:
            for (int y = Serial.available(); y == 0; y--) {
              Serial.read();  //Clear out any residual junk
            }
            break;
        }
      }
      Serial.print(" Kp,Ki,Kd = ");
      Serial.print(Kp1);
      Serial.print(",");
      Serial.print(Ki1);
      Serial.print(",");
      Serial.println(Kd1);  //Let us know what we just received
      PID1.SetTunings(Kp, Ki, Kd); //Set the PID gain constants and start running
      PID2.SetTunings(Kp, Ki, Kd); //Set the PID gain constants and start running
    }
    
    lastMessage = now; 
    //update the time stamp. 
  }  
#endif //DEBUG

}
void ISR_GPIO()
{
  if (digitalRead(ENCODERAPIN) == HIGH) { 

    // check channel B to see which way encoder is turning
    if (digitalRead(ENCODERBPIN) == LOW) { 
      encoderPos = encoderPos + 1;         // CW
      currentdirection = CLOCKWISE;
    } 
    else {
      encoderPos = encoderPos - 1;         // CCW
      currentdirection = COUNTERCLOCKWISE;
    }
  }

  else   // must be a high-to-low edge on channel A                                       
  { 
    // check channel B to see which way encoder is turning  
    if (digitalRead(ENCODERBPIN) == HIGH) {   
      encoderPos = encoderPos + 1;          // CW
      currentdirection = CLOCKWISE;
    } 
    else {
      encoderPos = encoderPos - 1;          // CCW
      currentdirection = COUNTERCLOCKWISE;
    }
  }
 
 
  // track 0 to 400
  encoderPos = encoderPos % CPR;

  angle = 0.9 * encoderPos;
 
  // track the number of interrupts
  interruptsReceived++;
}

void ISR_GPIO2(){
  // look for a low-to-high on channel B
  if (digitalRead(ENCODERBPIN) == HIGH) {   

   // check channel A to see which way encoder is turning
    if (digitalRead(ENCODERAPIN) == HIGH) {  
      encoderPos = encoderPos + 1;         // CW
      currentdirection = CLOCKWISE;
    } 
    else {
      encoderPos = encoderPos - 1;         // CCW
      currentdirection = COUNTERCLOCKWISE;
    }
  }
  // Look for a high-to-low on channel B
  else { 
    // check channel B to see which way encoder is turning  
    if (digitalRead(ENCODERAPIN) == LOW) {   
      encoderPos = encoderPos + 1;          // CW
      currentdirection = CLOCKWISE;
    } 
    else {
      encoderPos = encoderPos - 1;          // CCW
      currentdirection = COUNTERCLOCKWISE;
    }
  }
  // track 0 to 100
  encoderPos = encoderPos % CPR;

  angle = 0.9 * encoderPos;
 
  // track the number of interrupts
  interruptsReceived++;
}
void ISR_GPIO3()
{
  if (digitalRead(ENCODERAPIN2) == HIGH) { 

    // check channel B to see which way encoder is turning
    if (digitalRead(ENCODERBPIN2) == LOW) { 
      encoderPos2 = encoderPos2 + 1;         // CW
      currentdirection2 = CLOCKWISE;
    } 
    else {
      encoderPos2 = encoderPos2 - 1;         // CCW
      currentdirection2 = COUNTERCLOCKWISE;
    }
  }

  else   // must be a high-to-low edge on channel A                                       
  { 
    // check channel B to see which way encoder is turning  
    if (digitalRead(ENCODERBPIN2) == HIGH) {   
      encoderPos2 = encoderPos2 + 1;          // CW
      currentdirection2 = CLOCKWISE;
    } 
    else {
      encoderPos2 = encoderPos2 - 1;          // CCW
      currentdirection2 = COUNTERCLOCKWISE;
    }
  }
 
 
  // track 0 to 400
  encoderPos = encoderPos % CPR;

  angle2 = 0.9 * encoderPos2;
 
  // track the number of interrupts
  interruptsReceived2++;
}

void ISR_GPIO4(){
  // look for a low-to-high on channel B
  if (digitalRead(ENCODERBPIN2) == HIGH) {   

   // check channel A to see which way encoder is turning
    if (digitalRead(ENCODERAPIN2) == HIGH) {  
      encoderPos2 = encoderPos2 + 1;         // CW
      currentdirection2 = CLOCKWISE;
    } 
    else {
      encoderPos2 = encoderPos2 - 1;         // CCW
      currentdirection2 = COUNTERCLOCKWISE;
    }
  }
  // Look for a high-to-low on channel B
  else { 
    // check channel B to see which way encoder is turning  
    if (digitalRead(ENCODERAPIN2) == LOW) {   
      encoderPos2 = encoderPos2 + 1;          // CW
      currentdirection2 = CLOCKWISE;
    } 
    else {
      encoderPos2 = encoderPos2 - 1;          // CCW
      currentdirection2 = COUNTERCLOCKWISE;
    }
  }
  // track 0 to 100
  encoderPos = encoderPos % CPR;

  angle2 = 0.9 * encoderPos2;
 
  // track the number of interrupts
  interruptsReceived2++;
}
