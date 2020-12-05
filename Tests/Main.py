"""This is an example application built around the library.

While the GUI needs work the quzlity is acceptable and is useful for testing the library as new features are added.
"""

from motorisedcameratracking import *
from GUI import *
import sys
import time
import multiprocessing
import queue
import threading
x=MotorisedCameraTracking()




q=queue.Queue()
G=GUI(q)
t1=threading.Thread(target=G.initialise,args=())
t1.start()
while q.empty():
    #print('x')
    pass
target=q.get()
print(target)
t1=threading.Thread(target=x.track,args=(target,))
t2=threading.Thread(target=G.main,args=())
t2.start()
#run in threads
t1.start()




