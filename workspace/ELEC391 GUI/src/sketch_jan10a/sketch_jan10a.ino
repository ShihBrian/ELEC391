#include <SoftwareSerial.h>
#define LEDPin 13

SoftwareSerial mySerial(10,11);
/*===============================*/
//Globals for optical encoder
#define ENCODERAPIN 2 //interrupt
#define ENCODERBPIN 36 //can be interrupt for better performance Pin 2, 3, 18, 19, 20, 21
#define CPR 100 //100 ticks per 360 degrees
#define CLOCKWISE 1
#define COUNTERCLOCKWISE 2
volatile long encoderPos = 0.0;
volatile long interruptsReceived = 0;
short currentdirection = CLOCKWISE;
long previousPos = 0;
volatile double angle = 0.0;
volatile double old_angle = 0.0;
double curr_vel;
double old_vel = 0.0;
unsigned long curr_time;
unsigned long start_time = millis();
double deltaT = 10.0; //ms
double accel;
double scale = 1/(deltaT/1000);
/*===============================*/

unsigned long tick_start = millis();
unsigned long tickms = 10;
unsigned long curr_tick;
int x = 10;
int y = 10;
unsigned int startbyte = 0xFF;
unsigned int endbyte = 0xFE;
int dx = 1;
int dy = 0;
bool pause = false;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(57600);
  Serial.setTimeout(10);
  pinMode(ENCODERAPIN, INPUT);
  pinMode(ENCODERBPIN, INPUT);
  pinMode(LEDPin, OUTPUT);
  attachInterrupt(0,ISR_GPIO, RISING);
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
int move_speed = 1;
void test_pattern(int move_speed)
{
    x += dx*move_speed;
    y += dy*move_speed;
    if (x == 240 && y == 10){
      dx = 0;
      dy = 1;
    }
    if(y == 240 && x == 240){
      dx = -1;
      dy = 0;
    }
    if(y == 240 && x == 10){
      dx = 0;
      dy = -1;
    }
    if(y == 10 && x == 10){
      dx = 1;
      dy = 0;
    }      
}
unsigned int incomingByte = 0;
void loop() {
  curr_tick = millis();
  if(!pause){
    if(curr_tick-tickms >= tick_start){
      Send_Data(startbyte);
      Send_Data(x);
      Send_Data(y);
      Send_Data(endbyte);  
      tick_start = millis();
      test_pattern(move_speed);
    }
  }

  if(Serial.available()>0){
    incomingByte = Serial.read();
    if(incomingByte == 0xFF)
      move_speed = 0;
    else if(incomingByte == '1'){
      move_speed = incomingByte-48;
    }
    else if(incomingByte == 0xFE){
      pause = !pause;
    }
  }
  /*if(encoderPos != previousPos){
    Serial.print(angle);
    previousPos = encoderPos;
  }*/
}
void ISR_GPIO()
{
  // read both inputs
  int a = digitalRead(ENCODERAPIN);
  int b = digitalRead(ENCODERBPIN);
 
  if (a == b )
  {
    
    // b is leading a (counter-clockwise)
    encoderPos--;
    currentdirection = COUNTERCLOCKWISE;
  }
  else
  {
    // a is leading b (clockwise)
    encoderPos++;
    currentdirection = CLOCKWISE;
  }
 
  // track 0 to 100
  encoderPos = encoderPos % CPR;

  angle = 3.6 * encoderPos;
 
  // track the number of interrupts
  interruptsReceived++;
}


