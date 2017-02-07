#include <PID_v1.h>
#include <SoftwareSerial.h>
#include <math.h>

#define LEDPin 13
#define CWPin 4
#define CCWPin 5
#define CWPin2 6
#define CCWPin2 7

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
volatile double angle = 0.0;
short currentdirection2 = CLOCKWISE;
long previousPos2 = 0;
volatile double angle2 = 0.0;
unsigned long curr_time;
unsigned long start_time = millis();
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
};
/*===============================*/
unsigned long tick_start = millis();
unsigned long tickms = 10;
unsigned long curr_tick;

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
  pinMode(CCWPin, OUTPUT);
  pinMode(CWPin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(ENCODERAPIN),ISR_GPIO, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODERBPIN),ISR_GPIO2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODERAPIN2),ISR_GPIO3, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODERBPIN2),ISR_GPIO4, CHANGE);
  while(!Serial){
  }
  delay(100);
}

void Add_Padding(int padding, unsigned int data)
{
  if (padding == 2)
  {
    Serial.print("00");
    Serial.print(data,HEX);
  }
  else if(padding == 1)
  {
    Serial.print("0");
    Serial.print(data, HEX);
  }
  else
  {
    Serial.print(data,HEX);
  }
}

void Send_Data(int value)
{
    if(value < 16){
      Add_Padding(2,value );   
    }
    else if (value  < 256){
      Add_Padding(1,value ); 
    }
    else{
      Add_Padding(0,value ); 
    }  
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

void loop() {

#ifndef DEBUG
  curr_tick = millis();
  if(!pause){
    if(curr_tick-tickms >= tick_start){
      if(previousPos != encoderPos){
        Send_Message(encoderleft, encoderPos); 
        previousPos = encoderPos;
      }
      if(previousPos2 != encoderPos2){
        Send_Message(encoderright, encoderPos2); 
        previousPos2 = encoderPos2;
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
      digitalWrite(CWPin, LOW);
      digitalWrite(CCWPin, LOW);
      digitalWrite(CWPin2, LOW);
      digitalWrite(CCWPin2, LOW);       
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
          Send_Message(desiredleft, desired_angle1);
          desired_angle1 -= angle;
          if (desired_angle1 < 0)
            direction1 = CLOCKWISE;
          else
            direction1 = COUNTERCLOCKWISE;
          state = 2;
        }
        else if(state == 2){
          desired_angle2 = incomingByte;
          Send_Message(desiredright, desired_angle2);
          desired_angle2 -= (180-angle2);
          if (desired_angle2 > 0)
            direction2 = CLOCKWISE;
          else
            direction2 = COUNTERCLOCKWISE;
          state = 3;
        }
        else if(state == 3){
          if(incomingByte == 0xFA){
            digitalWrite(LEDPin, HIGH);
            state = 0;
          }
        }
      }
    }

  if(intersect){
    if(direction1 == CLOCKWISE){ //turn motor1 clockwise
      analogWrite(CWPin, abs(desired_angle1)*20 < 255? abs(desired_angle1)*20 : 255);
      digitalWrite(CCWPin, LOW);
    }
    else{ //turn motor1 counterclockwise
      analogWrite(CCWPin, abs(desired_angle1)*20 < 255? abs(desired_angle1)*20 : 255);
      digitalWrite(CWPin, LOW);
    }
    if(direction2 == CLOCKWISE){ //turn motor2 clockwise
      analogWrite(CWPin2, abs(desired_angle2)*20 > 255? abs(desired_angle2)*20 : 255);
      digitalWrite(CCWPin2, LOW);
    }
    else{ //turn motor2 counterclockwise
      analogWrite(CCWPin2, abs(desired_angle2)*20 > 255? abs(desired_angle2)*20 : 255);
      digitalWrite(CWPin2, LOW);
    }
  }
  
  if(encoderPos > 199 || encoderPos < 1 || encoderPos2 > 199 || encoderPos2 < 1  ){
      digitalWrite(CWPin, LOW);
      digitalWrite(CCWPin, LOW);
      digitalWrite(CCWPin2, LOW);
      digitalWrite(CWPin2, LOW);    
  }
  
#else  
  if((encoderPos != previousPos) || (encoderPos2 != previousPos2)){
    Serial.print(encoderPos);
    Serial.print("\t");
    Serial.println(encoderPos2);
    previousPos = encoderPos;
    previousPos2 = encoderPos2;
  }  
#endif DEBUG

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

