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
def calibrate():
    calibrate=tkinter.Tk()
    calibrate.title('calibration')
    x.calibrateZero()
    
def startTrackingA():
    #print('hi')
    target=targetEntry.get()
    x.track(target)
    

    upAdjust.pack_forget()
    downAdjust.pack_forget()
    leftAdjust.pack_forget()
    rightAdjust.pack_forget()
    targetEntry.pack_forget()
    startTracking.pack_forget()
    
    stopTracking.pack()
    global imageDisplayThread
    imageDisplayThread=threading.Thread(target=imageDisplay)
    imageDisplayThread.start()
    
def exit():
    if x.isRunning():
        x.terminate()
        window.destroy()
        sys.exit()
    else:
        window.destroy()
        sys.exit()
    
def imageDisplay():
    
    imageDisplay=tkinter.Label(window,text='no image to display')
    imageDisplay.pack()
    #time.sleep(30)
    lastImage=None
    
    while True:
        #print('hello')
        time.sleep(2)
        
        #try:
            
        
        #a=x.getAllFrames()
        #print(a)
            
            
        #
        if x.isImageAvalible():
            image,box,label,confidence=x.getFrame()
            a = image == lastImage
            if not a.all():
                lastImage=image
            
                image = draw_bbox(image, box, label, confidence)
                image=cv2.resize(image,(1000,500),interpolation = cv2.INTER_AREA)
                b,g,r = cv2.split(image)
                img = cv2.merge((r,g,b))
                img = Image.fromarray(img)
                img = ImageTk.PhotoImage(image=img)
                imageDisplay.config(image=img)
        #except:
        #    print('no image found')
            

        
        


motorisedCameraTracking=MotorisedCameraTracking()
x=motorisedCameraTracking
x.setWarnings(False)
x.setGUIFeatures(True)
window=tkinter.Tk()
window.title('motorisedcameratracking')
window.protocol("WM_DELETE_WINDOW", exit)

upAdjust=tkinter.Button(window,text='Motor Up',command=lambda: x.aim(5,"y"))
downAdjust=tkinter.Button(window,text='Motor Down',command=lambda: x.aim(-5,"y"))
leftAdjust=tkinter.Button(window,text='Motor Left',command=lambda: x.aim(-5,"x"))
rightAdjust=tkinter.Button(window,text='Motor Right',command=lambda: x.aim(5,"x"))
targetEntry=tkinter.Entry(window)
startTracking=tkinter.Button(window,text='get target',command=lambda: startTrackingA())

stopTracking=tkinter.Button(window,text='stop tracking',command=lambda: x.terminate())
        



    


upAdjust.pack()
downAdjust.pack()
leftAdjust.pack()
rightAdjust.pack()
targetEntry.pack()
startTracking.pack()

window.mainloop()






    









