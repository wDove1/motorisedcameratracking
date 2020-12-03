import tkinter
#import threadng
from motorisedcameratracking import *
from MotorControl import *

class GUI:
    x=MotorisedCameraTracking()
    #MC=MotorControl()
    q=None
    def __init__(self,q): 
        self.q=q

    def initialise(self):
        window=tkinter.Tk()
        window.title('Target selection')
        upAdjust=tkinter.Button(window,text='Motor Up',command=lambda:self.MC.yAdjustU())
        upAdjust.pack()
        downAdjust=tkinter.Button(window,text='Motor Down',command=lambda:self.MC.yAdjustD())
        downAdjust.pack()
        leftAdjust=tkinter.Button(window,text='Motor Left',command=lambda:self.MC.xAdjustL())
        leftAdjust.pack()
        rightAdjust=tkinter.Button(window,text='Motor Right',command=lambda:self.MC.xAdjustR())
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
        

#GUI=GUI()
#GUI.initialise()
