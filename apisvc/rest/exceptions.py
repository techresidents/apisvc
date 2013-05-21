class RestException(Exception):
    def __init__(self, message, code=500,
            user_message=None, developer_message=None):
        self.message = message
        self.code = code
        self.user_message = user_message
        self.developer_message = developer_message

    def __repr__(self):
        return "%s(message=%r, code=%r)" % \
                (self.__class__.__name__, self.message, self.code)
    
    def __str__(self):
        return self.message
    
class AuthenticationError(RestException):
    def __init__(self, message, code=401, 
            user_message=None, developer_message=None):
        if user_message is None:
            user_message = "Authentication is required for this action."
        super(AuthenticationError, self).__init__(
                message, code, user_message, developer_message)

class AuthorizationError(RestException):
    def __init__(self, message, code=403, 
            user_message=None, developer_message=None):
        if user_message is None:
            user_message = "You are not authorized for this action."
        super(AuthorizationError, self).__init__(
                message, code, user_message, developer_message)

class InvalidQuery(RestException):
    def __init__(self, message, code=400, 
            user_message=None, developer_message=None):
        if user_message is None:
            user_message = "Invalid request."
        super(InvalidQuery, self).__init__(
                message, code, user_message, developer_message)

class ResourceNotFound(RestException):
    def __init__(self, message=None, code=404, 
            user_message=None, developer_message=None):
        default_message = "Resource cannot be found."
        if message is None:
            message = default_message
        if user_message is None:
            user_message = default_message
        super(ResourceNotFound, self).__init__(
                message, code, user_message, developer_message)

class ValidationError(RestException):
    def __init__(self, message, code=400, 
            user_message=None, developer_message=None):
        if user_message is None:
            user_message = "Invalid request."
        super(ValidationError, self).__init__(
                message, code, user_message, developer_message)
