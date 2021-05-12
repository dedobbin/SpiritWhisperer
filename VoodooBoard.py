import serial
import time
import threading
import sys
import glob
import os
import getpass
import socket
import subprocess

import VoodooGraph

def debug(msg):
    debug = True
    if debug and msg is not None:
        print "<DEBUG>" + str(msg)

########## SPIRITWHISPERER #############
def getFromConfig(name):
	result = None
	searchfile = open("/home/" + getpass.getuser() + "/voodooboard/config", "r")
	for line in searchfile:
	    if ('@' + name) in line: 
		result = next(searchfile)[:-1]
	searchfile.close()
	if result is None:
		raise ValueError("Couldnt find value for {}".format(name))
	return result
	
class SpiritWhisperer:
    ################# TODO: ###########
    #   more functions to call
    #   filter out strings?? 
    ##################################

    #if you add a function, add it to paramsDict, FunctionsToIDDict and one Fubarino side

    #deps:
    #   serialpy
    #   glob (scanForConnections on linux)
    #   uses txt file: /home/username/voodooboard/paths

    paramsDict = {'digitalWrite': 2, 'digitalRead': 1, 'analogRead': 1 ,'analogWrite' : 2, 'pinMode' : 2, 'wheelTurn' : 2, 'wheelMove': 2};#used to lookup how many params a function has
    functionToIDDict = {'digitalWrite': 0, 'digitalRead': 1, 'analogWrite': 2 ,'analogRead' : 3, 'pinMode' : 4, 'wheelTurn' : 5, 'wheelMove' : 6};#look up ID of function
    comport = ""
    bautrate = 9600
    voodooBoard = None
    port = None
    
    #def __init__(self):
        #self.autoConnect(9600)
    def __del__(self):
        if self.voodooBoard is not None:
            self.voodooBoard.close()

    def connect(self, comPort, bautrate):
        self.port = comPort
        self.voodooBoard = serial.Serial(comPort, bautrate)
        

    #uses textinput from stdin
    def autoConnect(self, bautrate):
        bautrate = 9600
        ports = []
        ser = None
    
        if '1' in getFromConfig('askconnection'):
            askConnect = True
        else:
            askConnect = False
        
        if askConnect:
            port = raw_input("What port do you want to connect to?\n")
            self.connect(port, 9600)

        else:
            if sys.platform.startswith('win'):
                for i in range(0, 255):  
                    ports.append( "COM" + str(i))
            elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                ports = glob.glob('/dev/tty[A-Za-z]*')
            elif sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.*')
            else:
                raise EnvironmentError('Unsupported platform')
        
        
            for port in ports:
                try:
                    ser = serial.Serial(port, bautrate)
                except (OSError, serial.SerialException):
                    #print port , " not available"
                    continue
                if ser != None and askConnect is 1:
                    print port, " is available, is the Voodooboard connected to this port?"
                answer = 'y'
                if askConnect is 1:
                    answer = raw_input().lower()[0]
                if answer == 'y':
                    self.connect(port, 9600)
                    print "Connected to " + port
                    
                    self.sendData('9')
                    reply = self.readData()
                    if 'Voodoo' not in reply:
                        print 'No SpiritListener sketch found'
                    else:
                        print reply
                    
		    break
                else:
                    ser.close()
                    continue
            if ser == None:
                print "Couldn't find VoodooBoard"
                   
             
    def close(self):
        if self.voodooBoard is not None:
            self.voodooBoard.close()
        
    #only works with constants as parameters, will use actual parsetree if got time but doubt it is needed (never happend)
    def isValidCommand(self, inp):
        nParams = -1
        inp.replace(' ', '')# we don't need whitespace
        if not "(" in inp or not ")" in inp:
            raise ValueError('Cannot parse, no parameters')
        func = inp[0: inp.index('(')]

        if not any(func in s for s in self.functionToIDDict):
            raise ValueError('Command is not known')
        else:
            paramString = inp[ inp.index('(')+1 : inp.index( ')')]

        if '"' in paramString:
             raise ValueError('UH OH, parameters contain a string, should make some other way to strip params if strings are needed ... . ... rejecting for now')

        theList = [None]
        #strip parameters
        while "," in paramString: #multiple params given
            commaPos = paramString.index(',')
            theList.append(paramString[0: commaPos])
            paramString =paramString[commaPos+1: len(paramString)]

        theList.append(paramString)
        theList[0] = func
 
        #print theList
        return theList
       
    def sendData(self, data):
        self.voodooBoard.write(data)
        time.sleep(0.2)
            
    def readData(self):
        if self.voodooBoard is None:
		return
	return self.voodooBoard.read(self.voodooBoard.inWaiting())
        
    #uses sendData
    #theList is list of function + parameters
    #sends as separate messages now, can be concatted
    def sendCommand(self, theList):
        try:
            cmdString = theList[0]
            nParams = self.paramsDict[cmdString]
            commandID = str(self.functionToIDDict[cmdString])#ID so arduino can lookup easier

            if nParams + 1 is not len(theList):
                raise ValueError('wrong amount of parameters')
            self.sendData(commandID)
            #self.sendData(cmdString)
        
            for x in range(1, nParams+1):
                self.sendData(theList[x])
        except AttributeError:
            print "You don't seem to be connected" 
            

    def flash(self, hexFile):
        avrdPath = getFromConfig("avrdude")
        if hexFile is None or self.port is None:
            return False
	string = avrdPath + " -P "+ self.port +" -p pic32-360  -b 115200 -c stk500v2 -v -v -U flash:w:"+hexFile

        try:
            subprocess.check_call([string], shell=True)
            return True
        except subprocess.CalledProcessError:
            print "Failed to flash"
            return False
        except OSError:
             print "avrdude not found !"
             return False
        
    def whisperHello(self):
        self.sendData('9')
        return self.readData()
   
    def whipserPlot(self, reflash, sendSSID):
        #Will block when receiving data from VoodooBoard, matplotlib cant be called on non-mainthread
        voodooIP = ""
                        
        if reflash:
            hexFile = getFromConfig("wifihex")#todo: change name to SWhex or something
            raw_input("Put fubarino in programming mode, and press enter..")
            self.autoConnect(9600)
            if not self.flash(hexFile):
               print "Failed to reach VoodooBoard"
               return True

        time.sleep(1)
        raw_input("Press enter to reconnect")
        if sendSSID:
            self.autoConnect(9600)
            self.sendData("connect")
            self.sendData(getFromConfig("ssid"))
            self.sendData(getFromConfig("pw"))
            self.sendData(getFromConfig("ip"))

            i = 0
            print "Sending SSID information, please wait"
            while 1:
                received = self.readData()
                #if received is not None:
                    #debug(received)
                if "CIPSTA" in received:
                    voodooIP = received[received.index('"')+1:len(received)-1]
                if "Done !" in received:
                    break
                if "ERROR" in received:
                    print "VoodooBoard failed to join wifi network"
                    break
                
                i = i + 1
                time.sleep(1)
                if (i > 4000 or voodooIP == "0.0.0.0"):                                  
                    print "Wifi fail"
                    break
                               
                       
            print "Disconnect the cable, press ctrl-c when done\n"
        wifi = VoodooWifi(voodooIP, 10000)#wifi connection with new sketch
        wifi.goDraw(1)#blocks until ctrlc is pressed
        wifi.decon()
        return True

    def whisperFlash(self, path):
        hexFile = getFromConfig("hexfile")
        self.autoConnect(9600)
        if not self.flash(hexFile):     
            return False
        else: 
            return True

    def directWhisper(self, command):
        resultList = self.isValidCommand(command)
        self.sendCommand(resultList)
        time.sleep(0.1)
        return self.readData()

    def whisper(self, command):
            try:
                if command.lower() == 'exit':
                        print 'Goodbye !'
                    	return False
		elif command.lower() == 'hello':
		        print self.whisperHello()
                        return True
                    
                elif 'wifi' in command.lower():
                        reflash = True
                        sendSSID = True
                        if '-g' in command:
                            reflash = False
                            sendSSID = False
                        if '-s' in command:
                            reflash = False
                            sendSSID = True
                        self.whipserPlot(reflash, sendSSID)
                        return True

		elif command.lower() == 'flash':
                        raw_input("Put Fubarino in programming mode and press enter")
			hexFile = getFromConfig("hexfile")
                        if not self.whisperFlash(hexFile):
                            print "Failed to flash, reconnect cable?"
                        else:
                            print "Done, don't forget to reconnect!"
                        return True

		elif command.lower() == 'connect':
			self.autoConnect(9600)
                        return True
		else:
                        command = command.replace("HIGH", "1")
                        command = command.replace("LOW", "0")
                        command = command.replace("OUTPUT", "1")
                        command = command.replace("INPUT", "0")
		        print self.directWhisper(command)
                        return True

            except ValueError as err:
                print(err.args)
                return True
            except (KeyboardInterrupt):
                print "Got interrupted by keyboard"
                return False
	    except (serial.SerialException):
		print "No valid connection, are you sure you are connected to the VoodooBoard?"
                return True

     

        
        
class ClientSocket:
    s = 0
    address = ''
    port = 0
    def __init__(self, address, port):
        self.address = address
        self.port = port 
        self.transportProtocol = getFromConfig('transport')

    def goConnect(self):
        if self.transportProtocol is 'udp':
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(5)
        try:
            if self.transportProtocol is 'udp':
                 self.s.bind((self.address, self.port))
            else:
                self.s.connect((self.address, self.port))
            return True
        except:
            print "Problem connecting"
            return False

    def send(self, msg):
        self.s.sendall(msg)


    def close(self):
        self.s.close()

    #TODO: should check for end of file (means host closed) or read error
    def receiveTilClosed(self):
        allData = ""
        while True:
            data = self.s.recv(1024)
            if data:
                allData += data
            else:
                return allData
            
    def receive(self):
            try:
                return self.s.recv(1024)#blocks
            except:
                print "Problem receiving data over socket"
            
class HostSocket:
    s = 0
    def __init__(self, address, port):
        self.s = socket.socket()
        self.s.bind((address, port))
            
    def listen():
        self.s.listen(1)
        while True:
            c, addr = self.s.accept()#blocking
            c.send("YOU ARE NOT WELCOME")
            c.close()
            
    def close(self):
        self.s.close()

    
class VoodooWifi:
    sock = None
    xCoordinates = []
    yCoordinates = []
    data = [] # will contain coordinates read from sensors
    dataCollectThread = None
    keepCollecting = False
    MAXDATALEN = 20
    graph = None

    def __init__(self, address, port):
         self.sock = ClientSocket(address, port)
         self.graph = VoodooGraph.Graphic()
                 
    def __del__(self):
        self.decon()

    #used to shut down properly
    def decon(self):
        #stop data collection, disconnect from socket.
        #have to wait for thread, otherwise closing sock will be nasty
        self.keepCollecting = False;
        self.plotting = False
        if self.dataCollectThread is not None:
            print "waiting for data collecting thread to shut down"
            self.dataCollectThread.join()
            self.dataCollectThread = None
        self.sock.close()

    #blocks until ctrl c is pressed
    def goDraw(self, interval):
        self.startCollectingData()
        self.graph.start()
        while True:
            try:
                coo = self.getCoordinates()
                if coo is not None:
                    self.graph.update(coo[0], coo[1])

                time.sleep(interval)
            except (OSError, KeyboardInterrupt):
                break
            
        self.graph.clearCoordinates()
        

    def startCollectingData(self):
        self.keepCollecting = True
        self.dataCollectThread = threading.Thread(target=self.fillList)
        self.dataCollectThread.start()
    
    #todo: check length of data list and make room if needed, grows forever now
    #todo: handle de +S berichten af
    #used by StartCollectingData to keep collecting data
    def fillList(self):
        while self.keepCollecting:
            s = ""
            self.sock.goConnect()
            s = self.sock.receive()
            self.sock.close()
            self.processMessage(s)
            time.sleep(1)
                     
    #used to get x, y n and b
    def processMessage(self, inp):
        #debug(inp)
        try:
            #used to parse new voodoobotprotocol messages
            if inp is not None and len(inp) > 0 and inp[0] is not'-':
                st = 0
                end = inp.index('[')
                msgID = inp[st:end]
                #debug("msgID is " + msgID)
                if int(msgID) == 0:
                    self.graph.requestFilter = True
                st = end + 1
                end = inp.index(',')
                x = inp[st:end]
                st = end + 1
                end = inp.index(']')
                y = inp[st:end]
                self.addCoordinates(x, y)
                  
            else:
                
                #used to parse old voodoobotprotocol messages
                st = inp.index('-') + 2
                end = inp.index(':')
                msgID = inp[st:end]
                if "-D" in inp:
                    st = inp.index(':') +1
                    end = inp.index(',', st)
                    x = inp[st:end]
                    st = end + 1
                    end = inp.index(':', st)
                    y = inp[st:end]
                    self.addCoordinates(x, y)

                elif "-S" in inp:
                    st = inp.index(':') +1
                    end = inp.index(',', st)
                    xRel = inp[st:end]
                    st = end + 1
                    end = inp.index(',', st)
                    yRel = inp[st:end]
                    prev = self.getCoordinates()
                    if prev is not None:
                        self.addCoordinates(int(prev[0]) + int(xRel), int(prev[1]) + int(yRel))
        
                    
                    m = inp[st:end]
                    st = end + 1
                    end = inp.index(',', st)
                    b = inp[st:end]
                    st = end + 1
                    end = inp.index(';', st)
                    debug('b,n: {},{}'.format(b, m))
                    
                    #y1 = self.yData[-2]
                    #y2 = self.yData[-1] 
                    #x1 = self.xData[-2]
                    #x2 = self.yData[-1]
                    #m = (y2 - y1) / (x2 - x1)
	            #b = y1 - mx1
                    
                    
		
                
        except ValueError:
                #debug ("Malformed message: " + inp)
                pass
        
    def toScreen(self):
        print "Datalist: ", self.data
        print "xCoordinates: ", self.xCoordinates
        print "yCoordinates: ", self.yCoordinates

    def send(self, data):
        self.sock.send(data)

    def addCoordinates(self, x, y):
        if len(self.xCoordinates) is not len(self.yCoordinates):
            debug("Something walked in the soup, amount of x and y coordinates not equal")
        if len(self.xCoordinates) >= self.MAXDATALEN:
            del self.xCoordinates[0]
            del self.yCoordinates[0]
        self.xCoordinates.append(x)
        self.yCoordinates.append(y)
        
        
    #return last read coordinates of voodooboard
    # returns None if doesn't have first x and y.	
    def getCoordinates(self):
        if len(self.xCoordinates) < 1 or len (self.yCoordinates) < 1:
            debug("Has no coordinates")
            return None
	if len(self.xCoordinates) is not len(self.yCoordinates):
            debug("not same amount of x and y coordinates, this is weird")
        return self.xCoordinates[-1], self.yCoordinates[-1]
   
     
       
              
if __name__ == '__main__':
    '''
    graph = VoodooGraph.Graphic()
    graph.start()
    while (1):
        x = raw_input('x\n')
        y = raw_input('y\n')
        graph.update(x,y)
        time.sleep(1)
    '''
   
    '''
    vb = VoodooUDP("192.168.50.101", 10000)     
    vb.startCollectingData()
    while True:
        j = raw_input("command?\n")
        if j.lower()== "exit":
             break
    vb.decon()
    '''

    '''
    vb = VoodooUDP("192.168.50.118", 10000)     
    vb.startCollectingData()
    while True:
        j = raw_input("command?\n")
        if j.lower()== "check":
            vb.toScreen()
        if j.lower() == "stop":
            vb.keepCollecting = False
        if j.lower() == "exit":
            break
    print "<debug> exiting loop"
    vb.decon()
    '''

    
    sw = SpiritWhisperer()
    
    result = True
    while result:
       command = raw_input('Command?\n')
       result = sw.whisper(command)

    del sw
  


