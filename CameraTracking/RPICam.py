from picamera import PiCamera
from time import *
from cv2 import *
import numpy as np
import os
from PIL import Image
class RPICam:


        modelDetails={'name':'rPi_NoIRv2','width':3280,'height':2464}
        imagePath=None
        orientation=None
        def __init__(self,imagePath,orientation):
                self.imagePath=imagePath
                self.orientation=orientation

        def getImage(self):
                camera=PiCamera()
                camera.resolution=(1280,720)
                camera.capture(self.imagePath)
                camera.close()


        def postProcessing(self):
                img=cv2.imread(self.imagePath,1)#convert image to array of 0-255
                os.remove(self.imagePath)

                return img

        def orientationCorrection(self):
                img = Image.open(self.imagePath)
                img = img.rotate(-self.orientation)
                img = img.save(self.imagePath)

        def capture(self):
                self.getImage()
                self.orientationCorrection()
                return self.postProcessing()
                

        def getData(self):
                return self.modelDetails[self.model]

        def getModel(self):
                return self.model

        def getImagePath(self):
                return self.imagePath

        def getModelDetails(self):
                return self.modelDetails

