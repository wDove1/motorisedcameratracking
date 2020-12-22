import multiprocessing
import threading
import queue
import sys
import time
import warnings

from .Imaging import *
from .MotorControl import *




class MotorisedCameraTracking:
    """The API for the Camera Tracking Library

    This class contains all the methods required to operate a motorised tracking camera
    
    Attributes:
        controlQueue: The queue used for controlling the other classes
    """
    controlQueue=multiprocessing.Queue()
    dataQueue=multiprocessing.Queue()
    camera: dict = None
    motorOne: dict = None
    motorTwo: dict = None
    computer: dict = None

    MC=None
    Im=None
    

    def __init__(self,camera: dict = None, motorOne: dict = {'name': "28BJY48_ULN2003_RPI", 'maxSpeed': 24, 'minWaitTime': 0.0016}, motorTwo: dict = {'name': "28BJY48_ULN2003_RPI", 'maxSpeed': 24, 'minWaitTime': 0.0016}, computer: dict = None):
        warnings.warn('the library only supports a limited range of hardware currently')
        self.camera=camera
        self.motorOne=motorOne
        self.motorTwo=motorTwo
        self.computer=computer
        self.MC = MotorControl(motorOne=self.motorOne, motorTwo=self.motorTwo)
        #self.Im = 
        

    

    def track(self,target: str):#the queue is used for sending a termination signal
        """Tracks the object until a terminate signal is sent
        Args:
            target: The target to be tracked

        """

        if self.checkTargetSupported(target):
            
            a=Imaging(self.dataQueue,self.controlQueue,target)

            

            if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
                warnings.warn('tracking starting')
                p1 = multiprocessing.Process(target=a.main,args=())
                p1.start()
                p2 = multiprocessing.Process(target=self.MC.main,args=(self.dataQueue, self.controlQueue,))
                p2.start()
                p1.join()
                p2.join()

            p1.kill()
            p2.kill()
            #print('exiting')
            sys.exit()
            
        else:
            raise ValueError('target not supported')
        
    def trackLimited(self, target: str, limit1: float = 0, limit2: float = 0):
        """Tracks the object until a terminate signal is sent
        Args:
            target: The target to be tracked
            limit1: the first limit
            limit2: the second limit

        """
        if self.checkTargetSupported(target):
            a=Imaging(self.dataQueue,self.controlQueue,target)
            #MC=MotorControl()
            #dataQueue=queue.Queue()
            if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
                p1 = multiprocessing.Process(target=a.mainLimited,args=(limit1, limit2,))
                p1.start()
                p2 = multiprocessing.Process(target=self.MC.main,args=(self.dataQueue, self.controlQueue,))
                p2.start()
                p1.join()
                p2.join()
            p1.kill()
            p2.kill()
            sys.exit()

        else:
            raise ValueError('target not supported')

    def followPath(self,path):
        """A function to track along a path"""
        pass
            



    def terminate(self):
        """Used to end the tracking

        Puts signal "1" on the control Queue
        """
        self.controlQueue.put(1)
        warnings.warn('terminating')
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
        MC.runDisplacement(distance,axis)




