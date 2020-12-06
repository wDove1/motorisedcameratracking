import multiprocessing
import threading
import queue
import sys
import time

from measuremotorspecslib import *

from .Imaging import *
from .MotorControl import *#check for issues with names-this refairs to the local file as opposed to the library




class MotorisedCameraTracking:

    """The API for the Camera Tracking Library

    This class contains all the methods required to operate a motorised tracking camera
    
    Attributes:
        controlQueue: The queue used for controlling the other classes
    """
    controlQueue=queue.Queue()

    def track(self,target,options=None):#the queue is used for sending a termination signal
        """Tracks the object until a terminate signal is sent
        Args:
            target(str): The target to be tracked
            options(dict): A dictionary of options that may be changed every time tracking is started
        """

        print('z')
        a=Imaging(target)
        MC=MotorControl()
        dataQueue=queue.Queue()
        #print(__name__)

        if __name__ == 'motorisedcameratracking.MotorisedCameraTracking':
            #print('###########')
            p1 = threading.Thread(target=a.main,args=(dataQueue, self.controlQueue,))
            #print('###########')
            p1.start()
            #print('###########')
            p2 = threading.Thread(target=MC.main,args=(dataQueue, self.controlQueue,))
            #print('###########')
            p2.start()
            #print('###########')
            p1.join()
            print('###########')
            p2.join()
            #print('###########')
        print('f')
        
        p1.kill()
        p2.kill()
        print('exiting')
        sys.exit()
        
    def trackLimited(self,target,limit1=0,limit2=0):
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
        p1.kill()
        p2.kill()
        sys.exit()

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

    
    #add functions for positioning motors
    
    def aim(self,distance,axis):
        """Used to aim the motors through the GUI before tracking begins
        Args:
            distance: The distance to move
            axis: the axis to move on
        """
        MC.runDisplacement(distance,axis)


