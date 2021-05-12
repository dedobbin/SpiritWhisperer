import time
from matplotlib.pylab import *
from rdp import rdp


class Graphic:
    MAXCOORDINATES = 20
    MAXOBSTACLES = 20
    xData = []
    yData = []
    
    width = 100
    height = 100

    x2Data = []
    y2Data = []

    line1 = None
    line2 = None
    requestFilter = None
    
    def __init__(self):
        requestFilter = False
    
    def start(self):
         ion() # turn interactive mode on
         self.line1, self.line2,= plot(self.xData, self.yData, 'r', self.x2Data, self.y2Data, 'o')
         self.line1.axes.set_xlim(0, self.width)
         self.line1.axes.set_ylim(0, self.height)
         self.line1.set_label("Obstacles")
         #self.line1.set_label("Voodoo Path")
         #self.line2.set_label("Objects")
         legend()
         grid()
         draw()

         

    def __del__(self):
        close() 

    def update(self, x, y):
        if len(self.xData) > 0:
            lastCo = self.xData[-1], self.yData[-1]
            if lastCo[0] is x and lastCo[1] is y:
                return# dont update, nothing changed
        #print  "debug" + str(self.width) + ">" + str(x)
        if int(x) > int(self.width):
            self.resize(int(x) +5, self.height)
        if int(y) > int(self.height):
            #print  "debug" + str(self.height) + ">" + str(y)
            self.resize(self.width, int(y)+5)
        if len(self.xData) + 1 > self.MAXCOORDINATES:
            self.removeCoordinate(0)
        self.xData.append(x)
        self.yData.append(y)
        if self.requestFilter:
            filtered = self.peucker(self.xData,self.yData)
            self.requestFilter = False
        self.line1.set_xdata(self.xData)
        self.line1.set_ydata(self.yData)
        draw()

    def resize(self, x,y):
         #ion() # turn interactive mode on
         self.line1, self.line2,= plot(self.xData, self.yData, 'r', self.x2Data, self.y2Data, 'o')
         self.width = x
         self.height = y
         self.line1.axes.set_xlim(0, int(x))
         self.line1.axes.set_ylim(0, int(y))
         self.line1.set_label("Obstacles")
         #self.line1.set_label("Voodoo Path")
         #self.line2.set_label("Objects")
         grid()
         draw()
  
    def peucker(self, xList, yList):
	#rdp throws type error, probably because iam feeding it numpy array not list
        newlist = []
        i = 0
        for c in xList:
            newlist.append((int(xList[i]), int(yList[i])))
            i = i + 1
        newlist = rdp(newlist, epsilon=0.5)
        xList = []
        yList = []
        i = 0
        for c in newlist:
            xList.append(newlist[i][0])
            yList.append(newlist[i][1])
            i = i + 1
        print "<DEBUG>Peucker result: " 
        print xList
        print yList
        return (xList, yList)

    def addObstacle(self, x, y):
        if len(self.x2Data) + 1 > self.MAXOBSTACLES:
             self.removeObstacle()
        self.x2Data.append(x)
        self.y2Data.append(y)
        self.line2.set_xdata(self.xData)
        self.line2.set_ydata(self.yData)
        draw()

    def clearCoordinates(self):
        for i in range(0, len(self.xData)):
            self.removeCoordinate(0)
    
    def clearObstacles(self):
        for i in range(0, len(self.x2Data)):
            self.removeCoordinate(0)

    def removeCoordinate(self, i):
        del self.xData[i]
        del self.yData[i]
   
    def removeObstacle(self, i):
        del self.x2Data[i]
        del self.y2Data[i]
    
    def rotatePoint(self, point, degrees):
       result = [0.,0.]
       theta = (degrees/180.) * np.pi
       result[0]=  vector[0]*np.cos(theta)-vector[1]*np.sin(theta) 
       result[1]=  vector[0]*np.sin(theta)+vector[1]*np.cos(theta) 
       return result
        


if __name__ == "__main__":
    '''
    g = Graphic()
    for i in range(0,10):
        g.updateVBpos(i*10, i *15)
        time.sleep(1)
    
    '''

    import VoodooBoard
    g = Graphic()
    vbWifi = VoodooBoard.VoodooWifi("192.168.50.111", 10000) #UPDcommunication is .py file, VoodooBoard is class
    vbWifi.startCollectingData()#will create new thread
    while True:
        try:
            co = vbWifi.getCoordinates()
            if co is None:
                time.sleep(1)
                continue
            g.updateVBpos(co[0], co[1])
            time.sleep(1)
        except (KeyboardInterrupt, OSError):
            break

    vbWifi.decon()
    del g


    '''
    import VoodooBoard
    #old arduino test
    vbUDP = VoodooBoard.VoodooUDP("192.168.50.108", 10000) #UPDcommunication is .py file, VoodooBoard is class
    g = Graphic()

    for i in range(0, 20):
        try:
            vbUDP.collectData(False)
            time.sleep(0.4)
            coordinates = vbUDP.getCoordinates()
            if coordinates is not None:
                g.updateVBpos(coordinates[0], coordinates[1])
		print "---------------------"                
		print vbUDP.coordinates
        except ( KeyboardInterrupt, OSError):
                break
            
    del vbUDP
    del g
    '''
    exit()
