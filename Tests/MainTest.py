from motorisedcameratracking import *
from GUI import *
import threading
import queue

x=MotorisedCameraTracking()
q=queue.Queue()
G=GUI(q)
target='person'
print(target)
x.calibrateInteractive()
t=threading.Thread(target=G.main,args=())
t.start()
x.track('person')

