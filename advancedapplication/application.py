import tkinter 
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox
from motorisedcameratracking import *
import sys
import time
import multiprocessing
import queue
import threading
import cv2
from PIL import Image, ImageTk

    
def startTrackingA():
    target=targetEntry.get()#gets the target
    x.track(target)
    upAdjust.pack_forget()#removes the existing buttons from the GUI
    downAdjust.pack_forget()
    leftAdjust.pack_forget()
    rightAdjust.pack_forget()
    targetEntry.pack_forget()
    startTracking.pack_forget()
    stopTracking.pack()#assigns the stop tracking button to the GUI
    global imageDisplayThread
    imageDisplayThread=threading.Thread(target=imageDisplay)#starts displaying an image
    imageDisplayThread.start()
    
def exit():
    if x.isRunning():
        x.terminate()#terminates the tracking
        window.destroy()#destroys the window
        sys.exit()#closes the program
    else:
        window.destroy()
        sys.exit()
    
def imageDisplay():
    
    imageDisplay=tkinter.Label(window,text='no image to display')
    imageDisplay.pack()
    lastImage=None
    while True:
        time.sleep(2)#waits 2 seconds between checking for images
        if x.isImageAvailable():
            image,box,label,confidence=x.getFrame()
            a = image == lastImage
            if not a.all():#checks if the image is different
                lastImage=image
                image = draw_bbox(image, box, label, confidence)#adds the data to the image
                image=cv2.resize(image,(1000,500),interpolation = cv2.INTER_AREA)#resizes the image
                b,g,r = cv2.split(image)#convers the image to a form suitable for tkinter
                img = cv2.merge((r,g,b))
                img = Image.fromarray(img)
                img = ImageTk.PhotoImage(image=img)
                imageDisplay.config(image=img)#updates the image

motorisedCameraTracking=MotorisedCameraTracking(camera={'name': 'RPICam','orientation': 180,'Width':3000,'Height':2000},config={'imagingMode':'simple'})#creates the camera tracking object
x=motorisedCameraTracking
#x.setWarnings(False)
x.setGUIFeatures(True)#sets GUI features to true
window=tkinter.Tk()#creates the window
window.title('motorisedcameratracking')
window.protocol("WM_DELETE_WINDOW", exit)#assigns the exit button to the exit method

upAdjust=tkinter.Button(window,text='Motor Up',command=lambda: x.aim(5,"y"))#adds the buttons to the GUI
downAdjust=tkinter.Button(window,text='Motor Down',command=lambda: x.aim(-5,"y"))
leftAdjust=tkinter.Button(window,text='Motor Left',command=lambda: x.aim(-5,"x"))
rightAdjust=tkinter.Button(window,text='Motor Right',command=lambda: x.aim(5,"x"))
targetEntry=tkinter.Entry(window)
startTracking=tkinter.Button(window,text='get target',command=lambda: startTrackingA())
stopTracking=tkinter.Button(window,text='stop tracking',command=lambda: x.terminate())

upAdjust.pack()#assigns the buttons to the GUI
downAdjust.pack()
leftAdjust.pack()
rightAdjust.pack()
targetEntry.pack()
startTracking.pack()

window.mainloop()






    









