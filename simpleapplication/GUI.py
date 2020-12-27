import tkinter

from motorisedcameratracking import *

import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox

import sys
import time
import multiprocessing
import queue
import threading

class GUI:
    x=MotorisedCameraTracking()
    #MC=MotorControl()
    q=None
    def __init__(self,q): 
        self.q=q

    def initialise(self):
        window=tkinter.Tk()
        window.title('Target selection')
        upAdjust=tkinter.Button(window,text='Motor Up',command=lambda:self.x.aim(5,"y"))
        upAdjust.pack()
        downAdjust=tkinter.Button(window,text='Motor Down',command=lambda:self.x.aim(-5,"y"))
        downAdjust.pack()
        leftAdjust=tkinter.Button(window,text='Motor Left',command=lambda:self.x.aim(5,"x"))
        leftAdjust.pack()
        rightAdjust=tkinter.Button(window,text='Motor Right',command=lambda:self.x.x(-5,"x"))
        rightAdjust.pack()
        x=tkinter.Entry(window)
        x.pack()
        
        getData=tkinter.Button(window,text='get target',command=lambda:self.q.put(x.get()))
        getData.pack()
        window.mainloop()


    

        
    def main(self):
        window=tkinter.Tk()
        exit=tkinter.Button(window,text='Exit',command=lambda:self.x.terminate())
        exit.pack()
        
        window.mainloop()


    def change(self,target):
        self.q.put(target)
        self.main()
 
    def imageDisplay(self):
        window=tkinter.Tk()
        imageDisplay=tkinter.Label(window,text='no image to display')
        imageDisplay.pack()
        
        #while True:
            #print('hello')
            #time.sleep(10)
            #try:
        #print('hello')
        image,box,confidence=self.x.getFrame()
        print(confidence)
        #a=x.getAllFrames()
        #print(a)
        #print('hello')
        label='person'
        image = draw_bbox(image, box, label, confidence)
        image=cv2.resize(image,(1000,500),interpolation = cv2.INTER_AREA)
        b,g,r = cv2.split(image)
        img = cv2.merge((r,g,b))
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)
        imageDisplay.config(image=img)
        window.mainloop()
            #except:
            #    print('no image found')

#GUI=GUI()
#GUI.initialise()
