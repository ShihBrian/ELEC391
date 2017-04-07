#include <PID_v1.h>
#include <SoftwareSerial.h>

#define FWPinR 4
#define BWPinR 5
#define FWPinL 6
#define BWPinL 7

//BWL   FWL   BWR   FWR

//#define DEBUG
//#define LOCAL_OUTPUT
SoftwareSerial mySerial(10,11);
/*===============================*/
//Globals for optical encoder
#define FORWARD 1
#define BACKWARD 2
volatile long encoderPosLeft = 0;
volatile long encoderPosRight = 0;
short currDirectionLeft = FORWARD;
short currDirectionRight = FORWARD;
long previousPosLeft = 0;
long previousPosRight = 0;
volatile double extensionLeft = 0;
volatile double extensionRight= 0;
long PosLeftoffset = 0;
long PosRightoffset = 0;
volatile long countData = 0;
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
  start = 6,
};
/*===============================*/

/*===============================*/
//PID globals
float Kp = 120;
float Ki = 0;
float Kd = 170;
double DesiredLeft,PIDOutputLeft;
double DesiredRight,PIDOutputRight;
double ActualLeft = 0;
double ActualRight = 0;
int directionleft;
int directionright;
PID PID1(&ActualLeft, &PIDOutputLeft, &DesiredLeft, Kp, Ki, Kd, DIRECT);
PID PID2(&ActualRight, &PIDOutputRight, &DesiredRight, Kp, Ki, Kd, DIRECT);
const int sampleRate = 10; // Variable that determines how fast our PID loop runs
const long serialPing = 300;
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
bool ma_seven = true;
bool ma_two = false;
bool intersect = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(10);
  pinMode(FWPinL, OUTPUT);
  pinMode(BWPinL, OUTPUT);
  pinMode(FWPinR, OUTPUT);
  pinMode(BWPinR, OUTPUT);
  // Set all pins in PORTA and C (digital pins 22->37) as input pins
  for(int i = 22; i<38; i++) {
    pinMode(i, INPUT);
  }
  // Set pins 5,6,7 in PORT B (digital pins 11->16) as output pins
  for(int j = 8; j<17; j++) {
    pinMode(j, OUTPUT);
    digitalWrite(j, LOW);
  }
  analogWrite(BWPinL, 200);
  analogWrite(BWPinR, 200);
  delay(1000);
  analogWrite(BWPinL, 255);
  analogWrite(BWPinR, 255);
  delay(500);
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW); // /RST resets the internal counter between runs
  delay(10);
  digitalWrite(13, HIGH); // Stay high for rest of the run
  PID1.SetMode(AUTOMATIC);
  PID2.SetMode(AUTOMATIC);
  PID1.SetSampleTime(sampleRate);
  PID2.SetSampleTime(sampleRate);
  while(!Serial){ //wait for serial to be initialized
  }
  Send_Message(start,1);
  delay(500);
  all_off();
}

void loop() {
#if !defined(DEBUG) && !defined(LOCAL_OUTPUT) //main loop 
  static int tries = 0;
  curr_tick = millis();
  if(curr_tick-tickms >= tick_start){ //run loop every tickms 
    ISR_Counter(); //get new encoder positions
    if((previousPosLeft != encoderPosLeft)||(previousPosRight != encoderPosRight)){
      if(tries == 1){ //send message every second encoderPosLeft change
        Send_Message(encoderleft, encoderPosLeft); 
        Send_Message(encoderright, encoderPosRight);
        previousPosLeft = encoderPosLeft;
        previousPosRight = encoderPosRight;
        tries = 0;
      }
      else{
        tries++;
      }
    }
    tick_start = millis();
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
      ma_seven = true;
      ma_two = false;
    }
    else if(incomingByte == 0xED){
      ma_two = true;
      ma_seven = false;
    }
    else if(incomingByte == 0xEC){
      ma_two = false;
      ma_seven = false;
    }
    else if(incomingByte == 0xFC){
      rxPID = true;
    }
    else if(incomingByte == 0xEF){
      goto_middle();
    }
    
    if (state == 0){
      if(incomingByte == 0xFB){
        state = 1;
      }
    }
    else if(state == 1){
      DesiredLeft = incomingByte;
      state = 2;
      PID_Output(0, DesiredLeft, DesiredRight); 
    }
    else if(state == 2){
      DesiredRight = incomingByte;
      state = 3;
      PID_Output(0, DesiredLeft, DesiredRight); 
    }
    else if(state == 3){
      if(incomingByte == 0xFA){
        state = 0;
        PID_Output(0, DesiredLeft, DesiredRight); 
      }
    } 
  }
  //pass values to PID library to compute output power
  PID_Output(intersect, DesiredLeft, DesiredRight);   
#endif  

#ifdef DEBUG //for debugging and testing PID
  ISR_Counter();
  static double timenow = 0;
  static bool bonce = true;
  if (Serial.available() > 0) { //If we sent the program a command deal with it
      bonce = true;
      Kp1 = Serial.parseFloat();
      analogWrite(FWPinL, 100);
      Serial.print(Kp1-10);
      Serial.print("\t");
      timenow = millis();
  }
  
  if(encoderPosLeft == Kp1){
    if(bonce){
      analogWrite(FWPinL, 0);
      Serial.println(millis()-timenow);
      bonce = false;
    }
  }

#endif //DEBUG

#ifdef LOCAL_OUTPUT //for outputting encoder information on local arduino serial
  Local_Out();
#endif //LOCAL_OUTPUT

}

void goto_middle(){
  PID1.SetTunings(255,0,10);
  PID2.SetTunings(255,0,10);  
  while(abs(encoderPosLeft-90)>2 || abs(encoderPosRight-90)>2){
    ISR_Counter();
    PID_Output(1, 90,90); 
  }
  int i =0;
  for(i;i<1000;i++){
    ISR_Counter();
    PID_Output(1, 90,90);  
  }
  PID1.SetTunings(Kp,Ki,Kd);
  PID2.SetTunings(Kp,Ki,Kd);  
  all_off();
  Send_Message(start,1);
}

void Local_Out(){
  ISR_Counter();
  if((encoderPosLeft != previousPosLeft) || (encoderPosRight != previousPosRight)){
    Serial.print(encoderPosLeft);
    Serial.print("\t");
    Serial.println(encoderPosRight);
    previousPosLeft = encoderPosLeft;
    previousPosRight = encoderPosRight;
  }  
}

int MAleft[10];
int lastpwml = 0;
int lastpwml2 = 0;
int lastpwml3 = 0;
int lastpwml4 = 0;
int lastpwml5 = 0;
int lastpwml6 = 0;
int lastpwmr = 0;
int lastpwmr2 = 0;
int lastpwmr3 = 0;
int lastpwmr4 = 0;
int lastpwmr5 = 0;
int lastpwmr6 = 0;
int MAright[10];
void PID_Output(bool flag, int DesiredL, int DesiredR){
    int difference = 0;
    if(encoderPosLeft > DesiredL){
      difference = abs(encoderPosLeft - DesiredL);
      ActualLeft = DesiredL - difference;
      DesiredLeft = DesiredL;
      directionleft = BACKWARD;
    }
    else{
      ActualLeft = encoderPosLeft - difference;
      DesiredLeft = DesiredL; 
      directionleft = FORWARD;
    }
    if(encoderPosRight > DesiredR){
      difference = abs(encoderPosRight - DesiredR);
      ActualRight = DesiredR - difference;
      DesiredRight = DesiredR;
      directionright = BACKWARD;
    }
    else{
      ActualRight = encoderPosRight - difference;
      DesiredRight = DesiredR; 
      directionright = FORWARD;
    }
    PID1.Compute();
    PID2.Compute();    
    static int count = 0;
    //Run PID computation
    if(flag){
      if(ma_seven){
        PIDOutputLeft = (lastpwml+lastpwml2+lastpwml3+lastpwml4+lastpwml5+lastpwml6+PIDOutputLeft)/7;
        lastpwml6 = lastpwml5;
        lastpwml5 = lastpwml4;
        lastpwml4 = lastpwml3;
        lastpwml3 = lastpwml2;
        lastpwml2 = lastpwml;
        lastpwml = PIDOutputLeft;
        PIDOutputRight = (lastpwmr+lastpwmr2+lastpwmr3+lastpwmr4+lastpwmr5+lastpwmr6+PIDOutputRight)/7;
        lastpwmr6 = lastpwmr5;
        lastpwmr5 = lastpwmr4;
        lastpwmr4 = lastpwmr3;
        lastpwmr3 = lastpwmr2;
        lastpwmr2 = lastpwmr;
        lastpwmr = PIDOutputRight;
      }
      else if(ma_two){
        PIDOutputLeft = (lastpwml+PIDOutputLeft)/2;
        lastpwml2 = lastpwml;
        lastpwml = PIDOutputLeft;
        PIDOutputRight = (lastpwmr+PIDOutputRight)/2;
        lastpwmr2 = lastpwmr;
        lastpwmr = PIDOutputRight;        
      }
      //Turn on pin according to direction and PID output. Limit to 255 
      if (directionleft == FORWARD){
        analogWrite(FWPinL, PIDOutputLeft);
        digitalWrite(BWPinL, LOW);
        if(count > 50){
          //Send_Message(debug, PIDOutputLeft);
          count = 0;
        }
        count++;
      }
      else{
        analogWrite(BWPinL,PIDOutputLeft);
        digitalWrite(FWPinL, LOW);
      }
      
      if (directionright == FORWARD){
        analogWrite(FWPinR, PIDOutputRight);
        digitalWrite(BWPinR, LOW);
      }
      else{
        analogWrite(BWPinR,PIDOutputRight);
        digitalWrite(FWPinR, LOW);
      }
    }
}

//function to read 32bit data from encoder chip
void ISR_Counter(){
  digitalWrite(9, HIGH); // Set OE to HIGH (disable)
  
  digitalWrite(12, LOW);
  digitalWrite(8, HIGH); // SEL1 = 0 and SEL2 = 1
  
  digitalWrite(9  , LOW); // Set OE to LOW (enable)
  byte MSBresult = getbyte2();
  byte MSBresult2 = getbyte();
  
  digitalWrite(12, HIGH);
  digitalWrite(8, HIGH); // SEL1 = 1 and SEL2 = 1
  byte secondResult = getbyte2();
  byte secondResult2 = getbyte();


  digitalWrite(12, LOW);
  digitalWrite(8, LOW); // SEL1 = 0 and SEL2 = 0
  byte thirdResult = getbyte2();
  byte thirdResult2 = getbyte();
  
  digitalWrite(12, HIGH);
  digitalWrite(8, LOW); // SEL1 = 1 and SEL2 = 0
  byte LSBresult = getbyte2();
  byte LSBresult2 = getbyte();

  digitalWrite(9, HIGH); // Set OE to HIGH (disable)
  
  encoderPosLeft = mergeFunc(MSBresult, secondResult, thirdResult, LSBresult)+10;
  encoderPosRight = mergeFunc(MSBresult2, secondResult2, thirdResult2, LSBresult2)+10;

  encoderPosLeft = -encoderPosLeft+20;
  encoderPosRight = -encoderPosRight+20;

  if (encoderPosLeft<0) encoderPosLeft = 0;
  if (encoderPosRight<0) encoderPosRight = 0; 
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
  digitalWrite(FWPinL, LOW);
  digitalWrite(BWPinL, LOW);
  digitalWrite(FWPinR, LOW);
  digitalWrite(BWPinR, LOW);      
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
