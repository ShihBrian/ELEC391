#include <SoftwareSerial.h>
#include <math.h>
#define LEDPin 13
#define CCWPin 4
#define CWPin 5
#define CWPin2 6
#define CCWPin2 7
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
/*===============================*/

double fk_x;
double fk_y;
double arm_length = 55;
double top_angles[3];
unsigned long tick_start = millis();
unsigned long tickms = 10;
unsigned long curr_tick;
int x = 10;
int y = 10;
int dx = 1;
int dy = 0;
int move_speed = 1;
bool pause = false;
int thresholdPos = 0;
bool intersect = false;
int direc = CLOCKWISE;
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

int PowerLevel = 0;
double previous_angle = 0;
int delaytime = 10;

int state = 0;
int desired_angle1 = 0;
int desired_angle2 = 0;
int nextstate = 0;
bool changestate = false;
int direction1;
int direction2;

void loop() {

curr_tick = millis();
  if(!pause){
    if(curr_tick-tickms >= tick_start){
      Send_Data(startbyte);
      Send_Data(encoderPos);
      Send_Data(encoderPos2);
      Send_Data(endbyte);  
      tick_start = millis();
    }
  }

  if(Serial.available()>0){
    incomingByte = Serial.read();
    if(incomingByte == 0xFF){     
      thresholdPos = encoderPos;
      intersect = true;
      direc = currentdirection;
    }
    else if(incomingByte == 0xFD){
      move_speed = incomingByte-48;
      thresholdPos = 0;
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
            nextstate = 1;
            changestate = true;
          }
        }
        else if(state == 1){
          desired_angle1 = incomingByte;
          if (desired_angle1 < angle)
            direction1 = CLOCKWISE;
          else
            direction1 = COUNTERCLOCKWISE;
          nextstate = 2;
          changestate = true;
        }
        else if(state == 2){
          desired_angle2 = incomingByte;
          if (desired_angle2 > (180-angle2))
            direction2 = CLOCKWISE;
          else
            direction2 = COUNTERCLOCKWISE;
          nextstate = 3;
          changestate = true;
        }
        else if(state == 3){
          if(incomingByte == 0xFA){
            digitalWrite(LEDPin, HIGH);
            nextstate = 0;
            changestate = true;
          }
        }
        
        if(changestate){
          state = nextstate;
          changestate = false;
        }
      }
    }

  if(intersect){
    if(direction1 == CLOCKWISE){ //turn motor1 clockwise
      digitalWrite(CWPin, HIGH);
      digitalWrite(CCWPin, LOW);
    }
    else{ //turn motor1 counterclockwise
      digitalWrite(CCWPin, HIGH);
      digitalWrite(CWPin, LOW);
    }
    if(direction2 == CLOCKWISE){ //turn motor2 clockwise
      digitalWrite(CWPin2, HIGH);
      digitalWrite(CCWPin2, LOW);
    }
    else{ //turn motor2 counterclockwise
      digitalWrite(CCWPin2, HIGH);
      digitalWrite(CWPin2, LOW);
    }
  }
  
  if(encoderPos > 199 || encoderPos < 1 || encoderPos2 > 199 || encoderPos2 < 1  ){
      digitalWrite(CWPin, LOW);
      digitalWrite(CCWPin, LOW);
      digitalWrite(CCWPin2, LOW);
      digitalWrite(CWPin2, LOW);    
  }
  
  /*if((encoderPos != previousPos) || (encoderPos2 != previousPos2)){
    Serial.print(encoderPos);
    Serial.print("\t");
    Serial.println(encoderPos2);
    previousPos = encoderPos;
    previousPos2 = encoderPos2;
  }*/

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

