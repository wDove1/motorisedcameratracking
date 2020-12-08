from motorisedcameratracking import *
from GUI import *
import threading

x=MotorisedCameraTracking()
q=queue.Queue()
G=GUI(q)
target='person'
print(target)
t=threading.Thread(target=G.main,args=())
t.start()
x.track('person')

