import cv2
import matplotlib.pyplot as plt
import cvlib as cv
import time
from cvlib.object_detection import draw_bbox

from .Cameras import *
from .MotorControl import *

class Imaging:
    """The Imaging class is responsible for calculating the velocities etc for Motor Control
    Attributes:
        imagePath: The path to the images
        camera: The camera being used to get the images
        coordinates: The coordinates of the object within the image
        positions: Stores sub arrays of form [time,xdegrees,ydegrees] where x and y are angles relative to the start position
        target: what the user wants to track
        xMid: The horizontal midpoint of the image
        yMid: The vertical midpoint of the image
        currentPosition: The current position of the x and y motor and the time of that position
        currentVelocity: The cuurent velocity the mnotros are runnnig at
    """

    imagePath: str = '/home/pi/Desktop/image%s.jpg'
    camera=None
    OR=None
    coordinates: list = []
    positions: list = []#sub arrays should be of the the form [time,xdegrees,ydegrees]

    target: str = None
    xMid: int = 640
    yMid: int = 360
    currentPosition: list = [0,0,None]#positionx,positiony,time
    currentVelocity: list = [0,0]
    q=None
    previousTime: float = time.time()

    def __init__(self, q, controlQueue, target: str, camera: dict = {'name': 'RPICam'}):
        if camera['name']=='RPICam':
            self.camera=RPICam(self.imagePath,180)
        print('hello')
        self.target=target
        self.OR=ObjectRecognition(target)
        self.q=q
        self.controlQueue=controlQueue


    def main(self):
        """The main loop for processing images
        Args:
            q: The queue for transmitting velocity data
            controlQueue: the queue used for shutting down operation
        """
        self.currentPosition[-1]=time.time()
        self.positions.append([self.currentPosition[-1],0,0])
        while True:#allow it to loop multiple times
            x=self.camera.capture()
            previousTime=self.currentPosition[-1]#saves the time of the previous movement
            self.getCurrentPosition()
            self.currentPosition[-1]=time.time()#assigns the current time
            self.positions.append([self.currentPosition[-1],None,None])#adds the current time to the list of positions
            self.calculateCoordinates(x)#calculates the coordinates of the object in the image
            self.calculatePosition()#adds current angles of target to list
            self.calculateVelocity()#calculates velocity
            if not self.controlQueue.empty():#breaks when the signal is sent
                break

    def mainLimited(self, q, controlQueue, limit1: float, limit2: float):
        self.q=q
        while True:#allow it to loop multiple times
            x=self.camera.capture()
            previousTime=self.currentPosition[-1]#saves the time of the previous movement
            self.getCurrentPosition()
            self.currentPosition[-1]=time.time()#assigns the current time
            self.positions.append([self.currentPosition[-1],None,None])#adds the current time to the list of positions
            self.calculateCoordinates(x)#calculates the coordinates of the object in the image
            self.calculatePosition()#adds current angles of target to list
            self.calculateVelocity()#calculates velocity
            if self.positions[-1][1]<=limit1 or self.positions[-1][1]>=limit2 :
                self.recentre(self.positions[-1][1])
            if not self.controlQueue.empty():
                break

    def reset(self):
        coordinates = []
        positions = []#sub arrays should be of the the form [time,xdegrees,ydegrees]


        currentPosition = [0,0,None]#positionx,positiony,time
        currentVelocity = [0,0]

        previousTime = time.time()

    def recentre(self, position: float):
        xV=20
        timeToCentre=position/xV
        if timeToCentre<0:
            timeToCentre=-timeToCentre
        self.q.put([xV,0])
        time.sleep(timeToCentre)
        self.q.put(0,0)

    def getCurrentPosition(self):
        """calculates current position of motors"""
        self.currentPosition[0]=self.currentPosition[0]+(self.currentVelocity[0]*(self.currentPosition[-1]-self.previousTime))
        self.currentPosition[1]=self.currentPosition[1]+(self.currentVelocity[1]*(self.currentPosition[-1]-self.previousTime))
        

    def calculatePosition(self):
        """calculates the current relative position of the object"""
        self.positions[-1][1]=self.currentPosition[0]+(self.calculateAngleImage(self.coordinates[-1][0],[1920,1080],'x'))
        self.positions[-1][2]=self.currentPosition[1]+(self.calculateAngleImage(self.coordinates[-1][1],[1920,1080],'y'))
        
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
        elif xCo == None:
            self.search()
        #print(self.coordinates[-1])

    def calculateVelocity(self):
        """calculates and transmits the velocity to the Motor control class"""
        xV,yV=self.determineVelocity()


        self.q.put([xV,yV])

        self.currentVelocity=[xV,yV]
        
    def determineVelocity(self):
        """determines the velocity the object is moving at
        Returns:
            xV,yV: The velocities of the x and y motors respectively
        """
      
        xV=(self.positions[-1][1]-self.positions[-2][1])/(self.positions[-1][0]-self.positions[-2][0])
        yV=(self.positions[-1][2]-self.positions[-2][2])/(self.positions[-1][0]-self.positions[-2][0])
        return xV,yV

    def search(self):
        self.q.put([-10,0])#pick a better search pattern
        while True:
            img=self.camera.capture()
            xCo,yCo=self.OR.getCoordinates(img)
            if xCo != None:
                #reset the first steps of main
                self.reset()
                self.main()
                #restart tracking




########## OR class and functions ################

class ObjectRecognition:
    target: str = None
    OR=None
    targets: list = []
    def __init__(self,target: str):
        functions=[
            ['face',self.ORFaces],
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
            ['cat face',self.ORCatFace],
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
        for i in functions:
            self.targets.append(i[0])
        for i in functions:
            if i[0]==target:
                self.OR=i[1]


    def ORBackUp(self,img):
        """Calculates the ccordintes of the object in the image
        Args:
            img: A colour numpy array of the image

        Returns:
            coordinates: the coordinates of the object in the image
        """
        try:        
            bbox, label, conf = cv.detect_common_objects(img)
            for i in range(0,len(label)):#x not being assigned-not finding target in list of images
                if label[i] == self.target:
                    x=bbox[i]
            xCo=(x[0]+x[2])/2
            yCo=(x[1]+x[3])/2
        except:
            xCo=None
            yCo=None
        return xCo,yCo

    def ORFaces(self,img):
        """for faces
        Args:
            img: A colour numpy array of the image

        Returns:
            coordinates: the coordinates of the object in the image
        """
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + ("haarcascade_frontalface_default.xml"))

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(imgGray, 1.3, 5)  
        xCo=faces[0][0]+(faces[0][2]/2)
        yCo=faces[0][1]+(faces[0][3]/2)
        return xCo,yCo

    def ORCatFace(self,img):
        """for cat faces
        Args:
            img: A colour numpy array of the image

        Returns:
            coordinates: the coordinates of the object in the image
        """
        catCascade = cv2.CascadeClassifier(cv2.data.haarcascades + ("haarcascade_frontalcatface_extended.xml"))
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = catCascade.detectMultiScale(imgGray, 1.3, 5)  
        xCo=faces[0][0]+(faces[0][2]/2)
        yCo=faces[0][1]+(faces[0][3]/2)
        return xCo,yCo
        
        

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
