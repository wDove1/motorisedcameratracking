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


def calibrate():
    if not x.isRunning():
        global saveData#creates the global variables
        global saveDataLoaded

        #with open("saveFile.json", "r") as saveFile:
        #    saveData = json.load(saveFile)
        #saveDataLoaded=True

        waitTime=0.0012#sets the wait time to be used in calibration
        speed1,speed2=x.calibrateZero(waitTime,360)#calibrates the motors

        saveData['motors']['xMotor']['minWaitTime']=waitTime#assignas the results of calibration to the dictionary
        saveData['motors']['yMotor']['minWaitTime']=waitTime
        saveData['motors']['xMotor']['maxSpeed']=speed1
        saveData['motors']['yMotor']['maxSpeed']=speed2
        x.setSpecsZero(waitTime=saveData['motors']['xMotor']['minWaitTime'],speed1=saveData['motors']['xMotor']['maxSpeed'],speed2=None)#sets the specs for the motors to run on
    else:
        tkinter.messagebox.showinfo("warning","this can not be run while the tracking is active")#warns the user they are already tracking


def importCalibration():
    global saveData#tells it to reference the global variables
    global saveDataLoaded
    with open("saveFile.json", "r") as saveFile:#opens the json file
        saveData = json.load(saveFile)#loads the data
    saveDataLoaded=True#sets data loaded to true
    x.setSpecsZero(waitTime=saveData['motors']['xMotor']['minWaitTime'],speed1=saveData['motors']['xMotor']['maxSpeed'],speed2=saveData['motors']['xMotor']['maxSpeed'])#sets the specs for the motors to run on




def saveCalibration():
    if saveDataLoaded:
        print(saveData)
        with open("saveFile.json", "w") as saveFile:#opens the file
            json.dump(saveData, saveFile)#saves the data
    else:
        tkinter.messagebox.showinfo("warning","There is no calibration data to save")#does not save if there is no data to save

def setCalibration():
    pass
        
def disableAimButtons():
    """disables the buttons when the tracking is active to prevent an error being raised"""
    upAdjust.config(state=DISABLED)
    downAdjust.config(state=DISABLED)
    leftAdjust.config(state=DISABLED)
    rightAdjust.config(state=DISABLED)

def activateAimButtons():
    """renables buttons when tracking is stopped"""
    upAdjust.config(state=NORMAL)
    downAdjust.config(state=NORMAL)
    leftAdjust.config(state=NORMAL)
    rightAdjust.config(state=NORMAL)

    
def exit():
    """the method which is run when the exit button is pressed"""
    if x.isRunning():#checks if the tracking is active
        x.terminate()#stops the tracking

    window.destroy()#destroys the window
    sys.exit()#ends the program
    
def imageDisplayA():
    while True:#loops as is run in a thread
        time.sleep(2)#checks if an image is available every 2 seconds
        if x.isImageAvailable():
            image=x.getFrameAsImage([1000,500])#gets the image with the boxes pre drawn etc

            #b,g,r = cv2.split(image)#coverts the image to the format required by tkinter
            #img = cv2.merge((r,g,b))
            #img = Image.fromarray(img)
            #img = ImageTk.PhotoImage(image=img)
            img=convertImageTkinter(image)
            imageDisplay.config(image=img)#configures the label to show the image

def startTracking():
    if not x.isRunning():#checks the tracking is not already active
        popUp=tkinter.Tk()#creates a new window to start the tracking
        popUp.title('start Tracking')
        popUp.geometry("200x200")
        targets=x.getSupportedTargets()

        default = tkinter.StringVar(popUp)
        default.set(targets[0])#default value
        

        targetSelector = OptionMenu(popUp, default, *targets)#creates a drop down menu to let the user select the target
        targetSelector.pack()

        def track():
            disableAimButtons()#disables the aimimg buttons
            x.track(default.get())#starts tracking
            imageDisplayThread=threading.Thread(target=imageDisplayA)#starts the thread to display the images
            imageDisplayThread.start()

            popUp.destroy()#destroys the window
            

        button = tkinter.Button(popUp, text="startTracking", command=track)#adds the button to start tracking
        button.pack()

        
        popUp.mainloop()
    else:
        tkinter.messagebox.showinfo("warning","tracking is already active")#warns the user they are already tracking
    
def startTrackingLimited():
    if not x.isRunning():
        popUp=tkinter.Tk()#creates a window to start tracking
        popUp.title('start Tracking')
        popUp.geometry("300x200")
        targets=x.getSupportedTargets()


        

        default = tkinter.StringVar(popUp)
        default.set(targets[0]) # default value
        

        targetSelector = OptionMenu(popUp, default, *targets)#creates drop down menu
        targetSelector.grid(row=1,column=2)
        #creates labels and input boxes
        a=Label(popUp,text='first x limit')
        b=Label(popUp,text='second x limit')
        c=Label(popUp,text='first y limit')
        d=Label(popUp,text='second y limit')
        a.grid(row=2,column=1)#uses grid to align the items
        b.grid(row=3,column=1)
        c.grid(row=4,column=1)
        d.grid(row=5,column=1)
        
        xl1=tkinter.Entry(popUp)
        xl2=tkinter.Entry(popUp)
        yl1=tkinter.Entry(popUp)
        yl2=tkinter.Entry(popUp)
        xl1.grid(row=2,column=2)
        xl2.grid(row=3,column=2)
        yl1.grid(row=4,column=2)
        yl2.grid(row=5,column=2)

        warningLabel=tkinter.Label(popUp)
        warningLabel.grid(row=6,column=2)

        def track():
            xLimit1=float(xl1.get())#gets the str from the boxes and converts it to a float
            xLimit2=float(xl2.get())
            yLimit1=float(yl1.get())
            yLimit2=float(yl2.get())
            if xLimit1<0 and xLimit2>0 and yLimit1<0 and yLimit2>0:#if limits are in correct format it starts tracking
                startTracking(xLimit1,xLimit2,yLimit1,yLimit2)
            else:
                warningLabel.config(text='please enter correct limits')#warns the user incorrect limits have been used.


        def startTracking(xLimit1,xLimit2,yLimit1,yLimit2):#starts tracking with the correct limits
            disableAimButtons()
            x.trackLimited(default.get(),xLimit1,xLimit2,yLimit1,yLimit2)
            imageDisplayThread=threading.Thread(target=imageDisplayA)#stsrts the thread to display the image
            imageDisplayThread.start()
            popUp.destroy()#destroys the window 

            

        button = tkinter.Button(popUp, text="startTracking", command=track)
        button.grid(row=7,column=2)

    else:
        tkinter.messagebox.showinfo("warning","tracking is already active")#warns the user they are already tracking

def stopTracking():
    if x.isRunning():#checks if the motor is running
        x.terminate()#ends the tracking
        activateAimButtons()#reactivates the aiming buttons
    else:
        tkinter.messagebox.showinfo("warning","nothing to stop")#warns the user there is nothing to stop
        
def startUp():
    importCalibration()#imports the calibration details

        
def help():
    webbrowser.open('https://github.com/wDove1/motorisedcameratracking')#opens the github repository

def showVersionDetails():
    pass

saveData=None
saveDataLoaded=False
x=MotorisedCameraTracking(camera={'name': 'RPICam','orientation': 180,'Width':3000,'Height':2000},config={'imagingMode':'intermediate'})#creates an object for the motor tracking

#x.setWarnings(False)
x.setGUIFeatures(True)

startUp()#calls the starup function

window=tkinter.Tk()#creates the main window
window.title('motorisedcameratracking')#titles the window 
window.protocol("WM_DELETE_WINDOW", exit)#assigns the exit button to the exit function which also terminates the processes
window.geometry("1920x1080")#sets the size of the window

menuBar=Menu(window)#creates the menu

#assigns drop down menus and buttons to the menu
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
#calibrationMenu.add_command(label='setCalibration',command=setCalibration)

menuBar.add_cascade(label='Tracking',menu=trackingMenu)#adds drop down menus to the main menu
menuBar.add_cascade(label='Help',menu=helpMenu)
menuBar.add_cascade(label='Calibration',menu=calibrationMenu)
window.config(menu=menuBar)

upAdjust=tkinter.Button(window,text='Motor Up',command=lambda: x.aim(5,"y"))#creates the aiming buttons
downAdjust=tkinter.Button(window,text='Motor Down',command=lambda: x.aim(-5,"y"))
leftAdjust=tkinter.Button(window,text='Motor Left',command=lambda: x.aim(-5,"x"))
rightAdjust=tkinter.Button(window,text='Motor Right',command=lambda: x.aim(5,"x"))


upAdjust.grid(row = 0, column = 0, pady = 5)#assigns the buttons to the window
downAdjust.grid(row = 1, column = 0, pady = 5)
leftAdjust.grid(row = 2, column = 0, pady = 5)
rightAdjust.grid(row = 3, column = 0, pady = 5)

imageDisplay=tkinter.Label(window,text='no image to display')#creates the label for displaying the iamge
imageDisplay.grid(row=4,column=8,pady=100,padx=100)


window.mainloop()#starts the window

