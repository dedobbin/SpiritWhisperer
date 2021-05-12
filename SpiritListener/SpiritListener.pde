#define DIGITALWRITE 0
#define DIGITALREAD 1
#define ANALOGWRITE 2
#define ANALOGREAD 3
#define PINMODE 4
#define WHEELTURN 5
#define WHEELMOVE 6

#define CHECK 9

#define MOTOR1ENABLE 0
#define MOTOR1FORWARD 1
#define MOTOR1BACKWARD 2

#define MOTOR2ENABLE 0
#define MOTOR2FORWARD 1
#define MOTOR2BACKWARD 2

typedef int (*OneParamFunction)(int a);//digitalRead, analogRead (int digitalRead(uint8_t pin))
typedef int (*TwoParamFunction)(int a, int b);//digital and analogRead and write, pinMode

void* functionList[5];

String params[10];


void setup() {
  initPins();
  initFunctionList(functionList);
  Serial.begin(9600);
}

String readFromSerial(bool paramBool)
{
  String rString = "";
  while (!Serial.available());
 
  while (Serial.available()) {
    delay(3);  //delay to allow buffer to fill
    if (Serial.available() > 0) {
      char c = Serial.read();  
      rString += c;
    }
  }

  return rString;
}
void loop() {
  //read commando
  int cmdID = readFromSerial(false).toInt();
  if (cmdID == CHECK)
  {
    Serial.print("Voodoo"); 
  }
  else if (cmdID == DIGITALREAD || cmdID == ANALOGREAD)
  {
    int paramOne = readFromSerial(true).toInt();
    OneParamFunction f = (OneParamFunction) functionList[cmdID];
    int result = f(paramOne);
    Serial.print("Executed function\nResult: ");
    Serial.print(result);
    Serial.flush();
  }
  else if (cmdID == DIGITALWRITE || cmdID == ANALOGWRITE ||cmdID == PINMODE || cmdID == WHEELMOVE ||cmdID == WHEELTURN)
  {
    int paramOne = (readFromSerial(true)).toInt();
    delay(1);
    int paramTwo = (readFromSerial(true)).toInt();
    delay(1);
    TwoParamFunction f = (TwoParamFunction)functionList[cmdID];
    int result = f(paramOne, paramTwo);
    Serial.print("Executed function");
  }
  else if (cmdID == WHEELTURN ||  cmdID == WHEELMOVE)
  {
     int paramOne = (readFromSerial(true)).toInt();
    delay(1);
    int paramTwo = (readFromSerial(true)).toInt();
    delay(1);
    TwoParamFunction f = (TwoParamFunction)functionList[cmdID];
    int result = f(paramOne, paramTwo);
  }
}

void wheelTurn(int miliseconds, int direction)
{
   
  
  
}


void wheelMove(int direction, int speed)
{
 
  
}

void resetMotor()
{
 
}

void initFunctionList(void ** functionList)
{
 
}

void initPins()
{
    
}