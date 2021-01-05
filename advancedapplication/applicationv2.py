import tkinter
from tkinter import *
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox
from motorisedcameratracking import *
import threading
import sys
import time
import cv2
from PIL import Image, ImageTk
import webbrowser
import json

class Calibrate:
    speed1=None
    speed2=None
    waitTime=None

    distance=None
    increment=None


    def calibrate(self,x):
        self.waitTime=0.002
        self.distance=360
        self.increment=0.0001


        with open("saveFile.json", "r") as saveFile:
            saveData = json.load(saveFile)



        calibratePopUp=tkinter.Tk()
        calibratePopUp.title('calibration')
        calibrateButton=Button(calibratePopUp,text='run calibration',command=lambda:self.runCalibration())
        calibrateButton.pack()
        stopButton=Button(calibratePopUp,text='stop',command=lambda:self.end(calibratePopUp))
        stopButton.pack()
        calibratePopUp.mainloop()
        
    def end(self,window):
        return self.speed1,self.speed2,self.waitTime
        window.destroy()
                          
    def runCalibration(self):
        print(self.waitTime)
        self.waitTime-=self.increment
        self.speed1,self.speed2=x.calibrateZero(self.waitTime,self.distance)



def calibrate():
    with open("saveFile.json", "r") as saveFile:
        saveData = json.load(saveFile)
    print(saveData)
    a=Calibrate()
    speed1,speed2,waitTime=a.calibrate(x)
    print(speed1)
    saveData['motors']['xMotor']['minWaitTime']=waitTime
    saveData['motors']['yMotor']['minWaitTime']=waitTime
    saveData['motors']['xMotor']['maxSpeed']=speed1
    saveData['motors']['yMotor']['maxSpeed']=speed2
    print(saveData)

def importCalibration():
    with open("saveFile.json", "r") as saveFile:
        saveData = json.load(saveFile)
    x.setSpecsZero(waitTime=saveData['motors']['xMotor']['minWaitTime'],speed1=saveData['motors']['xMotor']['maxSpeed'],speed2=None)
    #print(data)
    #print(data['motors']['xMotor'])


def saveCalibration():
    print(saveData)
    #with open("saveFile.json", "w") as saveFile:
    #    json.dump(saveData, saveFile)
        
def disableAimButtons():#disables the buttons when the tracking is active to prevent an error being raised
    upAdjust.config(state=DISABLED)
    downAdjust.config(state=DISABLED)
    leftAdjust.config(state=DISABLED)
    rightAdjust.config(state=DISABLED)

def activateAimButtons():#renables buttons when tracking is stopped
    upAdjust.config(state=NORMAL)
    downAdjust.config(state=NORMAL)
    leftAdjust.config(state=NORMAL)
    rightAdjust.config(state=NORMAL)

    
def exit():
    if x.isRunning():
        x.terminate()
        window.destroy()
        sys.exit()
    else:
        window.destroy()
        sys.exit()
    
def imageDisplayA():
    

    #time.sleep(30)
    lastImage=None
    
    while True:
        #print('hello')
        time.sleep(2)
        
        #try:
            
        
        #a=x.getAllFrames()
        #print(a)
            
            
        #
        if x.isImageAvailable():
            image,box,label,confidence=x.getFrame()
            a = image == lastImage
            if not a.all():
                lastImage=image
            
                image = draw_bbox(image, box, label, confidence)
                print(box)
                image=cv2.resize(image,(1000,500),interpolation = cv2.INTER_AREA)
                b,g,r = cv2.split(image)
                img = cv2.merge((r,g,b))
                img = Image.fromarray(img)
                img = ImageTk.PhotoImage(image=img)
                imageDisplay.config(image=img)
        #except:
        #    print('no image found')
            

def startTracking():
    popUp=tkinter.Tk()
    popUp.title('start Tracking')
    popUp.geometry("200x200")
    targets=x.getSupportedTargets()


    

    default = tkinter.StringVar(popUp)
    default.set(targets[0]) # default value
    

    w = OptionMenu(popUp, default, *targets)
    w.pack()

    def track():
        x.track(default.get())
        imageDisplayThread=threading.Thread(target=imageDisplayA)
        imageDisplayThread.start()
        disableAimButtons()
        popUp.destroy()
        

    button = tkinter.Button(popUp, text="startTracking", command=track)
    button.pack()

    
    popUp.mainloop()
    
def startTrackingLimited():
    popUp=tkinter.Tk()
    popUp.title('start Tracking')
    popUp.geometry("200x200")
    targets=x.getSupportedTargets()


    

    default = tkinter.StringVar(popUp)
    default.set(targets[0]) # default value
    

    targetSelector = OptionMenu(popUp, default, *targets)
    targetSelector.pack()
    
    l1=tkinter.Entry(popUp)
    l2=tkinter.Entry(popUp)
    l1.pack()
    l2.pack()

    def track():
        x.trackLimited(default.get(),l1.get(),l2.get())
        imageDisplayThread=threading.Thread(target=imageDisplayA)
        imageDisplayThread.start()
        popUp.destroy()

        

    button = tkinter.Button(popUp, text="startTracking", command=track)
    button.pack()

def stopTracking():
    if x.isRunning():
        x.terminate()
        activateAimButtons()

        
def help():
    webbrowser.open('https://github.com/wDove1/motorisedcameratracking')

saveData=None

motorisedCameraTracking=MotorisedCameraTracking(camera={'name': 'RPICam','orientation': 180,'Width':3000,'Height':2000},config={'imagingMode':'simple'})
x=motorisedCameraTracking
#x.setWarnings(False)
x.setGUIFeatures(True)

window=tkinter.Tk()
window.title('motorisedcameratracking')
window.protocol("WM_DELETE_WINDOW", exit)
window.geometry("1920x1080")

menuBar=Menu(window)

trackingMenu=Menu(menuBar,tearoff=0)
trackingMenu.add_command(label='startTracking',command=startTracking)
trackingMenu.add_command(label='startTrackingLimited',command=startTrackingLimited)
trackingMenu.add_command(label='stop',command=stopTracking)

helpMenu=Menu(menuBar,tearoff=0)
helpMenu.add_command(label='help',command=help)

calibrationMenu=Menu(menuBar,tearoff=0)
calibrationMenu.add_command(label='motorCalibration',command=calibrate)
calibrationMenu.add_command(label='saveCalibration',command=saveCalibration)
calibrationMenu.add_command(label='importCalibration',command=importCalibration)


menuBar.add_cascade(label='Tracking',menu=trackingMenu)
menuBar.add_cascade(label='Help',menu=helpMenu)
menuBar.add_cascade(label='Calibration',menu=calibrationMenu)
window.config(menu=menuBar)

upAdjust=tkinter.Button(window,text='Motor Up',command=lambda: x.aim(5,"y"))
downAdjust=tkinter.Button(window,text='Motor Down',command=lambda: x.aim(-5,"y"))
leftAdjust=tkinter.Button(window,text='Motor Left',command=lambda: x.aim(-5,"x"))
rightAdjust=tkinter.Button(window,text='Motor Right',command=lambda: x.aim(5,"x"))


upAdjust.grid(row = 0, column = 0, pady = 5)
downAdjust.grid(row = 1, column = 0, pady = 5)
leftAdjust.grid(row = 2, column = 0, pady = 5)
rightAdjust.grid(row = 3, column = 0, pady = 5)

imageDisplay=tkinter.Label(window,text='no image to display')
imageDisplay.grid(row=4,column=8,pady=100,padx=100)#work this out


window.mainloop()

