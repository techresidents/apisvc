from rest.error import Error
from rest.middleware.base import RestMiddleware
from rest.response import Response

class ErrorMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        return None
        
    def process_response(self, context, response, **kwargs):
        if not response.successful:
            if isinstance(response.data, basestring):
                message = response.data
            else:
                message = "internal error"
            response.data = Error(code=response.code, message=message)
        return response

    def process_exception(self, context, request, exception, **kwargs):
        response = Response(code=500, data=Error(code=500, message="internal error"))
        return response
