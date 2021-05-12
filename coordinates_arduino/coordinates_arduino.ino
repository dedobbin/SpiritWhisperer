#include <SPI.h>        
#include <Ethernet.h>
#include <EthernetUdp.h>

int someV = 0;
// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {  
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 50, 108);

unsigned int localPort = 10000;      // local port to listen on

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

char packetBuffer[UDP_TX_PACKET_MAX_SIZE]; //buffer to hold incoming packet,

void setup() {
  // start the Ethernet and UDP:
  Ethernet.begin(mac,ip);
  Udp.begin(localPort);

  Serial.begin(9600);
  Serial.println(Ethernet.localIP());
}

void loop() {

  int packetSize = Udp.parsePacket();
  if(Udp.available())
  {
    Serial.print("Received packet of size ");
    Serial.println(packetSize);
    Serial.print("From ");
    IPAddress remote = Udp.remoteIP();
    for (int i =0; i < 4; i++)
    {
      Serial.print(remote[i], DEC);
      if (i < 3)
      {
        Serial.print(".");
      }
    }
    Serial.print(", port ");
    Serial.println(Udp.remotePort());

    // read the packet into packetBufffer
    Udp.read(packetBuffer,UDP_TX_PACKET_MAX_SIZE);
    Serial.println("Contents:");
    Serial.println(packetBuffer);

    //REPLY
      //Serial.println("will send");
      for (int i = 0; i < 10; ++i)
      {
        Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
        someV = random(0, 100);
        Udp.print(someV);
        Udp.endPacket();
      }
 }
}

