from motorisedcameratracking import *
from GUI import *
import threading
import queue
import time
x=MotorisedCameraTracking()
q=queue.Queue()
G=GUI(q)
target='person'
print(target)
#x.calibrateInteractive()
t=threading.Thread(target=G.main,args=())
t.start()
x.track('person')
#t=threading.Thread(target=x.track,args=('person',))
#t.start()

#print('tracking...........')
#time.sleep(20)
#a,b,c=x.getFrame()
#print(a)
#print(b)
#print(c)