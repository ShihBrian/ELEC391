#include <PID_v1.h>
#include <SoftwareSerial.h>
#include <math.h>

#define CWPinL 4
#define CCWPinL 5
#define CWPinR 6
#define CCWPinR 7

#define REED1 46
#define REED2 47

//#define DEBUG
//#define LOCAL_OUTPUT
SoftwareSerial mySerial(10,11);
/*===============================*/
//Globals for optical encoder
#define CPR 400 //400 ticks per 360 degrees
#define CLOCKWISE 1
#define COUNTERCLOCKWISE 2
volatile long encoderPos = 0;
volatile long encoderPos2 = 0;
short currentdirection = CLOCKWISE;
long previousPos = 0;
volatile double angle = 90.0;
short currentdirection2 = CLOCKWISE;
long previousPos2 = 0;
volatile double angle2 = 90.0;
volatile long countData = 0;
long Pos1offset = 0;
long Pos2offset = 0;
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
float Kp = 100;
float Ki = 0;
float Kd = 10;
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
int rxPID = false;
int PIDrx_count = 0;
int P, I, D;
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
  pinMode(CCWPinL, OUTPUT);
  pinMode(CWPinL, OUTPUT);
  pinMode(CCWPinR, OUTPUT);
  pinMode(CWPinR, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(REED1, INPUT_PULLUP);
  pinMode(REED2, INPUT_PULLUP);
  digitalWrite(9, LOW); // /RST resets the internal counter between runs
  delay(10);
  digitalWrite(9, HIGH); // Stay high for rest of the run
  // Set all pins in PORTA and C (digital pins 22->37) as input pins
  for(int i = 22; i<38; i++) {
    pinMode(i, INPUT);
  }
  // Set pins 5,6,7 in PORT B (digital pins 11->16) as output pins
  for(int j = 11; j<17; j++) {
    pinMode(j, OUTPUT);
    digitalWrite(j, LOW);
    
  }
  PID1.SetMode(AUTOMATIC);
  PID2.SetMode(AUTOMATIC);
  PID1.SetSampleTime(sampleRate);
  PID2.SetSampleTime(sampleRate);
  while(!Serial){ //wait for serial to be initialized
  }
  delay(100);
}

void loop() {
#if !defined(DEBUG) && !defined(LOCAL_OUTPUT) //main loop 
  static int tries = 0;
  curr_tick = millis();
  if(!pause){
    if(curr_tick-tickms >= tick_start){ //run loop every tickms 
      ISR_Counter(); //get new encoder positions
      if((previousPos != encoderPos)||(previousPos2 != encoderPos2)){
        if(tries == 2){ //send message every second encoderPos change
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

  if(Serial.available()>0) {
    incomingByte = Serial.read();
    
    if(rxPID == true){
      if(PIDrx_count == 0){
        P = incomingByte;
      }
      else if(PIDrx_count == 1)
        I = incomingByte;
      else if(PIDrx_count == 2)
        D = incomingByte;
      PIDrx_count++;
      if(PIDrx_count == 3){
        PIDrx_count = 0;
        rxPID = false;
        PID1.SetTunings(P,I,D);
        PID2.SetTunings(P,I,D);
        Send_Message(debug, P);
        Send_Message(debug, I);
        Send_Message(debug, D);
      } 
    }
    
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
    else if(incomingByte == 0xFC){
      rxPID = true;
    }
    
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
    //pass values to PID library to compute output power
    PID_Output(intersect, desired_angle1, desired_angle2);
#endif  
#ifdef DEBUG //for debugging and testing PID
  /*static int iter = 0;
  ISR_Counter();
  PID_Output(true, desired_angle1, desired_angle2);
  
  now = millis(); //Keep track of time
  if(now - lastMessage > serialPing) { //Move arm to new position every serialPing ms
    if (iter== 2){
      desired_angle1 = 160;
      desired_angle2 = 68;
      all_off();
    }
    else if(iter ==4){
      desired_angle1 = 68;
      desired_angle2 = 160;     
      all_off();
    }
    else if(iter==6){
      desired_angle1 = 90;
      desired_angle2 = 90;     
      all_off();
    }
    else if(iter ==8){
      desired_angle1 = 121;
      desired_angle2 = 121;     
      all_off();
      iter = 0;
    }
    iter++;   
    lastMessage = now; 
  }  */
  static bool leftdone = false;
  static bool rightdone = false;
  ISR_Counter();

  if(!leftdone)
    analogWrite(CWPinL, 50);
  if(leftdone && !rightdone)
    analogWrite(CCWPinR, 50);
    
  now = millis(); //Keep track of time
  
  if(now - lastMessage > serialPing) {
    if(!leftdone){
      if(previousPos2 == encoderPos2){
        leftdone = true;
        Pos2offset = encoderPos2 + 5;
      } 
      previousPos2 = encoderPos2;
    }
    if(leftdone){
      if(previousPos == encoderPos){
        rightdone = true;
        Pos1offset = encoderPos -5;
      } 
      previousPos = encoderPos;      
    }
    
    lastMessage = now; 
  } 

  while(1){
    PID_Output(1, 90,90);
  }
  
  
#endif //DEBUG

#ifdef LOCAL_OUTPUT //for outputting encoder information on local arduino serial
  if((encoderPos != previousPos) || (encoderPos2 != previousPos2)){
    Serial.print(angle);
    Serial.print("\t");
    Serial.println(angle2);
    previousPos = encoderPos;
    previousPos2 = encoderPos2;
  }
#endif //LOCAL_OUTPUT
}

void PID_Output(bool flag, int desired_angle1, int desired_angle2){
    if (flag){
      //figure out if desired angle is larger or smaller than actual and set direction to turn motor
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
      //Run PID computation
      PID1.Compute();
      PID2.Compute();
      //Turn on pin according to direction and PID output. Limit to 255 
      if (direction1 == CLOCKWISE){
        analogWrite(CWPinL, PIDOutput1>255? 255 : PIDOutput1);
        digitalWrite(CCWPinL, LOW);
      }
      else{
        analogWrite(CCWPinL, PIDOutput1>255? 255 : PIDOutput1);
        digitalWrite(CWPinL, LOW);
      }
      if (direction2 == CLOCKWISE){
        analogWrite(CWPinR, PIDOutput2>255? 255 : PIDOutput2);
        digitalWrite(CCWPinR, LOW);
      }
      else{
        analogWrite(CCWPinR, PIDOutput2>255? 255 : PIDOutput2);
        digitalWrite(CWPinR, LOW);
      }

      //dont want arm going past 0 or 180 degrees
      if(encoderPos > 199 || encoderPos < 1 || encoderPos2 > 199 || encoderPos2 < 1  ){
        all_off(); 
      }
    }
}

//function to read 32bit data from encoder chip
void ISR_Counter(){
  digitalWrite(13, HIGH); // Set OE to HIGH (disable)
  
  digitalWrite(11, LOW);
  digitalWrite(12, HIGH); // SEL1 = 0 and SEL2 = 1
  
  digitalWrite(13, LOW); // Set OE to LOW (enable)
  byte MSBresult = getbyte();
  byte MSBresult2 = getbyte2();
  
  digitalWrite(11, HIGH);
  digitalWrite(12, HIGH); // SEL1 = 1 and SEL2 = 1
  byte secondResult = getbyte();
  byte secondResult2 = getbyte2();
  
  digitalWrite(11, LOW);
  digitalWrite(12, LOW); // SEL1 = 0 and SEL2 = 0
  byte thirdResult = getbyte();
  byte thirdResult2 = getbyte2();
  
  digitalWrite(11, HIGH);
  digitalWrite(12, LOW); // SEL1 = 1 and SEL2 = 0
  byte LSBresult = getbyte();
  byte LSBresult2 = getbyte2();

  digitalWrite(13, HIGH); // Set OE to HIGH (disable)
  
  encoderPos = Pos1offset+mergeFunc(MSBresult, secondResult, thirdResult, LSBresult);
  encoderPos2 = Pos2offset+mergeFunc(MSBresult2, secondResult2, thirdResult2, LSBresult2);

  angle = (encoderPos *0.9);
  angle2 = (encoderPos2*0.9);
}

//get length of data being sent out
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
//Send message in the following order: startbyte, type, length, data, endbyte
void Send_Message(MsgType type,long data){
  int data_length = get_length(data);
  Serial.print(startbyte, HEX);
  Serial.print(type, HEX);
  Serial.print(data_length, HEX);
  Serial.print(data, HEX);
  Serial.print(endbyte, HEX);
}
//turn all motor control pins off
void all_off(){
  digitalWrite(CWPinL, LOW);
  digitalWrite(CCWPinL, LOW);
  digitalWrite(CWPinR, LOW);
  digitalWrite(CCWPinR, LOW);      
}

//function to get individual bytes from encoder chip
byte getbyte(){
/*Get stable data for the most significant byte of countData*/
  byte MSBold = PINA;       // read datapins D0->D7 and store in MSBold
  byte MSBnew = PINA;       // read again immediatly after to assure stable data
  if (MSBnew == MSBold){ 
    byte MSBresult = MSBnew;
    return MSBresult;  
  }
  else getbyte();
}
byte getbyte2(){
/*Get stable data for the most significant byte of countData*/
  byte MSBold = PINC;       // read datapins D0->D7 and store in MSBold
  byte MSBnew = PINC;       // read again immediatly after to assure stable data
  if (MSBnew == MSBold){ 
    byte MSBresult = MSBnew;
    return MSBresult;  
  }
  else getbyte();
}
//merge 4 bytes into a signed 32bit value
long mergeFunc(byte MSBresult, byte secondResult, byte thirdResult, byte LSBresult){
/*Merges the 4 bytes returning one 32-bit variable called countData*/
  long tempVar = 0;
  tempVar |= ((long) MSBresult << 24) | ((long) secondResult << 16) | ((long) thirdResult << 8) | ((long) LSBresult << 0);
  countData = tempVar;
  return countData;
}
