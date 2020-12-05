import cv2
import matplotlib.pyplot as plt
import cvlib as cv
import time
from cvlib.object_detection import draw_bbox

from .RPICam import *
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
        currentPosition: The current position of the x motor and the time of that position
        currentVelocity: The cuurent velocity the mnotros are runnnig at


    """

    imagePath='/home/pi/Desktop/image%s.jpg'
    camera=RPICam(imagePath,180)
    coordinates=[]
    positions=[]#sub arrays should be of the the form [time,xdegrees,ydegrees]
    #MC=MotorControl()
    target: str = None
    xMid:int = 640
    yMid: int = 360
    currentPosition=[0,time.time()]#position,time-position of x motor
    currentVelocity=[0,0]
    q=None
    previousTime=time.time()
    def __init__(self,target: str):
        print('hello')
        
        self.target=target

    def main(self,q,controlQueue):
        """The main loop for processing images
        Args:
            q: The queue for transmitting velocity data
            controlQueue: the queue used for shutting down operation
        """
        self.q=q
        #yV=0
        print('x')
        while True:#allow it to loop multiple times
            x=self.camera.capture()
            previousTime=self.currentPosition[1]#saves the time of the previous movement
            self.getCurrentPosition()
            self.currentPosition[1]=time.time()#assigns the current time
            self.positions.append([self.currentPosition[1],None,None])#adds the current time to the list of positions
            print('b')
            self.calculateCoordinates(x)#calculates the coordinates of the object in the image
            self.calculatePosition()#adds current angles of target to list
            self.calculateVelocity()#calculates velocity
            if not controlQueue.empty():
                break

    def getCurrentPosition(self):
        """calculates current position of motors"""
        print(self.currentVelocity[0])
        print(self.currentPosition[1]-self.previousTime)
        self.currentPosition[0]=self.currentPosition[0]+(self.currentVelocity[0]*(self.currentPosition[1]-self.previousTime))
        

    def calculatePosition(self):
        """calculates the current relative position of the object"""
        self.positions[-1][1]=self.currentPosition[0]+(self.calculateAngleImage(self.coordinates[-1][0],[1920,1080],'x'))
        
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
            print((coordinates-self.xMid)*anglePerPixel)
            return (coordinates-self.xMid)*anglePerPixel

    def calculateCoordinates(self,img):
        """Calculates the ccordintes of the object in the image
        Args:
            img: A colour numpy array of the image
        """

        try:        
            #start=time.time()
            bbox, label, conf = cv.detect_common_objects(img)
            #end=time.time()
            #print(start-end)
            #print(bbox,label)
            #output_image = draw_bbox(img, bbox, label, conf)
            #plt.imshow(output_image)
            #plt.show()            

            for i in range(0,len(label)):#x not being assigned-not finding target in list of images
                if label[i] == self.target:
                    x=bbox[i]


                
            xCo=(x[0]+x[2])/2
            yCo=(x[1]+x[3])/2
        except:
            xCo=0
            yCo=0

        self.coordinates.append([xCo,yCo])
        print(self.coordinates[-1])

    def calculateVelocity(self):
        """calculates and transmits the velocity to the Motor control class"""
        if self.coordinates[-1][0]<self.xMid:
            xV=-10
        else:
            xV=10
        if self.coordinates[-1][1]<self.yMid:
            yV=-10
        else:
            yV=10
        self.q.put([xV,yV])
        print('xV',xV)
        self.currentVelocity=[xV,yV]
        
    def determinevelocity(self):
        return (self.positions[-1][1]-self.positions[-2][1])/(self.positions[-1][0]-self.positions[-2][0])

