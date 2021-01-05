class Error(Exception):
    pass

class GUIFeaturesNotEnabledError(Error):
    """Used when the user tries to call a function which requires "GUI Features" but it is not enabled"""
    pass

class NoImageAvailableError(Error):
    """used when the user tries to retrieve an image but none is available"""
    pass

class NotTrackingError(Error):
    """used when the user tries to use a feature that requires tracking to have been started"""
    pass

class TrackingActiveError(Error):
    """used when the user tries to use a feature that can't be run at the same time as tracking"""
    pass

class FeatureNotImplementedError(Error):
    """used when the user attempts to use a feature that has not been implemented fully"""

    def __init__(self,message: str = 'This feature has not been implemented although it seems a function of this name is in the code. Possible solutions include updating to a newer version or implementing the feature and submitting it on github'):
        super.__init__(message)

