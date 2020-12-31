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
        enableWarnings: A variable to set whether warnings should be used
        enableFeedback: A varialbe to set whether feedback will be needed
        GUIFeatures: A varialbe to set whether GUI features are needed

        config: A dict of configuraion options

        controlQueueMC: The queue used for controlling the motor control object
        controlQueueImg: The queue used for controlling the imaging object
        dataQueue: The queue used for transmitting data from the imaging object to the motor control object
        imageReturnQueue: The queue used for returning images to be used in the GUI

        p1: The first process
        p2: The second process

        camera: A dict containing information on the camera to be used
        motorOne: A dict containg information on the x axis motor to be used
        motorTwo: A dict containg information on the y axis motor to be used
        computer: A dict containing information on the computer being used

        MC: The variable to be assigned to the motor control object
        Im: The variable to be assigned to the imaging object

        running: A vaariable which indicates whether the tracking is active

        target: The target set by the user

        images: A list of images captured
    """
    enableWarnings: bool = False
    enableFeedback: bool = False
    GUIFeatures: bool = False

    config: dict = None

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

    def __init__(self, 
                camera: dict = {'name': 'RPICam','orientation': 180,'Width':1280,'Height':720},
                motorOne: dict = {'name': "28BJY48_ULN2003_RPI", 'maxSpeed': 50, 'minWaitTime': 0.0016}, 
                motorTwo: dict = {'name': "28BJY48_ULN2003_RPI", 'maxSpeed': 50, 'minWaitTime': 0.0016}, 
                computer: dict = None,
                config: dict={'imagingMode': 'advanced'}):
        """
        initialises the class

        if the default hardware is being used there is no need to change the variables
        Args:
            camera: A dictionary to set up the camera
            motorOne: A dictionary to set up the x motor
            motorTwo: A dictionary to set up the y motor
            computer: currently serves no purpose but will likely gain a purpose as hardware is diversified
            config: serves to configure the behavior of the backend
        
        
        """
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
            while True:#constantly loops
                if not self.imageReturnQueue.empty():#checks if the queue is empty
                    x=self.imageReturnQueue.get()#gets the image and appends it to the array
                    self.images.append(x)
        else:
            raise GUIFeaturesNotEnabled('To use this function GUI features needs to be enabled')#raises an error if GUIFeatures are not enabled


    def track(self,target: str,options: dict = {}):
        """starts the tracking of the given target


        Args:
            target: The target to be tracked

        """
        self.target=target
        if self.checkTargetSupported(target):#checks the target is supported
            xMaxSpeed,yMaxSpeed=self.MC.getMaxSpeed()#gets the motors max speeds
            a=Imaging(self.dataQueue,self.controlQueueImg,self.imageReturnQueue,target,camera=self.camera,mode=self.config['imagingMode'],extras={'xMaxSpeed':xMaxSpeed,'yMaxSpeed':yMaxSpeed})#creates an imaging object

            if self.GUIFeatures:#starts the recording of frames if GUI features is enabled
                t=threading.Thread(target=self.recordFrames,args=())
                t.start()

            #if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
            warnings.warn('tracking starting')#warns the user tracking is starting
            self.p1 = multiprocessing.Process(target=a.main,args=())#creates and starts the processes - They are not joined so the code can continue executing
            self.p1.start()
            self.p2 = multiprocessing.Process(target=self.MC.main,args=(self.dataQueue, self.controlQueueMC,))
            self.p2.start()
            self.running=True#sets running to true
            
        else:
            raise ValueError('target not supported')
        
    def trackLimited(self, target: str, limit1: float = 0, limit2: float = 0,options: dict = {}):
        """starts the tracking of the given target but limits the movement of the x motor 

        Aside from the limits on the x axis range it can track it is pretty much a clone of track() so the same usage reccomendations and restrictions apply
        such as not starting it in a thread as or a process as these things should not be necesary due to the fact in this version of the code it does not also kill the processes and they may cause issues

        Args:
            target: The target to be tracked
            limit1: the first limit
            limit2: the second limit

        """
        self.target=target
        if self.checkTargetSupported(target):
            a=Imaging(self.dataQueue,self.controlQueueImg,target,camera=self.camera,mode=self.config['imagingMode'],extras={'xMaxSpeed':xMaxSpeed,'yMaxSpeed':yMaxSpeed})
 
            if self.GUIFeatures:
                t=threading.Thread(target=self.recordFrames,args=())
                t.start()
            
            if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
                warnings.warn('tracking starting')
                self.p1 = multiprocessing.Process(target=a.mainLimited,args=(limit1, limit2,))
                self.p1.start()
                self.p2 = multiprocessing.Process(target=self.MC.main,args=(self.dataQueue, self.controlQueueMC,))
                self.p2.start()
                self.running=True

        else:
            raise ValueError('target not supported')

    def followPath(self,path):
        """A function to track along a path-Not implemented
        
        Args:
            path: The path to follow
        """
        raise FeatureNotImplemented()
        
            



    def terminate(self):
        """Used to end the tracking

        Puts signal "1" on the control Queues and then waits until the processes have stopped before issuing kill commands
        """
        #print(self.running)
        if self.running == True:#checks running is true as otherwise an error will occur from attempting is_alive() on a none object
            self.controlQueueMC.put(1)#signals the objects
            self.controlQueueImg.put(1)
            warnings.warn('terminating')
            while True:#loops as the processes have to finish what they are doing
                if not (self.p1.is_alive() and self.p2.is_alive()):#waits for them to be finished
                    self.p1.kill()#kills them
                    self.p2.kill()
                    self.running=False#sets running to false
                    break
        else:
            raise NotTracking('nothing to terminate')#raises an error which can be caught
       
        #code 1 is for termination
        #other codes may be added for other purposes


    def calibrateInteractive(self):
        """An interactive calibration tool
        This will likely be removed in a future verson
        """

        print('welcome to the calibration tool')
        waitTime=float(input('please enter the first wait time. The default is: '+'0.0016'+': '))#gather the data required
        distance=float(input('please enter the distance, higher is better: '))
        increment=float(input('please enter the wait time increment. The recommended is 0.0001:  '))
        while True:
            self.MC.setWaitTime(waitTime)#set the wait time
            speed1=self.MC.measureMotorSpecsOne(distance)#measures the speed
            print('x motor speed is: ',speed1)
            #print('y motor speed is: ',speed2)
            worked=input('please enter (Y/n) for whether it worked')#checks if it worked
            if worked=='n':
                break
            waitTime-=increment#decreases the wait time
        waitTime+=increment#sets the wait time to the last one that worked
        print('the changes are being set')
        self.MC.setMaxSpeed(speed1)#sets the new values
        self.MC.setWaitTime(waitTime)
        

    def calibrateZero(self,waitTime,distance):
        """A non interactive version of the calibration tool that is likely to be removed in a future version"""
        self.MC.setWaitTime(waitTime)#sets the wait time
        speed=self.MC.measureMotorSpecsOne(distance)#measures the speed
        return speed,speed#returns the speed

    def setSpecsZero(self,waitTime,speed1,speed2):
        """A method for setting changes such as waitTime and speed but may be removed in future versions due to only supporting the basic motors"""
        self.MC.setWaitTime(waitTime)#sets the wait time
        self.MC.setMaxSpeed(speed1) #sets the max speed
        

    def getSupportedTargets(self) -> list:
        """returns a list of the supported targets
        Returns:
            A list of supported targets
        """
        OR=ObjectRecognition(None)
        return OR.getTargets()
        

    def checkTargetSupported(self,target) -> bool:
        """checks if the target is supported

        Args:
            target: The target to check for

        Returns:
            True if it is supported otherwise False
        """
        if target in self.getSupportedTargets():#checks the target is in the list of supported targets
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
        """returns the most recent frame from the camera
        Returns:
            img, box, label, confidence where img is the image as a numpy array, box is an array of bounding boxes, label is an array of bounding boxes, confidence is an array of confidences for the labels
        """
        
        

        if not self.GUIFeatures:#checks if GUIFeatures is True as this changes how the function should behave
            if self.imageReturnQueue.empty():#raises an error if the queue is empty
                #warnings.warn('no image availble')
                raise NoImageAvailable('no image available to be returned')
            
            while not self.imageReturnQueue.empty():#keeps getting until the queue is empty
                x=self.imageReturnQueue.get()
                if self.imageReturnQueue.empty():
                    break
        
            img=x['img']#gets the data to be returned from the dict
            box=x['box']
            confidence=x['confidence']
            label=x['label']
            return img, box, label, confidence
        else:
            if len(self.images)==0:#raises an error if the list is empty
                raise NoImageAvailable('no image available to be returned')

            img=self.images[-1]['img']#gets the data to be returned from the dict
            box=self.images[-1]['box']
            confidence=self.images[-1]['confidence']
            label=self.images[-1]['label']
            return img, box, label, confidence

    def getAllFrames(self) -> list:
        """returns all frames as an array
        Returns:
            An array of dictionaries where each dictionary is a frame.
            The dicts contain:
            'img':The image
            'box':A list of bounding boxes
            'confidence':A list of confidences
            'label':A list of labels
        """
        if self.GUIFeatures:
            return self.images
        else:
            raise GUIFeaturesNotEnabled('To use this function GUI features needs to be enabled')
    
    def getFrameAsImage(self,resolution: list):
        """used to return a frame as an image.

        Ideal for use when the user has little experience with the required libraries for processing the image
        Args:
            resolution: The resolution as a list of the form [Width,Height]
        Returns:
            An image with the boxes and labels etc already applied
        """
        i,b,l,c=self.getFrame()#calls the get frame function

        image = draw_bbox(i, b, l, c)#adds bounding boxes etc to the image
        image=cv2.resize(image,(resolution[0],resolution[1]),interpolation = cv2.INTER_AREA)#resizes it
        return image

    def getCurrentAnalytics(self) -> dict:
        """returns current analytics data such as speed or target acquisition status """
        raise FeatureNotImplemented()

    def getSessionAnalytics(self) -> dict:
        """get analytics about the session such as percentage of time the target was acquired for"""
        raise FeatureNotImplemented()

    def setWarnings(self,warningMode: bool):
        """sets whether the user wants warnings or not"""
        self.enableWarnings=warningMode
        if not self.enableWarnings:
            warnings.filterwarnings('ignore')#if warnings not enabled disable them

    def setGUIFeatures(self,choice: bool):
        """sets whether GUI features are to be used or not
        This is likely to have a performance impact so only activate if necesary
        Args:
            choice: whether the features should be enabled or not
        """
        self.GUIFeatures=choice

    def setFeedback(self,choice: bool):
        """sets whether feedback recording will be used
        Args:
            choice: whether feedback should be enabled or not
        """
        self.enableFeedback=choice
        

    def isRunning(self) -> bool:
        """used to check whether the tracking is active
        Returns:
            True if running otherwise False
        """
        return self.running


    def isImageAvailable(self) -> bool:
        """checks if an image is available to return
        Returns:
           True if an image is available otherwise false 
        """
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
    """converts an image created by the program to one suitable for tkinter
    Args:
        image: The image to be converted

    Returns:
        An image in the format required for displaying in tkinter
    """
    b,g,r = cv2.split(image)
    img = cv2.merge((r,g,b))
    img = Image.fromarray(img)
    return ImageTk.PhotoImage(image=img)
            
