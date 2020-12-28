import multiprocessing
import threading
import queue
import sys
import time
import warnings

from .Imaging import *
from .MotorControl import *
from .errors import *

import cv2
from cvlib.object_detection import draw_bbox
from PIL import Image, ImageTk

class MotorisedCameraTracking:
    """The API for the Camera Tracking Library

    This class contains all the methods required to operate a motorised tracking camera
    
    Attributes:
        controlQueue: The queue used for controlling the other classes
    """
    enableWarnings=False
    enableFeedback=False
    GUIFeatures=False

    config:dict=None

    controlQueueMC=multiprocessing.Queue()
    controlQueueImg=multiprocessing.Queue()
    dataQueue=multiprocessing.Queue()
    imageReturnQueue=multiprocessing.Queue()

    p1=None
    p2=None

    camera: dict = None
    motorOne: dict = None
    motorTwo: dict = None
    computer: dict = None

    MC=None
    Im=None

    running: bool = False#

    target:str = None
    
    images=[]

    def __init__(self, camera: dict = {'name': 'RPICam','orientation': 180,'Width':1280,'Height':720}, motorOne: dict = {'name': "28BJY48_ULN2003_RPI", 'maxSpeed': 24, 'minWaitTime': 0.0016}, motorTwo: dict = {'name': "28BJY48_ULN2003_RPI", 'maxSpeed': 24, 'minWaitTime': 0.0016}, computer: dict = None,config:dict={'imagingMode':'advanced'}):
        warnings.warn('the library only supports a limited range of hardware currently')
        self.camera=camera
        self.motorOne=motorOne
        self.motorTwo=motorTwo
        self.computer=computer
        self.MC = MotorControl(motorOne=self.motorOne, motorTwo=self.motorTwo)
        #self.Im = 
        self.config=config
        

    def recordFrames(self):
        """if called and GUI features are activated it will record all the frames from the camera"""
        if self.GUIFeatures:
            while True:
                if not self.imageReturnQueue.empty():
                    x=self.imageReturnQueue.get()
                    self.images.append(x)
        else:
            raise GUIFeaturesNotEnabled('To use this function GUI features needs to be enabled')


    def track(self,target: str):#the queue is used for sending a termination signal
        """Tracks the object until a terminate signal is sent
        Args:
            target: The target to be tracked

        """
        self.target=target
        if self.checkTargetSupported(target):
            xMaxSpeed,yMaxSpeed=self.MC.getMaxSpeed()
            a=Imaging(self.dataQueue,self.controlQueueImg,self.imageReturnQueue,target,camera=self.camera,mode=self.config['imagingMode'],extras={'xMaxSpeed':xMaxSpeed,'yMaxSpeed':yMaxSpeed})

            if self.GUIFeatures:
                t=threading.Thread(target=self.recordFrames,args=())
                t.start()

            #if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
            warnings.warn('tracking starting')
            self.running=True
            #print(self.running)
            self.p1 = multiprocessing.Process(target=a.main,args=())
            self.p1.start()
            self.p2 = multiprocessing.Process(target=self.MC.main,args=(self.dataQueue, self.controlQueueMC,))
            self.p2.start()
                #self.p1.join()
                #self.p2.join()

            #self.p1.kill()
            #self.p2.kill()
            #print('exiting')
            #sys.exit()
            
        else:
            raise ValueError('target not supported')
        
    def trackLimited(self, target: str, limit1: float = 0, limit2: float = 0):
        """Tracks the object until a terminate signal is sent
        Args:
            target: The target to be tracked
            limit1: the first limit
            limit2: the second limit

        """
        self.target=target
        if self.checkTargetSupported(target):
            a=Imaging(self.dataQueue,self.controlQueueImg,target)
            #MC=MotorControl()
            #dataQueue=queue.Queue()
            if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
                self.p1 = multiprocessing.Process(target=a.mainLimited,args=(limit1, limit2,))
                self.p1.start()
                self.p2 = multiprocessing.Process(target=self.MC.main,args=(self.dataQueue, self.controlQueueMC,))
                self.p2.start()
                #self.p1.join()
                #self.p2.join()
            #self.p1.kill()
            #self.p2.kill()
            #sys.exit()

        else:
            raise ValueError('target not supported')

    def followPath(self,path):
        """A function to track along a path"""
        pass
            



    def terminate(self):
        """Used to end the tracking

        Puts signal "1" on the control Queue
        """
        #print(self.running)
        if self.running == True:
            self.controlQueueMC.put(1)
            self.controlQueueImg.put(1)
            warnings.warn('terminating')
            while True:
                if not (self.p1.is_alive() and self.p2.is_alive()):
                    self.p1.kill()
                    self.p2.kill()
                    break
        else:
            raise NotTracking('nothing to terminate')
        
        #code 1 is for termination
        #other codes may be added for other purposes


    def calibrateInteractive(self):
        """An interactive calibration tool"""

        print('welcome to the calibration tool')
        waitTime=float(input('please enter the first wait time. The default is: '+'0.0016'+': '))
        distance=float(input('please enter the distance, higher is better: '))
        increment=float(input('please enter the wait time increment. The recommended is 0.0001:  '))
        while True:
            self.MC.setWaitTime(waitTime)


            speed1=self.MC.measureMotorSpecsOne(distance)
            print('x motor speed is: ',speed1)
            #print('y motor speed is: ',speed2)
            worked=input('please enter (Y/n) for whether it worked')
            if worked=='n':
                break
            waitTime-=increment
        waitTime+=increment
        print('the changes are being set')
        self.MC.setMaxSpeed(speed1)
        self.MC.setWaitTime(waitTime)
        

    def calibrateZero(self,waitTime,distance):
        self.MC.setWaitTime(waitTime)
        speed=self.MC.measureMotorSpecsOne(distance)
        return speed,speed

    def setSpecsZero(self,waitTime,speed1,speed2):
        self.MC.setWaitTime(waitTime)
        self.MC.setMaxSpeed(speed1)  
        

    def getSupportedTargets(self):
        """returns a list of the supported targets"""
        OR=ObjectRecognition(None)
        return OR.getTargets()
        

    def checkTargetSupported(self,target):
        """checks if the target is supported

        Args:
            target: The target to check for
        """
        if target in self.getSupportedTargets():
            return True
        else:
            return False
        
    
    def aim(self, distance: float, axis: str):
        """Used to aim the motors through the GUI before tracking begins
        Args:
            distance: The distance to move
            axis: the axis to move on
        """
        self.MC.runDisplacement(distance,axis)

    

    def getFrame(self):
        """returns the most recent frame from the camera"""
        
        #empty the queue

        if not self.GUIFeatures:
            if self.imageReturnQueue.empty():
                #warnings.warn('no image availble')
                raise NoImageAvailable('no image available to be returned')
            
            while not self.imageReturnQueue.empty():
                x=self.imageReturnQueue.get()
                if self.imageReturnQueue.empty():
                    break
        
            img=x['img']
            box=x['box']
            confidence=x['confidence']
            label=x['label']
            return img, box, label, confidence
        else:
            if len(self.images)==0:
                raise NoImageAvailable('no image available to be returned')
            img=self.images[-1]['img']
            box=self.images[-1]['box']
            confidence=self.images[-1]['confidence']
            label=self.images[-1]['label']
            return img, box, label, confidence

    def getAllFrames(self):
        """returns all frames as an array"""
        if self.GUIFeatures:
            return self.images
        else:
            raise GUIFeaturesNotEnabled('To use this function GUI features needs to be enabled')
    
    def getFrameAsImage(self,resolution:list):
        """used to return a frame as an image.

        Ideal for use when the user has little experience with the required libraries
        """
        i,b,l,c=self.getFrame()

        image = draw_bbox(i, b, l, c)
        image=cv2.resize(image,(resolution[0],resolution[1]),interpolation = cv2.INTER_AREA)
        return image

    def getCurrentAnalytics(self):
        pass

    def getSessionAnalytics(self):
        pass

    def setWarnings(self,warningMode:bool):
        """sets whether the user wants warnings or not"""
        self.enableWarnings=warningMode
        if not self.enableWarnings:
            warnings.filterwarnings('ignore')

    def setGUIFeatures(self,choice:bool):
        """use True if you want to use a GUI else False.
        This is likely to have a performance imapct so only activate if necesary
        """
        self.GUIFeatures=choice

    def setFeedback(self,choice:bool):
        """sets whether feedback recording will be used"""
        self.enableFeedback=choice
        

    def isRunning(self):
        """returns if the tracking is active"""
        return self.running


    def isImageAvailable(self):
        """checks if an image is available to return"""
        if not self.GUIFeatures:
            if self.imageReturnQueue.empty():
                return False
            else:
                return True

        else:
            if len(self.images)==0:
                return False
            else:
                return True


        



def convertImageTkinter(image):
    """convers an image created by the program to one suitable for tkinter
    Args:
        image: The image to be converted
    """
    b,g,r = cv2.split(image)
    img = cv2.merge((r,g,b))
    img = Image.fromarray(img)
    return ImageTk.PhotoImage(image=img)
            
