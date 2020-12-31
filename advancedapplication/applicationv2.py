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

def calibrate():
    calibrate=tkinter.Tk()
    calibrate.title('calibration')
    x.calibrateZero()
    


    
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

        
def help():
    webbrowser.open('https://github.com/wDove1/motorisedcameratracking')

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

menuBar.add_cascade(label='Tracking',menu=trackingMenu)
menuBar.add_cascade(label='Help',menu=helpMenu)
window.config(menu=menuBar)

upAdjust=tkinter.Button(window,text='Motor Up',command=lambda: x.aim(5,"y"))
downAdjust=tkinter.Button(window,text='Motor Down',command=lambda: x.aim(-5,"y"))
leftAdjust=tkinter.Button(window,text='Motor Left',command=lambda: x.aim(-5,"x"))
rightAdjust=tkinter.Button(window,text='Motor Right',command=lambda: x.aim(5,"x"))


upAdjust.grid(row = 0, column = 0, pady = 2)
downAdjust.grid(row = 1, column = 0, pady = 2)
leftAdjust.grid(row = 2, column = 0, pady = 2)
rightAdjust.grid(row = 3, column = 0, pady = 2)

imageDisplay=tkinter.Label(window,text='no image to display')
imageDisplay.grid()#work this out


window.mainloop()

