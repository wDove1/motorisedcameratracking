import pkg_resources
class Config():
    """Hello"""
    timeUnit=None
    


    #xMotor=""
    #yMotor=""
    #Cameras=[RPICam]#store the list of classes to allow the user to create their own
    #Motors=[]



    def __init__(self,timeUnit):
        """The __init__ method"""
        self.timeUnit=timeUnit

    def getFaceClassifiersPath(self):
        print(pkg_resources.resource_filename('motorisedcameratracking','data/haarcascade_frontalface_default.xml'))
        return pkg_resources.resource_filename('motorisedcameratracking','data/haarcascade_frontalface_default.xml')

        




