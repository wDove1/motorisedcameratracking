from picamera import PiCamera
from time import *
from cv2 import *
import numpy as np
import os
from PIL import Image
class RPICam:
        """A class for the raspberry pi camera
        Attributes:
            modelDetails: A dictionary containing details of the Camera
            imagePath: The path where the image will be stored and found
            orientation: The orientation of the image
        """

        modelDetails={'name':'rPi_NoIRv2','width':3280,'height':2464}
        imagePath: str = None
        orientation: float = None
        def __init__(self,imagePath: str,orientation: str):
                """sets the values of imagePath and orientation
                Args:
                   imagePath: the path to the image
                   orientation: the orientation of the camera
                """
                self.imagePath=imagePath
                self.orientation=orientation

        def getImage(self,resolution: list = [1280,720]):
                """Gets the image from the camera
                Args:
                    resolution:The resolution the camera will run at
                """
                camera=PiCamera()
                camera.resolution=(resolution[0],resolution[1])
                camera.capture(self.imagePath)
                camera.close()


        def postProcessing(self):
                """loads the image and converts it to a numPy array
                Returns:
                    img: A numPy array containing the image                
                """
                img=cv2.imread(self.imagePath,1)#convert image to a colour array
                os.remove(self.imagePath)

                return img

        def orientationCorrection(self):
                """Corrects the orientation of the image

                Runs on the image before it is opened so may need replacing
                """
                img = Image.open(self.imagePath)#opens the image
                img = img.rotate(-self.orientation)#rotates the image
                img = img.save(self.imagePath)#saves the image to the same location

        def capture(self,resolution: list =[1280,720]):
                """The outward facing method to capture an image

                returns:
                    numPy array: contains the image
                """
                self.getImage(resolution)#gets the image
                self.orientationCorrection()#corrects the orientation
                return self.postProcessing()#returns the image as a numPy array
                

        def getData(self):
                return self.modelDetails[self.model]

        def getModel(self):
                return self.model

        def getImagePath(self):
                return self.imagePath

        def getModelDetails(self):
                return self.modelDetails

class GenericCamera:
        camera=cv2.VideoCapture(1)

        def __init__(self):
                pass


        def capture(self):
                x,frame = camera.read()
                return frame

class VirtualCamera:
        images=[]
        #images.append(np.array())
        def __init__(self):
                pass

        def capture(self):
                return None
