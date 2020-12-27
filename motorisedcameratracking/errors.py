class Error(Exception):
    pass

class GUIFeaturesNotEnabled(Error):
    """Used when the user tries to call a function which requires "GUI Features" but it is not enabled"""
    pass

class NoImageAvailable(Error):
    """used when the user tries to retrieve an image but none is available"""
    pass

class NotTracking(Error):
    """used when the user tries to use a feature that requires tracking to have been started"""
    pass
