import cv2
import matplotlib.pyplot as plt
import cvlib as cv
import time
from cvlib.object_detection import draw_bbox
import warnings
from .Cameras import *
from .MotorControl import *
from .Config import *

class Imaging:
    """The Imaging class is responsible for calculating the velocities etc for Motor Control
    Attributes:
        imagePath: The path to the images
        camera: The camera being used to get the images
        OR: The object for object recognition
        dataQueue: The queue for transmitting veolcities
        coordinates: The coordinates of the object within the image
        positions: Stores sub arrays of form [time,xdegrees,ydegrees] where x and y are angles relative to the start position
        target: what the user wants to track
        xMid: The horizontal midpoint of the image
        yMid: The vertical midpoint of the image
        currentPosition: The current position of the x and y motor and the time of that position
        currentVelocity: The cuurent velocity the mnotros are runnnig at
        previousTime: The time the proevious image was captured
    """

    imagePath: str = '/home/pi/Desktop/image%s.jpg'
    camera=None
    OR=None
    dataQueue=None  
    MCPipe=None

    target: str = None
    xMid: int = 640
    yMid: int = 360
    centralBox=None

    coordinates: list = []
    positions: list = []#sub arrays should be of the the form [time,xdegrees,ydegrees]
    currentPosition: list = [None,0,0]#time,positionx,positiony
    currentVelocity: list = [0,0]
    previousTime: float = None

    xV=0
    yV=0
    xD=0
    yD=0

    

    def __init__(self,MC, dataQueue, controlQueue,imageReturnQueue, target: str, camera: dict = {'name': 'RPICam','orientation': 180,'Width':1280,'Height':720},mode='advanced',extras={'xMaxSpeed':40,'yMaxSpeed':40},):
        if camera['name']=='RPICam':
            self.camera=RPICam(self.imagePath,camera['orientation'])#sets the camera based on the one that is selected
        elif camera['name']=='Virtual':
            self.camera=VirtualCamera()
        else:
            camera=GenericCamera()
        self.resolution=[camera['Width'],camera['Height']]#sets the resolution
        self.xMid=camera['Width']/2
        self.yMid=camera['Height']/2
        self.centralBox=[camera['Width']/4,camera['Width']*3/4,camera['Height']/4,camera['Height']*3/4]
        self.target=target
        self.OR=ObjectRecognition(target,imageReturnQueue)#creates the object recognition object
        self.dataQueue=dataQueue
        self.controlQueue=controlQueue
        self.mode=mode
        self.MC=MC
        self.xMaxSpeed=extras['xMaxSpeed']#sets the maxspeeds as they are needed in some calculations
        self.yMaxSpeed=extras['yMaxSpeed']

    def MotorUpdater(self):
        while True:
            data=self.MCPipe.recv()
            #print(data)
            self.xV=data['xV']
            self.yV=data['yV']
            self.xD=data['xD']
            self.yD=data['xD']
        

    def main(self,MC,MCPipe):#offers a choice of mode
        self.MC=MC
        self.MCPipe=MCPipe
        t=threading.Thread(target=self.MotorUpdater)
        t.start()
        if self.mode=='advanced':
            self.advancedTracking()

        elif self.mode=='intermediate':
            self.intermediateTracking()

        elif self.mode=='simple':
            self.simpleTracking()

        else:
            self.simpleTracking()

    def mainLimited(self,MC,MCPipe,xLimit1,xLimit2,yLimit1,yLimit2):#only supports one mode currently
        self.MC=MC
        self.MCPipe=MCPipe
        t=threading.Thread(target=self.MotorUpdater)
        t.start()
        if self.mode=='advanced':
            self.advancedTrackingLimited(xLimit1,xLimit2)

        elif self.mode=='intermediate':
            self.intermediateTrackingLimited(xLimit1,xLimit2,yLimit1,yLimit2)

        elif self.mode=='simple':
            self.simpleTrackingLimited(xLimit1,xLimit2,yLimit1,yLimit2)
        else:
            self.simpleTrackingLimited(xLimit1,xLimit2,yLimit1,yLimit2)



    def advancedTracking(self):
        """The main loop for processing images

        While this works it has an issue where due to how it calculates the objects velocity it matches velocity meaning objects end up against the end of the frame and therefore more acceleration can not occur 

        Args:
            q: The queue for transmitting velocity data
            controlQueue: the queue used for shutting down operation
        """
        warnings.warn('imaging main is active')
        self.currentPosition[0]=time.time()#saves the time the tracking starts
        self.positions.append(self.currentPosition)#appends the position twice to show velocity is zero-probably not used
        self.positions.append(self.currentPosition)
        
        while True:#allow it to loop multiple times
            self.previousTime=self.currentPosition[0]           #saves the time of the previous movement
            print(self.previousTime)
            img=self.camera.capture(resolution=self.resolution)
            self.currentPosition[0]=time.time()                 #assigns the current time
            #print(self.currentPosition)
            
            self.getCurrentPositionOfMotors()

            self.positions.append([self.currentPosition[0],None,None])         #adds the current time to the list of positions
            
            self.calculateCoordinates(img)                      #calculates the coordinates of the object in the image
            self.calculatePositionOfObject()                    #adds current angles of target to list
            print('self.positions A ',self.positions)
            xV,yV=self.determineVelocity()                            #calculates velocity
            self.MCPipe.send({'xV':xV,'yV':yV,'recentre':False})
            if not self.controlQueue.empty():#breaks when the signal is sent
                break

    def advancedTrackingLimited(self, limit1: float, limit2: float):
        """The limited version of the tracking
       
        Args:
            limit1: The first limit
            limit2: The second limit 
        """
        warnings.warn('imaging main is active')
        self.currentPosition[0]=time.time()#saves the time the tracking starts
        self.positions.append(self.currentPosition)#appends the position twice to show velocity is zero-probably not used
        self.positions.append(self.currentPosition)

        while True:#allow it to loop multiple times
            recentre=False
            x=self.camera.capture()
            previousTime=self.currentPosition[-1]                                                                       #saves the time of the previous movement
            self.getCurrentPositionOfMotors()
            self.currentPosition[-1]=time.time()                                                                        #assigns the current time
            self.positions.append([self.currentPosition[-1],None,None])                                                 #adds the current time to the list of positions
            self.calculateCoordinates(x)                                                                                #calculates the coordinates of the object in the image
            self.calculatePositionOfObject()                                                                            #adds current angles of target to list
            xV,yV=self.determineVelocity()                                                                                    #calculates velocity

                        
            if self.outsideLimits(xLimit1,xLimit2,yLimit1,yLimit2):
                xV=0
                yV=0
                recentre=True
                self.reset()

            self.MCPipe.send({'xV':xV,'yV':yV,'recentre':recentre})


            if not self.controlQueue.empty():
                self.reset()
                break

    def reset(self):
        """Resets the variables
        Likely to be removed once varaibles are converted to non global        
        """
        coordinates = []
        positions = []#sub arrays should be of the the form [time,xdegrees,ydegrees]
        currentPosition = [None,0,0]#positionx,positiony,time
        currentVelocity = [0,0]
        previousTime = time.time()



    def getCurrentPositionOfMotors(self):
        """calculates current position of motors"""
        self.currentPosition[1]=self.currentPosition[1]+(self.currentVelocity[0]*(self.currentPosition[0]-self.previousTime))
        self.currentPosition[2]=self.currentPosition[2]+(self.currentVelocity[1]*(self.currentPosition[0]-self.previousTime))
        print('self.currentPosition ',self.currentPosition)

    def calculatePositionOfObject(self):
        """calculates the current relative position of the object"""
        self.positions[-1][1]=self.currentPosition[1]+(self.calculateAngleImage(self.coordinates[-1][0],self.resolution,'x'))
        self.positions[-1][2]=self.currentPosition[2]+(self.calculateAngleImage(self.coordinates[-1][1],self.resolution,'y'))
        print('self.positions[-1] ',self.positions[-1])
        
    def calculateAngleImage(self,coordinates,resolution: int,XorY: str) -> float:
        """calculates the angle of the object within the image
        Args:
            coordinates: The coordinates of the object with in the image
            resolution: The resolution of the image
        Returns:
            The angle from the middle of the image in the specified axis

        """
        if XorY=='x':
            anglePerPixel=0.0191
            return (coordinates-self.xMid)*anglePerPixel
        if XorY=='y':
            anglePerPixel=0.0198
            return (coordinates-self.yMid)*anglePerPixel

    def calculateCoordinates(self,img):
        """Calculates the ccordintes of the object in the image
        Args:
            img: A colour numpy array of the image
        """
        xCo,yCo=self.OR.getCoordinates(img)
        if xCo != None:
            self.coordinates.append([xCo,yCo])
            print('xCo ',xCo)
            print('yCo ',yCo)
        elif xCo == None:
            self.search()
        #print(self.coordinates[-1])

    #def calculateVelocity(self):
    #    """calculates and transmits the velocity to the Motor control class"""
    #    xV,yV=self.determineVelocity()


    #    self.dataQueue.put([xV,yV])

    #    self.currentVelocity=[xV,yV]
        
    def determineVelocity(self):
        """determines the velocity the object is moving at
        Returns:
            xV,yV: The velocities of the x and y motors respectively
        """
        deltaTime=self.positions[-1][0]-self.positions[-2][0]
        print('positions ',self.positions)
        print('dT ',deltaTime)
        if deltaTime !=0:
            
            xV=(self.positions[-1][1]-self.positions[-2][1])/(self.positions[-1][0]-self.positions[-2][0])
            yV=(self.positions[-1][2]-self.positions[-2][2])/(self.positions[-1][0]-self.positions[-2][0])
            
        else:
            xV=0
            yV=0
        print('xV ',xV)
        print('yV ',yV)
        xV,yV=self.velocityCheck(xV,yV)
        self.currentVelocity=[xV,yV]
        return xV,yV

    def search(self):
        """used for reacquirig a lock when a target is lost"""
        warnings.warn('attempting to aquire a new target')
        self.dataQueue.put([-10,0])#pick a better search pattern
        while True:
            img=self.camera.capture()
            xCo,yCo=self.OR.getCoordinates(img)
            if xCo != None:
                #reset the first steps of main
                warnings.warn('new target aquired')
                self.reset()
                self.advancedTracking()
                #restart tracking

###############################################################

    def simpleTracking(self):
        """A simple tracking function that sets the velocity based on how far from the centre of the image the target is"""
        while True:
            img=self.camera.capture(resolution=self.resolution)
            xCo,yCo=self.OR.getCoordinates(img)
            if xCo != None:
                xV,yV=self.simpleVelocityCalculation(xCo,yCo)
                #self.dataQueue.put([xV,yV])
            else:
                xV=10
                yV=0
                #self.dataQueue.put([xV,yV])

            self.MCPipe.send({'xV':xV,'yV':yV,'recentre':False})

            if not self.controlQueue.empty():#breaks when the signal is sent
                break

    def simpleTrackingLimited(self,xLimit1,xLimit2,yLimit1,yLimit2):
        while True:
            recentre=False
            img=self.camera.capture(resolution=self.resolution)
            xCo,yCo=self.OR.getCoordinates(img)
            if xCo != None:
                xV,yV=self.simpleVelocityCalculation(xCo,yCo)
                #self.dataQueue.put([xV,yV])
            else:
                xV=10
                yV=0
                #self.dataQueue.put([xV,yV])

            if self.outsideLimits(xLimit1,xLimit2,yLimit1,yLimit2):
                xV=0
                yV=0
                recentre=True

            self.MCPipe.send({'xV':xV,'yV':yV,'recentre':recentre})

            if not self.controlQueue.empty():#breaks when the signal is sent
                break


    def simpleVelocityCalculation(self,xCo,yCo,maxSpeed: float = 20):
        """used to determine the velocity based on how far from the centre of the the target is
        
        This is likely to work best when the images are being taken frequently
        """
        xDis=xCo-self.xMid
        yDis=yCo-self.yMid
        x=xDis/self.xMid
        y=yDis/self.yMid
        
        xV=x*maxSpeed
        yV=y*maxSpeed
        return self.velocityCheck(xV,yV)

    def intermediateTracking(self):
        """A tracking method that tries to match the velocity of the target by increasing or decreasing it based on how from the centre of the image the target is"""
        xV=0
        yV=0
        while True:
            img=self.camera.capture(resolution=self.resolution)#captures the image

            targetsList=self.OR.getCoordinatesMultiTargetLP(img)#gets the coordinates of the objects
            if targetsList==None:#checks none has not been returned
                pass
            elif len(targetsList) == 1:
                xCo=targetsList[0][1]
                yCo=targetsList[0][2]
                if not self.inCentralBox(xCo,yCo):
                    xV,yV=self.intermediateVelocityCalculation(xV,yV,xCo,yCo)
                    #self.dataQueue.put([xV,yV])#only sends a new velocity when one is available
            elif self.isMultiple(targetsList):
                pass#maintains the same velocity
                #tweak the tracking for the scenario
            
            self.MCPipe.send({'xV':xV,'yV':yV,'recentre':False})
            
            if not self.controlQueue.empty():#breaks when the signal is sent
                break

    def intermediateTrackingLimited(self,xLimit1,xLimit2,yLimit1,yLimit2):
        xV=0
        yV=0
        while True:
            recentre=False
            img=self.camera.capture(resolution=self.resolution)#captures the image

            targetsList=self.OR.getCoordinatesMultiTargetLP(img)#gets the coordinates of the objects
            if targetsList==None:#checks none has not been returned
                pass
            elif len(targetsList) == 1:
                xCo=targetsList[0][1]
                yCo=targetsList[0][2]
                if not self.inCentralBox(xCo,yCo):
                    xV,yV=self.intermediateVelocityCalculation(xV,yV,xCo,yCo)
                    #self.dataQueue.put([xV,yV])#only sends a new velocity when one is available
            elif self.isMultiple(targetsList):
                pass#maintains the same velocity
                #tweak the tracking for the scenario


            if self.outsideLimits(xLimit1,xLimit2,yLimit1,yLimit2):
                warnings.warn('outside limits')
                xV=0
                yV=0
                recentre=True
                #self.MC.recentre()
            self.MCPipe.send({'xV':xV,'yV':yV,'recentre':recentre})
                
            if not self.controlQueue.empty():#breaks when the signal is sent
                break

    def intermediateVelocityCalculation(self,xV,yV,xCo,yCo):
        """used to calculate velocities for intermediate tracking
        Args:
            xV: the current x velocity
            yV: the current y velocity
            xCo: the xCoordinate of the target in the image
            yCo: the yCoordinate of the target in the image

        """
        xDis=xCo-self.xMid
        yDis=yCo-self.yMid
        x=xDis/self.xMid
        y=yDis/self.yMid
        maxAdditionalSpeed=10
        xV=xV+x*maxAdditionalSpeed
        yV=xV+y*maxAdditionalSpeed
        return self.velocityCheck(xV,yV)

###############################################################

    def inCentralBox(self,xCo,yCo):
        if self.centralBox[0]<xCo<self.centralBox[1] and self.centralBox[2]<yCo<self.centralBox[3] :
            return True
        else:
            return False

    def isMultiple(self,targetList):
        if len(targetList)>1:
            return True
        else:
            return False

    def outsideLimits(self,xLimit1,xLimit2,yLimit1,yLimit2):
        print('xl1',xLimit1)
        print('xl2',xLimit2)
        print('yl1',yLimit1)
        print('yl2',yLimit2)
        print('xD',self.xD)
        print('yD',self.yD)
        if not (xLimit1<self.xD<xLimit2 and yLimit1<self.yD<yLimit2):
            return True
        else:
            return False



    def velocityCheck(self,xV,yV):
        """used for ensuring the velocity is below the maxSpeed"""
        if xV <0:
            xSpeed=-xV
        else:
            xSpeed=xV

        if yV <0:
            ySpeed=-yV
        else:
            ySpeed=yV

        if xSpeed>self.xMaxSpeed:
            if xV <0:
                xV=-self.xMaxSpeed
            else:
                xV=self.xMaxSpeed

        if ySpeed>self.yMaxSpeed:
            if yV <0:
                yV=-self.yMaxSpeed
            else:
                yV=self.yMaxSpeed

        return xV,yV






########## OR class and functions ################

class ObjectRecognition:
    target: str = None
    OR=None
    targets: list = []
    def __init__(self,target: str,imageReturnQueue=None):
        functions=[#defines the targets and the corresponding functions
            ['person',self.ORBackUp],
            ['bicycle',self.ORBackUp],
            ['car',self.ORBackUp],
            ['motorcycle',self.ORBackUp],
            ['airplane',self.ORBackUp],
            ['bus',self.ORBackUp],
            ['train',self.ORBackUp],
            ['truck',self.ORBackUp],
            ['boat',self.ORBackUp],
            ['traffic light',self.ORBackUp],
            ['fire hydrant',self.ORBackUp],
            ['stop sign',self.ORBackUp],
            ['parking meter',self.ORBackUp],
            ['bench',self.ORBackUp],
            ['bird',self.ORBackUp],
            ['cat',self.ORBackUp],
            ['dog',self.ORBackUp],
            ['horse',self.ORBackUp],
            ['sheep',self.ORBackUp],
            ['cow',self.ORBackUp],
            ['elephant',self.ORBackUp],
            ['bear',self.ORBackUp],
            ['zebra',self.ORBackUp],
            ['giraffe',self.ORBackUp],
            ['backpack',self.ORBackUp],
            ['umbrella',self.ORBackUp],
            ['handbag',self.ORBackUp],
            ['tie',self.ORBackUp],
            ['suitcase',self.ORBackUp],
            ['frisbee',self.ORBackUp],
            ['skis',self.ORBackUp],
            ['snowboard',self.ORBackUp],
            ['sports ball',self.ORBackUp],
            ['kite',self.ORBackUp],
            ['spoon',self.ORBackUp],
            ['bowl',self.ORBackUp],
            ['banana',self.ORBackUp],
            ['apple',self.ORBackUp],
            ['sandwich',self.ORBackUp],
            ['orange',self.ORBackUp],
            ['broccoli',self.ORBackUp],
            ['carrot',self.ORBackUp],
            ['hot dog',self.ORBackUp],
            ['pizza',self.ORBackUp],
            ['donut',self.ORBackUp],
            ['cake',self.ORBackUp],
            ['chair',self.ORBackUp],
            ['couch',self.ORBackUp],
            ['potted plant',self.ORBackUp],
            ['bed',self.ORBackUp],
            ['dining table',self.ORBackUp],
            ['toilet',self.ORBackUp],
            ['tv',self.ORBackUp],
            ['laptop',self.ORBackUp],
            ['mouse',self.ORBackUp],
            ['remote',self.ORBackUp],
            ['keyboard',self.ORBackUp],
            ['cell phone',self.ORBackUp],
            ['microwave',self.ORBackUp],
            ['oven',self.ORBackUp],
            ['toaster',self.ORBackUp],
            ['sink',self.ORBackUp],
            ['refrigerator',self.ORBackUp],
            ['book',self.ORBackUp],
            ['clock',self.ORBackUp],
            ['vase',self.ORBackUp],
            ['scissors',self.ORBackUp],
            ['teddy bear',self.ORBackUp],
            ['hair drier',self.ORBackUp],
            ['toothbrush',self.ORBackUp],
            ]
        self.target=target
        self.imageReturnQueue=imageReturnQueue
        for i in functions:
            self.targets.append(i[0])
        for i in functions:
            if i[0]==target:
                self.OR=i[1]
        if self.imageReturnQueue==None:
            warnings.warn('imageReturnQueue not set')


    def ORBackUp(self,img):
        """Calculates the ccordintes of the object in the image
        Args:
            img: A colour numpy array of the image

        Returns:
            coordinates: the coordinates of the object in the image
        """
        #try:        
        bbox, label, conf = cv.detect_common_objects(img,model='yolov4-tiny')#detects objects
        if len(label)!=0:
            xCo=None
            yCo=None
            for i in range(0,len(label)):#loops through the labels
                if label[i] == self.target:#checks if the label is equal to the target
                    x=bbox[i]
                    xCo=(x[0]+x[2])/2#calculates the centre of the bounding box
                    yCo=(x[1]+x[3])/2
                    break
        #except:
        else:
            xCo=None
            yCo=None
        if self.imageReturnQueue!=None:
            warnings.warn('placing an image on the return Queue')
            self.imageReturnQueue.put({'img':img,'box':bbox,'label':label,'confidence':conf})#returns the image
        else:
            warning.warn('no queue found')
        return xCo,yCo

    def getCoordinatesMultiTargetLP(self,img,targets=[]):
        if len(targets)==0:
            targets.append(self.target)
        bbox, label, conf = cv.detect_common_objects(img,model='yolov4-tiny')#detects objects
        returnTargets=[]#creates the array for returning the objects
        if len(label)!=0:
            #xCo=None
            #yCo=None
            for i in range(0,len(label)):#loops through the labels
                if label[i] in self.targets:#checks if the label is equal to one of the targets
                    x=bbox[i]
                    xCo=(x[0]+x[2])/2#calculates the centre of the bounding box
                    yCo=(x[1]+x[3])/2
                    returnTargets.append([label[i],xCo,yCo])#appends the label and coordiates to the list
        #except:
        else:
            #xCo=None
            #yCo=None
            returnTargets=None#sets the list to None
        if self.imageReturnQueue!=None:
            warnings.warn('placing an image on the return Queue')
            self.imageReturnQueue.put({'img':img,'box':bbox,'label':label,'confidence':conf})#returns the image
        else:
            warning.warn('no queue found')
        return returnTargets

    def getCoordinates(self,img):
        """returns the ccordnates of the object in the image
        Returns:
            coordinates: the coordinates of the object in the image
        """
        return self.OR(img)

    def getTargets(self) -> list:
        """returns a list of the targets
        Returns:
            targest: the posible targets
        """
        return self.targets

