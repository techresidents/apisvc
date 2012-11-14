
class RestException(Exception):
    pass

class ValidationError(RestException):
    pass

class AuthorizationError(RestException):
    pass

class AuthenticationError(RestException):
    pass

class InvalidQuery(RestException):
    pass

class ResourceNotFound(RestException):
    pass
