import multiprocessing
import threading
import queue
import sys
import time

from measuremotorspecslib import *

from .Imaging import *
from .MotorControl import *




class MotorisedCameraTracking:

    """The API for the Camera Tracking Library

    This class contains all the methods required to operate a motorised tracking camera
    
    Attributes:
        controlQueue: The queue used for controlling the other classes
    """
    controlQueue=multiprocessing.Queue()

    def track(self,target: str):#the queue is used for sending a termination signal
        """Tracks the object until a terminate signal is sent
        Args:
            target(str): The target to be tracked

        """

        if self.checkTargetSupported(target):
            a=Imaging(target)
            MC=MotorControl()
            dataQueue=multiprocessing.Queue()
            #print(__name__)

            if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
                p1 = multiprocessing.Process(target=a.main,args=(dataQueue, self.controlQueue,))
                p1.start()
                p2 = multiprocessing.Process(target=MC.main,args=(dataQueue, self.controlQueue,))
                p2.start()
                p1.join()
                p2.join()


            
            p1.kill()
            p2.kill()
            print('exiting')
            sys.exit()
        else:
            raise ValueError('target not supported')
        
    def trackLimited(self, target:str, limit1:float = 0, limit2:float = 0):
        """Tracks the object until a terminate signal is sent
        Args:
            target(str): The target to be tracked
            limit1: the first limit
            limit2: the second limit

        """
        if self.checkTargetSupported(target):
            a=Imaging(target)
            MC=MotorControl()
            dataQueue=queue.Queue()
            if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
                p1 = threading.Thread(target=a.mainLimited,args=(dataQueue, self.controlQueue, limit1, limit2,))
                p1.start()
                p2 = threading.Thread(target=MC.main,args=(dataQueue, self.controlQueue,))
                p2.start()
                p1.join()
                p2.join()
            #p1.kill()
            #p2.kill()
            sys.exit()

        else:
            raise ValueError('target not supported')

    def followPath(self,path):
        pass



    def terminate(self):
        """Used to end the tracking

        Puts signal "1" on the control Queue
        """
        self.controlQueue.put(1)
        #code 1 is for termination
        #other codes may be added for other purposes


    def calibrateInteractive(self):
        y=MeasureMotorSpecs()
        y.measureInteractive()

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


