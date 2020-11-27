#modified for compatability with new motor1 class
import _thread
import threading
import time
from Motor1 import *
#from DataStore import *
from Config import *
class MotorControl:
    M1=Motor1([17,22,23,24])
    M2=Motor1([13,6,5,12])
    #DataStore=DataStore()
    #Config=Config()
    timeUnit=0.25
    xVelocity=0
    yVelocity=0
    xAcceleration=0
    yAcceleration=0

    xVtemp=0
    yVtemp=0
    q=None


        

    def setVelocity(self,x,y):
        print('setting velocity')
        print('velocity=',xVtemp)
        xVtemp=x
        yYtemp=y


    def incrementer(self):
        while True:
            t1=time.time()
            self.xVelocity+=self.xAcceleration
            self.yVelocity+=self.yAcceleration
            t2=time.time()
            t=t2-t1
            time.sleep(self.timeUnit-t)
            #print('a')

    def updater(self):#fix this
        print('c')
        while True:
            

            if not self.q.empty():
                x=self.q.get()
                print('x=',x)
                self.xVelocity=x[0]
                time.sleep(self.timeUnit)
            #else:
                #print('empty')

                

    def xMotor(self):
        while True:
            #print(self.xVelocity)
            if self.xVelocity !=0:
                self.M1.runVelocityT(self.xVelocity,self.timeUnit)

    def yMotor(self):
        print('e')
        while True:
            
            if self.yVelocity !=0:
                self.M2.runVelocityT(self.yVelocity,self.timeUnit)

    def main(self,q):
        print('y')
        self.q=q
        #_thread.start_new_thread(self.incrementer,())
        print('d')
        t1=threading.Thread(target=self.updater,args=())
        t2=threading.Thread(target=self.xMotor,args=())
        t3=threading.Thread(target=self.yMotor,args=())
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
