#include <SoftwareSerial.h>

SoftwareSerial mySerial(10,11);

unsigned long tick_start = millis();;
unsigned long tickms = 10;
unsigned long curr_tick;
int x = 10;
int y = 10;
unsigned int startbyte = 0xFF;
unsigned int endbyte = 0xFE;
int dx = 1;
int dy = 0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(57600);
  while(!Serial){
  }
  delay(1500);
}

void Send_Data(int padding, unsigned int data)
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

void loop() {
  int stack[] = {0,0,0};
  int idx=2;
  int temp;

  curr_tick = millis();
  if(curr_tick-tickms >= tick_start){
    
    Send_Data(1,startbyte);
    
    if(x < 16){
      Send_Data(2,x);   
    }
    else if (x < 255){
      Send_Data(1,x); 
    }
    else{
      Send_Data(0,x); 
    }
    if(y < 16){
      Send_Data(2,y);
    }
    else if (y < 255){
      Send_Data(1,y); 
    }
    else{
      Send_Data(0,y); 
    }
    
    Send_Data(1,endbyte); 
    
    tick_start = millis();

    x += dx;
    y += dy;
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
}

