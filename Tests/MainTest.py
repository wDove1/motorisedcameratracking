from motorisedcameratracking import *
import cv2
import matplotlib.pyplot as plt
import cvlib as cv
from cvlib.object_detection import draw_bbox
import threading
import queue
import time
from GUI import *

x=MotorisedCameraTracking()
#q=queue.Queue()
#G=GUI(q)
target='person'
#print(target)
#x.calibrateInteractive()
x.setGUIFeatures(True)

x.track('person')

#t=threading.Thread(target=G.main,args=())
#t=threading.Thread(target=x.track,args=('person',))
#t.start()
#t.start()
#print('tracking...........')
time.sleep(40)
#try:
#label='person'
#im,bbox,label,conf=x.getFrame()
#output_image = draw_bbox(im, bbox, label, conf,write_conf=True)
#plt.imshow(output_image)
#plt.show()
    #print(a)
#print(b)
#print(c)
x.terminate()
#except:
#    x.terminate()
