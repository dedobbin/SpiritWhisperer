/*
i2c:
 reserveer 25 voor data
 26 voor clk
 */

#include <Wire.h>


#define MAXMSGHISTORY 5
const int STDELAY = 1000;


int m_lf = 3;
int m_lr = 4;
int m_rf = 5;
int m_rr = 6;

int cl = 8;
int ds = 7;
int led = 10;
int str = 9;
int dout = 20;

int msgID = 0;
String msgHistory[MAXMSGHISTORY];

void setup()
{

  Serial.begin(9600);
  //while (!Serial.available());
  //Serial.println("<DEBUG>it starts");
  
  while (1)
  {
   Serial.flush();
  
  while (!Serial.available());//block

    String check = "";
    while(Serial.available())
    {
      check += (char)Serial.read();
    }
    if (check == "connect")
        break;
     //Serial.println(check);
  }
    
  
  
  Serial.flush();
  
  while (!Serial.available());//block

    String ssid = "";
    while(Serial.available())
    {
      ssid += (char)Serial.read();
    }
    Serial.print("Got: "); 
    Serial.println(ssid); 
    
     while (!Serial.available());//block

    String pw = "";
    while(Serial.available())
    {
      pw += (char)Serial.read();
    }
    Serial.print("Got: "); 
    Serial.println(pw); 

Serial.flush();
  
  while (!Serial.available());//block

    String ip = "";
    while(Serial.available())
    {
      ip += (char)Serial.read();
    }
    Serial.print("Got: "); 
    Serial.println(ip); 
  
  startServer(ssid, pw, ip);


}
//start TCP server
void startServer(String ssidInfo, String pw, String ip)
{

Serial.print("DEBUG");
Serial.print(ssidInfo);
Serial.print(",");
Serial.println(pw);
  Serial0.begin(115200);

  String reply;

  reply = serialdata("AT+RST");//reset
  Serial.print(reply);
  delay(STDELAY);
  Serial.flush();

  reply = serialdata("AT+CWMODE=1");//station mode
  Serial.print(reply);
  delay(STDELAY);
  Serial.flush();

  reply = serialdata(" AT+CIPMUX=1");//multiple connections
  Serial.print(reply);
  delay(STDELAY);
  Serial.flush();

 String ssidString = "AT+CWJAP=\"" + ssidInfo + "\",\"" + pw + "\"\r";
  reply = serialdata(ssidString);
  
  Serial.print(reply);
  Serial.flush();
  while(!Serial0.available());
  reply="";
  while(Serial0.available())
  {
    reply += (char)Serial0.read();
  }
  reply ="";

  //reply=  serialdata("AT+CIPSTA=\"192.168.50.103");
  reply = serialdata("AT+CIPSTA=\""+ ip);
  Serial.print(reply);
  delay(STDELAY);
  Serial.flush();

  reply = serialdata("   AT+CIPSERVER=1,10000");//server at port 10000
  Serial.print(reply);
  delay(STDELAY);
  Serial.flush();

  reply = serialdata("AT+CIFSR");//get ip address
  Serial.println("Checking current IP: ");
  Serial.print(reply);
  delay(STDELAY);
  Serial.flush();

  Serial.println("Done !");
}



//start UDP server

void myWifi()
{
  Serial0.begin(115200);
  Serial.println(serialdata("AT+RST"));
  Serial.flush();
  delay(STDELAY);
  Serial.println(serialdata("AT+CWMODE=3"));
  Serial.flush();
  delay(STDELAY);
  Serial.println(serialdata("AT+CWJAP=\"secret cow society\",\"here_is_my_password\"\r"));
  Serial.flush();
  while (!Serial.available());
  Serial.println(serialdata("AT+CIPSTA?"));
  Serial.flush();
  delay(STDELAY);
  Serial.println(serialdata("AT+CIPMUX=0"));
  Serial.flush();
  delay(STDELAY);
  Serial.println(serialdata("AT+CIPSTART=\"UDP\",\"192.168.50.118\",10000"));
  Serial.flush();
  delay(STDELAY);
}


void sendData(int destination)
{
  int x,  y;
  String command = "AT+CIPSEND=";
  command.concat(destination);
  command.concat(",");

  String msg = "";
  
  msgID ++;
  if (msgID >= MAXMSGHISTORY)
  {
    msgID = 0;
  }
  #ifdef OLDSTYLE
  if (msgID != 0)
  {
    x = random(0,20) - 10;
    y = random(0,20) - 10;
    int b = random(0, 100);
    int m = random(0, 100);
    msg = "-S";
    msg.concat(msgID);
    msg.concat(":");
    msg.concat(x);
    msg.concat(",");
    msg.concat(y);
    msg.concat(",");
    msg.concat(b);
    msg.concat(",");
    msg.concat(m);
    msg.concat(":");

  }
  else
  {
    msg = "-D";
    msg.concat(msgID);
    msg.concat(":");
    x = random(0,100);
    y = random(0,100);
    msg.concat(x);
    msg.concat(",");
    msg.concat(y);
    msg.concat(":");
  }
  #else
     x = random(0,100);
     y = random(0,100);
     msg.concat(msgID);
     msg.concat("[");
     msg.concat(x);
     msg.concat(",");
     msg.concat(y);
     msg.concat("]");
     
  #endif
  command +=  msg.length();
  //msgHistory[msgID] = msg; 
  Serial0.println(command);
  delay(10);
  Serial0.print(msg);

}


String serialdata(String com)
{
  String rtn = "";
  Serial0.println(com);
  Serial0.flush();
  delay(1000);
  while(Serial0.available())
  {
    rtn += (char)Serial0.read();
  }
  //Serial.print("got: ");
  //Serial.print(rtn);
  return rtn;
}



void loop()
{
  String s= "";
  while (Serial0.available())
  {
    s += (char) Serial0.read();
    delay(1);
  }
  if (s !=  "")
  {
    Serial.println(s.substring(0,9));
    if (s.substring(1, 9) == ",CONNECT")
    {
      int destination = s.charAt(0) - '0'; //make int
      
      Serial.println("<DEBUG> Got a connection  ");
        sendData(destination);
        s = "";
     
    }


  }
  delay(10);
  Serial.flush();


}

// returns -1 if what you are looking for doesnt exist
// n means nth appearance
int getIndex(String in, char target, int n)
{
  int result = -1;
  int found = 0; //how many of target are found
  for (int i = 0; i < in.length(); ++i)
  {
    if (in[i] == target)
    {
      found ++;
      if (found == n)
        return i;
    }
  }
  return -1;
}

