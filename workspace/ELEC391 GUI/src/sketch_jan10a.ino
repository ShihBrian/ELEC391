#include <SoftwareSerial.h>

SoftwareSerial mySerial(10,11);

unsigned long tick_start = millis();;
unsigned long tickms = 30;
unsigned long curr_tick;

unsigned int test = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  while(!Serial){
  }
  delay(1500);
}

void loop() {
  curr_tick = millis();
  if(curr_tick-tickms >= tick_start){
    test++;
    Serial.println(test);
    tick_start = millis();
  }
}
