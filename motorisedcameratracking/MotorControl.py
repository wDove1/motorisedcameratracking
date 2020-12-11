#modified for compatability with new motor1 class
import _thread
import threading
import time
import queue
from numba import *
from motorcontrollib import M_28BJY48_ULN2003_RPI
from typing import *
from .Config import *
class MotorControl:
    """A class to control the motors operation
    Attributes:
        M1: The first motor (x axis)
        M2: The second motor (y axis)
        timeUnit: How frequently the velocity will be updated etc
        xVelocity: The velocity M1 will run at
        yVelocity: The velocity M2 will run at
        xAcceleration: Currently unused
        yAcceleration: Currently unused
        q: The queue used for transmitting velocity information
    Todo:
        
        *investigate adding acceleration support
    """
    
    M1=None
    M2=None
    #Config=Config()
    timeUnit: float = 0.25#test value instead of 0.25 for issue with loop
    xVelocity: float = 0
    yVelocity: float = 0
    xAcceleration: float = 0
    yAcceleration: float = 0
    dataQueue=None

    def __init__(self, motorOne: dict, motorTwo: dict):
        if motorOne['name']=="28BJY48_ULN2003_RPI":
            self.M1=M_28BJY48_ULN2003_RPI(stepPins=[17,22,23,24],maxSpeed=motorOne['maxSpeed'],minWaitTime=motorOne['minwaitTime'])
        if motorTwo['name']=="28BJY48_ULN2003_RPI":
            self.M1=M_28BJY48_ULN2003_RPI(stepPins=[17,22,23,24],maxSpeed=motorTwo['maxSpeed'],minWaitTime=motorOne['minwaitTime'])
    
    def incrementer(self,controlQueue):
        """updates the velocity with the accelerations
        Args:
            controlQueue: Used for shutting down the program
        """
        while True:
            t1=time.time()
            self.xVelocity+=self.xAcceleration
            self.yVelocity+=self.yAcceleration
            t2=time.time()
            t=t2-t1
            time.sleep(self.timeUnit-t)
            #print('a')

    def updater(self,controlQueue):#fix this
        """updates the velocities as new ones are calculated
        Args:
            controlQueue: Used for shutting down the program
        """
        print('c')
        while True:
            

            if not self.dataQueue.empty():
                x=self.dataQueue.get()
                print('x=',x)
                self.xVelocity=x[0]
                self.yVelocity=x[1]
                time.sleep(self.timeUnit)

            if not controlQueue.empty():
                break
                

    def xMotor(self,controlQueue):
        """The method to control the motor that moves on the x axis
        Args:
            controlQueue: Used for shutting down the program
        """
        while True:
            if self.xVelocity !=0:
                self.M1.runVelocityT(self.xVelocity,self.timeUnit)
            if not controlQueue.empty():
                break

    def yMotor(self,controlQueue):
        """The method to control the motor that moves on the y axis
        Args:
            controlQueue: Used for shutting down the program
        """

        while True:
            if self.yVelocity !=0:
                self.M2.runVelocityT(self.yVelocity,self.timeUnit)
            if not controlQueue.empty():
                break

    def main(self,q,controlQueue):
        """The main method that starts the threads to allow the motors to run
        Args:
            q:The queue for transmitting velocity data
            controlQueue: Used for shutting down the program
        """
        print('y')
        self.dataQueue=q
        #_thread.start_new_thread(self.incrementer,())
        print('d')
        t1=threading.Thread(target=self.updater,args=(controlQueue,))
        t2=threading.Thread(target=self.xMotor,args=(controlQueue,))
        t3=threading.Thread(target=self.yMotor,args=(controlQueue,))
        t1.start()
        t2.start()
        t3.start()
        #t4.start()

    def xAdjustL(self):
        self.M1.runDisplacement(-5)

    def xAdjustR(self):
        self.M1.runDisplacement(5)
            
    def yAdjustU(self):
        self.M2.runDisplacement(5)

    def yAdjustD(self):
        self.M2.runDisplacement(-5)

    def getVelocity(self):
        return self.xV,self.yV

    def runDisplacement(self,distance,axis):
        """Runs the motor a set distance useful for aiming the motors
            Args:
                distance: The displacement the motor will move
                axis: The axis to be manipulated
        """
        if axis == "x":
            M1.runDispalcement(distance)
        elif axis == "y":
            M2.runDispalcement(distance)

    def xMotorTest(self,distance,returnQueue):
        t1=time.time()
        self.M1.runDisplacement(distance)
        t2=time.time()
        returnQueue.put(t2-t1)
    
    def yMotorTest(self,distance,returnQueue):
        t1=time.time()
        self.M2.runDisplacement(distance)
        t2=time.time()
        returnQueue.put(t2-t1)
    
    def measureMotorSpeedOne(self,distance):
        """for measuring the motor speed with 2 default motors"""
        controlQueue=queue.Queue()
        returnQueue1=queue.Queue()
        returnQueue2=queue.Queue()
        t1=threading.Thread(target=self.updater,args=(controlQueue,))
        t2=threading.Thread(target=self.xMotorTest,args=(distance,returnQueue1,))
        t3=threading.Thread(target=self.yMotorTest,args=(distance,returnQueue2,))
        t1.start()
        t2.start()
        t3.start()
        while returnQueue1.empty() and returnQueue2.empty():
            pass
        speed1=distance/returnQueue1.get()
        speed2=distance/returnQueue2.get()
        return speed1,speed2
        

        
