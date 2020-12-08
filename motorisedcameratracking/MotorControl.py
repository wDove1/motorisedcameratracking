#modified for compatability with new motor1 class
import _thread
import threading
import time
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
        *rename q to dataQueue
        *investigate adding acceleration support
    """
    
    M1=M_28BJY48_ULN2003_RPI(stepPins=[17,22,23,24],maxSpeed=24)
    #M1=Motor('virtual','virtual','virtual',{})
    M2=M_28BJY48_ULN2003_RPI(stepPins=[13,6,5,12],maxSpeed=24)
    #Config=Config()
    timeUnit: float = 2.0#test value instead of 0.25 for issue with loop
    xVelocity: float = 0
    yVelocity: float = 0
    xAcceleration: float = 0
    yAcceleration: float = 0
    q=None
    
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
            

            if not self.q.empty():
                x=self.q.get()
                print('x=',x)
                self.xVelocity=x[0]
                time.sleep(self.timeUnit)
            #else:
                #print('empty')
            if not controlQueue.empty():
                break
                

    def xMotor(self,controlQueue):
        """The method to control the motor that moves on the x axis
        Args:
            controlQueue: Used for shutting down the program
        """
        while True:
            #print(self.xVelocity)
            if self.xVelocity !=0:
                print('running')#keeps printimng while motor is meant to be running
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
        self.q=q
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

        
