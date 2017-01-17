#include <SoftwareSerial.h>

SoftwareSerial mySerial(10,11);

unsigned long tick_start = millis();;
unsigned long tickms = 30;
unsigned long curr_tick;

unsigned int test = 0;
unsigned int startbyte = 0xFF;
unsigned int endbyte = 0xFE;

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
    test++;
    
    Send_Data(1,startbyte);
    if(test < 16){
      Send_Data(2,test);
      Send_Data(2,test);  
    }
    else if(test<255){
      Send_Data(1,test);
      Send_Data(1,test);     
    }
    else{
      Send_Data(0,test);
      Send_Data(0,test);     
    }
      Send_Data(1,endbyte); 
    
    tick_start = millis();

    if (test == 250){
      test = 0;
    }
  }
}
