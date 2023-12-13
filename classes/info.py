class Response:
    value = ''
    time = -1.0
    lazy = False
    def_Success_Message = 'Success'
    def_Failure_Message = 'Failure'
    message = ""
    returnObject = None

class Success(Response):
    def __init__(self, val = True, time = -1.0, message = "", lazy = False, returnValue = 0.0, returnObject = None):
        self.value = val
        self.time = time
        self.returnValue = returnValue
        if ( message == "" ):
            self.message = self.def_Success_Message
        self.lazy = lazy
        self.returnObject = returnObject

class Failure(Response):
    def __init__(self, val = False, time = -1.0, message = "", lazy = False, returnValue = 0.0, returnObject = None):
        self.value = val
        self.returnValue = returnValue
        self.time = time
        if ( message == "" ):
            self.message = self.def_Success_Message
        self.lazy = lazy
        self.returnObject = returnObject
