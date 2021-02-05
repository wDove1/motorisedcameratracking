#modified for compatability with new motor1 class
import threading
import time
import queue
import multiprocessing
import warnings
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
    timeUnit: float = 0.5#test value instead of 0.25 for issue with loop
    xVelocity: float = 0
    yVelocity: float = 0
    xAcceleration: float = 0
    yAcceleration: float = 0
    dataQueue=None
    xVQueue=None
    yVQueue=None
    
    ImPipe=None

    xDisplacement=0
    yDisplacement=0
    xDQueue=None
    yDQueue=None

    trackingThread=None
    tracking=False

    def __init__(self, motorOne: dict, motorTwo: dict):
        if motorOne['name']=="28BJY48_ULN2003_RPI":
            self.M1=M_28BJY48_ULN2003_RPI(stepPins=[17,22,23,24],maxSpeed=motorOne['maxSpeed'],minWaitTime=motorOne['minWaitTime'])
        else:
            self.M1=M_Virtual()
            
        if motorTwo['name']=="28BJY48_ULN2003_RPI":
            self.M2=M_28BJY48_ULN2003_RPI(stepPins=[13,6,5,12],maxSpeed=motorTwo['maxSpeed'],minWaitTime=motorTwo['minWaitTime'])
        else:
            self.M2=M_Virtual()
    
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

    #def updater(self,xVQueue,yVQueue,xDQueue,yDQueue):#fix this
    #    """updates the velocities as new ones are calculated
    #    Args:
    #        controlQueue: Used for shutting down the program
    #    """
        
    #    warnings.warn('MotorControl main is now active')
    #    self.xDisplacement=0
    #    self.yDisplacement=0
    #    while True:
    #        print('xV a',self.xVelocity)
    #        print('xD a',self.xDisplacement)
    #        #warnings.warn('MotorControl has looped')
    #        if self.dataQueue.qsize() <= 1:
                
    #            #print('MotorControl running as ideal')
    #            empty=self.dataQueue.empty()
    #            #print(empty)
            
    #            if not empty:
    #                x=self.dataQueue.get()
    #                self.xVelocity=x[0]
    #                self.yVelocity=x[1]
                    

    #            #print(self.xVelocity)

    #            #print('x ',self.xVelocity)
    #            #print('y ',self.yVelocity)

    #            t2=threading.Thread(target=self.xMotor)
    #            t3=threading.Thread(target=self.yMotor)

    #            t2.start()
    #            t3.start()
    #            t2.join()
    #            t3.join()
    #            #print('threads closed')
                
    #        else:
    #            #print('clearing excess items from the queue')
    #            while self.dataQueue.qsize() >= 1:
    #                x=self.dataQueue.get()
    #            #x=self.dataQueue.get()
    #            self.xVelocity=x[0]
    #            self.yVelocity=x[1]

    #            #print(self.xVelocity)

            

    #            t2=threading.Thread(target=self.xMotor)
    #            t3=threading.Thread(target=self.yMotor)

    #            t2.start()
    #            t3.start()
    #            t2.join()
    #            t3.join()

    #        self.xDisplacement+=self.xVelocity*self.timeUnit
    #        self.yDisplacement+=self.yVelocity*self.timeUnit
    #        #print('x ',self.xVelocity)
    #        xVQueue.put(self.xVelocity)
    #        #print('queue size 1: ', xVQueue.qsize())
    #        #print('xV from queue:', xVQueue.get())
    #        yVQueue.put(self.yVelocity)

    #        xDQueue.put(self.xDisplacement)
    #        yDQueue.put(self.yDisplacement)

    #        self.ImPipe.send({'xV':self.xVelocity,'yV':self.yVelocity,'xD':self.xDisplacement,'yD':self.yDisplacement})

    #        if self.ImPipe.poll():
    #            data=self.ImPipe.recv()
    #            if data['recentre']:
    #                warnings.warn('recentring')
    #                self.xVelocity=0
    #                self.yVelocity=0
    #                self.M1.runDisplacement(-self.xDisplacement)
    #                self.M2.runDisplacement(-self.yDisplacement)
    #                self.xDisplacement=0
    #                self.yDisplacement=0
    #        if not self.controlQueue.empty():
    #            warnings.warn('MotorControl is Exiting')
    #            break

    def updater(self,xVQueue,yVQueue,xDQueue,yDQueue):
        warnings.warn('MotorControl main is now active')
        self.xDisplacement=0#sets the initial value of the variables
        self.yDisplacement=0
        data={'xV':0,'yV':0,'recentre':False}
        while True:
            if self.ImPipe.poll():#gets the most recent data from the pipe
                while True:
                    if self.ImPipe.poll():
                        data=self.ImPipe.recv()
                    else:
                        break

            if data['recentre']:#checks if recentring is required
                warnings.warn('recentring')
                self.xVelocity=0
                self.yVelocity=0
                self.M1.runDisplacement(-self.xDisplacement)#returns it to the start
                self.M2.runDisplacement(-self.yDisplacement)
                self.xDisplacement=0#resets the displacement
                self.yDisplacement=0
            else:
                self.xVelocity=data['xV']#sets the velocity
                self.yVelocity=data['yV']

            t2=threading.Thread(target=self.xMotor)#runs the motors
            t3=threading.Thread(target=self.yMotor)

            t2.start()
            t3.start()
            t2.join()
            t3.join()

            self.xDisplacement+=self.xVelocity*self.timeUnit#updates the displacement
            self.yDisplacement+=self.yVelocity*self.timeUnit
            
            self.ImPipe.send({'xV':self.xVelocity,'yV':self.yVelocity,'xD':self.xDisplacement,'yD':self.yDisplacement})

            xVQueue.put(self.xVelocity)#puts the values on the respective queues for getters etc.
            yVQueue.put(self.yVelocity)
            xDQueue.put(self.xDisplacement)
            yDQueue.put(self.yDisplacement)

            if not self.controlQueue.empty():
                warnings.warn('MotorControl is Exiting')
                break

    def xMotor(self):
        """The method to control the motor that moves on the x axis
        Args:
            controlQueue: Used for shutting down the program
        """
        if self.xVelocity !=0:
            self.M1.runVelocityT(self.xVelocity,self.timeUnit)


    def yMotor(self):
        """The method to control the motor that moves on the y axis
        Args:
            controlQueue: Used for shutting down the program
        """
        if self.yVelocity !=0:
            self.M2.runVelocityT(self.yVelocity,self.timeUnit)


    def getXDisplacement(self):
        if self.tracking:
            if not self.xDQueue.empty():
                
                while self.xDQueue.qsize()>=1:

                    x=self.xDQueue.get()
                    #print(x)
                return x
            else:
                print('no displacement found')
                return 0
        else:
            print('not tracking')
            return 0

    def getYDisplacement(self):
        if self.tracking:
            if not self.yDQueue.empty():
                
                while self.yDQueue.qsize()>=1:
                    #print("Getting velocity")
                    y=self.yDQueue.get()
                return y
            else:
                #print("no velocity found")
                return 0
        else:
            return 0

    def getXVelocity(self):
        #return self.xVelocity
        #print('queue size 2: ', self.xVQueue.qsize())
        if not self.xVQueue.empty():
            
            while self.xVQueue.qsize()>=1:
                #print("Getting velocity")
                x=self.xVQueue.get()
            return x
        else:
            #print("no velocity found")
            return 0

    def getYVelocity(self):
        #return self.yVelocity
        if not self.yVQueue.empty():
            
            while self.yVQueue.qsize()>=1:
                #print("Getting velocity")
                y=self.yVQueue.get()
            return y
        else:
            return 0

    def main(self,q,controlQueue,ImPipe):
        """The main method that starts the threads to allow the motors to run
        Args:
            q:The queue for transmitting velocity data
            controlQueue: Used for shutting down the program
        """

        self.dataQueue=q
        self.controlQueue=controlQueue
        
        self.ImPipe=ImPipe

        xVQueue=multiprocessing.Queue()
        yVQueue=multiprocessing.Queue()

        xDQueue=multiprocessing.Queue()
        yDQueue=multiprocessing.Queue()
        
        self.trackingThread=multiprocessing.Process(target=self.updater,args=(xVQueue,yVQueue,xDQueue,yDQueue,))
        self.trackingThread.start()

        self.xVQueue=xVQueue
        self.yVQueue=yVQueue

        self.xDQueue=xDQueue
        self.yDQueue=yDQueue

        self.tracking=True

        while True:
            if not self.trackingThread.is_alive():
                self.trackingThread.kill()
                break
                





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
            self.M1.runDisplacement(distance)
        elif axis == "y":
            self.M2.runDisplacement(distance)

    def xMotorTest(self,distance):#,returnQueue):
        #t1=time.time()
        self.M1.runDisplacement(distance)
        #t2=time.time()
        #returnQueue.put(t2-t1)
    
    def yMotorTest(self,distance):#,returnQueue):
        #t1=time.time()
        self.M2.runDisplacement(distance)
        #t2=time.time()
        #returnQueue.put(t2-t1)

    def updaterTest(self,distance,returnQueue1):
        print('x')
        tA=time.time()
        #x=self.dataQueue.get()
        #if self.dataQueue.empty():

        #self.xVelocity=x[0]
        #self.yVelocity=x[1]
        t2=threading.Thread(target=self.xMotorTest,args=(distance,))
        t3=threading.Thread(target=self.yMotorTest,args=(distance,))
        
        t2.start()
        t3.start()
        t2.join()
        t3.join()

        tB=time.time()
        #print('x')
        returnQueue1.put(tB-tA)

                

                
    
    def measureMotorSpecsOne(self,distance):
        """for measuring the motor speed with 2 default motors"""
        #self.dataQueue=queue.Queue()
        #controlQueue=queue.Queue()
        returnQueue1=queue.Queue()
        #returnQueue2=queue.Queue()
        
        t1=threading.Thread(target=self.updaterTest,args=(distance,returnQueue1,))
        #t2=threading.Thread(target=self.xMotorTest,args=(distance,returnQueue1,))
        #t3=threading.Thread(target=self.yMotorTest,args=(distance,returnQueue2,))
        t1.start()
        t1.join()
        #t2.start()
        #t3.start()
        while returnQueue1.empty():# and returnQueue2.empty():
            pass


        speed1=distance/returnQueue1.get()
        #speed2=distance/returnQueue2.get()
        return speed1#,speed2
        

    def setWaitTime(self, waitTime):
        self.M1.setMinWaitTime(waitTime)
        self.M2.setMinWaitTime(waitTime)

    def setMaxSpeed(self,maxSpeed):
        self.M1.setMaxSpeed(maxSpeed)
        self.M2.setMaxSpeed(maxSpeed)

    def getMaxSpeed(self):
        return self.M1.getMaxSpeed(),self.M2.getMaxSpeed()

    def xRunVelocityT(self,velocity,time):
        self.M1.runVelocityT(velocity,time)

    def yRunVelocityT(self,velocity,time):
        self.M2.runVelocityT(velocity,time)
