class Response(object):
    def __init__(self, data=None, headers=None, code=200):
        self.data = data
        self.code = code
        self.headers = headers or {}
    
    @property
    def successful(self):
        if self.code is not None and \
            self.code >= 200 and self.code <= 299:
                return True
        else:
            return False

class ExceptionResponse(Response):
    def __init__(self, exception):
        super(ExceptionResponse, self).__init__(
                data=exception.user_message,
                code=exception.code)
        self.exception = exception
