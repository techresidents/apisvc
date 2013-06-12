from rest.error import Error
from rest.exceptions import RestException
from rest.middleware.base import RestMiddleware
from rest.response import Response, ExceptionResponse

class ErrorMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        return None
        
    def process_response(self, context, response, **kwargs):
        if not response.successful:
            message = "An unexpected error occured. Please try again."
            developer_message = None
            if isinstance(response, ExceptionResponse):
                if response.exception.user_message:
                    message = response.exception.user_message
                developer_message = response.exception.developer_message
            elif isinstance(response.data, basestring):
                message = response.data
            response.data = Error(
                    code=response.code,
                    message=message,
                    developerMessage=developer_message)
        return response

    def process_exception(self, context, request, exception, **kwargs):
        code = 500
        message = "internal error"
        developer_message = None
        if isinstance(exception, RestException):
            code = exception.code
            if exception.user_message:
                message = exception.user_message
                developer_message = exception.developer_message

        error = Error(
                code=code,
                message=message,
                developerMessage=developer_message)

        response = Response(code=code , data=error)

        return response
