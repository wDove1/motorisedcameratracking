import multiprocessing
import queue


from Imaging import *
from MotorControl import *#check for issues with names-this refairs to the local file as opposed to the library

from MeasureMotorSpecsLib import *
import sys
import time

class MotorisedCameraTracking:

    """The API for the Camera Tracking Library

    This class contains all the methods required to operate a motorised tracking camera
    
    Attributes:
        controlQueue: The queue used for controlling the other classes
    """
    controlQueue=multiprocessing.Queue()

    def track(self,target,options=None):#the queue is used for sending a termination signal
        """Tracks the object until a terminate signal is sent

    
        Args:
            target(str): The target to be tracked
            options(dict): A dictionary of options that may be changed every time tracking is started
        """
        print('z')
        a=Imaging(target)
        MC=MotorControl()
        controlQueue=multiprocessing.Queue()
        q=multiprocessing.Queue()

        if __name__ == 'CameraTrackingPython':
            p1 = multiprocessing.Process(target=a.main,args=(q, self.controlQueue,))
            p1.start()
            p2 = multiprocessing.Process(target=MC.main,args=(q, self.controlQueue,))
            p2.start()
            p1.join()
            p2.join()
        print('f')
        #while queue.empty():
        #    print('f')
        #command=q.get()
        #if command == 1:
        #    print('stoppimg')
        #    controlQueue.put(True)
        #    while p1.is_alive() and p2.is_alive():
        #        pass
            
        p1.kill()
        p2.kill()
        print('exiting')
        sys.exit()
        


    


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
    
    def aim(self,distance):
        """Used to aim the motors through the GUI before tracking begins
        Args:
            distance: The distance to move
        """
        pass


