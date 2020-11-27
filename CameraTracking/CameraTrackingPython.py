import multiprocessing
import queue
#import _thread
from textUI import *
from Imaging import *
from MotorControl import *
#from GUI import *
import sys
import time

class CameraTrackingPython:
    p1=None
    p2=None

    def track(self,target,queue):#the queue is used for sending a termination signal
        print('z')
        a=Imaging(target)
        MC=MotorControl()
        q=multiprocessing.Queue()
        if __name__ == 'CameraTrackingPython':
            p1 = multiprocessing.Process(target=a.main,args=(q,))
            p1.start()
            p2 = multiprocessing.Process(target=MC.main,args=(q,))
            p2.start()
            p1.join()
            p2.join()

        while q.empty():
            print('f')
        stop=q.get()
        if stop == 1:
            p1.kill()
            p2.kill()
            sys.exit()
        


    


    def terminate(self):
        self.p1.kill()
        self.p2.kill()
        sys.exit()
