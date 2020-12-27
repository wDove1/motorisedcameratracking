from motorisedcameratracking import *

import threading
import queue
import time
from GUI import *

x=MotorisedCameraTracking()
#q=queue.Queue()
#G=GUI(q)
target='person'
print(target)
#x.calibrateInteractive()
x.setGUIFeatures(True)

x.track('person')

#t=threading.Thread(target=G.main,args=())
#t=threading.Thread(target=x.track,args=('person',))
#t.start()
#t.start()
#print('tracking...........')
time.sleep(20)

a=x.getAllFrames()
print(a)
#print(b)
#print(c)
x.terminate()
