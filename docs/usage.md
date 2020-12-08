# Usage
## installation
To install the project you need to be using python of at least 3.7 and it is installed through pip.


## usage
The code is imported with:
```python
from motorisedcameratracking import *
```
You can then create an object from the MotorisedCameraTracking API with:
```python
MCT=MotorisedCameraTracking()
```

When using the library it is important you call all constructors and methods with keywords as there is less chance of backwards compatability issues this way.

## example
```python
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
```
G.main() just serves to call the [terminate method from the API ](API-reference.md#motorisedcameratracking.MotorisedCameraTracking.MotorisedCameraTracking.terminate) when the button in it is pressed. 
