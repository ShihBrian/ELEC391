#include <SoftwareSerial.h>

SoftwareSerial mySerial(10,11);

unsigned long tick_start = millis();;
unsigned long tickms = 10;
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

void loop() {
  int stack[] = {0,0,0};
  int idx=2;
  int temp;
  curr_tick = millis();
  if(curr_tick-tickms >= tick_start){
    test++;
    
    Serial.print("0");
    Serial.print(startbyte, HEX);
    if(test < 16){
      Serial.print("00");
      Serial.print(test, HEX);
      Serial.print("00");
      Serial.print(test, HEX);
    }
    else if(test<255){
      Serial.print("0");  
      Serial.print(test, HEX);
      Serial.print("0");
      Serial.print(test, HEX);      
    }
    else{
      Serial.print(test, HEX);
      Serial.print(test, HEX);      
    }
    Serial.print("0");
    Serial.print(endbyte, HEX);
    
    tick_start = millis();

    if (test == 500){
      test = 0;
    }
  }
}
