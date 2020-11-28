import time
import sys
import RPi.GPIO as GPIO

from Config import *
class Motor1:
    motorDetails={'motorName':'28BJY-48','controllerName':'ULN2003','voltage':5,'baseAngle':0.087890625,'useAngle1':0.703125,'useAngle2':0.3515625}

    sequence = [[1,0,0,1],[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1]]
    maxSpeed=48#approximate experimental value
    maxWaitTime=0.0016
    stepPins=None

    def __init__(self,stepPins):
        # Use BCM GPIO references
        # instead of physical pin numbers
        GPIO.setmode(GPIO.BCM)
        # Define GPIO signals to use
        # Physical pins 11,15,16,18
        # GPIO17,GPIO22,GPIO23,GPIO24
        self.stepPins = stepPins
        # Set all pins as output
        for pin in self.stepPins:
            #print("Setup pins")
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin, False)

    def motor(self,steps,additionalWaitTime=0):#decide how to make this work
        stepCount = 8
        if steps<0:
            stepDir=-1
        else:
            stepDir=1

        x=round(steps)
        if x<=0:
            x=-x#must always be positive

        stepCounter = 0
        for i in range(0,x):
            for n in range(0,4):
                currentPin = self.stepPins[n]
                if self.sequence[stepCounter][n]==1:
                    GPIO.output(currentPin,True)
                else:#see if this is redundant
                    GPIO.output(currentPin,False)

            stepCounter += stepDir
          # If we reach the end of the sequence
          # start again
            if (stepCounter==stepCount):
                stepCounter = 0
                
            if (stepCounter<0):
                stepCounter = 7
          # Wait before moving on
            time.sleep(self.maxWaitTime+additionalWaitTime)

    def runDisplacement(self,degrees):
        steps=self.convertDegrees(degrees)
        print(steps)
        self.motor(steps)
        
    def runVelocityD(self,degreesPs,distance):
        if degreesPs==0 or distance==0:
            raise ValueError('No zero values aloud')
        if degreesPs>self.maxSpeed:
            raise ValueError('Velocity to high')
        minTime=distance/self.maxSpeed#calculates the minimum time the motor can finish the rotation
        neededTime=distance/degreesPs#calculates the required time to run
        additionalWaitTime=(neededTime-minTime)/self.convertDegrees(distance)#calculates the differece in times and splits it so it is added across wait times
        if additionalWaitTime<0:
            additionalWaitTime=-additionalWaitTime        
        self.motor(self.convertDegrees(distance),additionalWaitTime)#runs the motor

    def runVelocityT(self,degreesPs,time):#useful for time limited running in main program
        if degreesPs==0 or time==0:
            raise ValueError('No zero values aloud')
        if degreesPs>self.maxSpeed:
            raise ValueError('Velocity to high')
        distance=degreesPs*time#calculates the distance
        minTime=distance/self.maxSpeed#calculates the minimum time the motor can finish the rotation
        additionalWaitTime=(time-minTime)/self.convertDegrees(distance)#calculates the differece in times and splits it so it is added across wait times
        if additionalWaitTime<0:
            additionalWaitTime=-additionalWaitTime
        self.motor(self.convertDegrees(distance),additionalWaitTime)#runs the motor        

        

    def convertDegrees(self,degrees):
        '''convers degrees to steps for internal use within the function'''
        return degrees/self.motorDetails['baseAngle']

