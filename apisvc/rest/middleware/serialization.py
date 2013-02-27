import logging

from rest.exceptions import ValidationError
from rest.middleware.base import RestMiddleware
from rest.response import Response


DEFAULT_FORMAT = "JSON"
DEFAULT_CONTENT_TYPE = "application/json"

CONTENT_TYPE_FORMAT = {
    "application/json": "JSON",
}

FORMAT_CONTENT_TYPE = {
    "JSON": "application/json",
}

class SerializationMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        response = None
        body = request.body()
        if body:
            try:
                content_type = request.header("content-type") or DEFAULT_CONTENT_TYPE
                format = CONTENT_TYPE_FORMAT.get(content_type, DEFAULT_FORMAT)
                result = [] if context.bulk else context.resource_class()
                try:
                    serializer = context.resource_class.serializer
                    context.data = serializer.deserialize(
                            api=self.api,
                            resource_uri=context.path,
                            resource=result,
                            format=format,
                            data=body)
                except:                
                    result = context.resource_class()
                    context.data = serializer.deserialize(
                            api=self.api,
                            resource=result,
                            resource_uri=context.path,
                            format=format,
                            data=body)
                    context.bulk = False
            except ValidationError as error:
                logging.warning(str(error))
                response = Response(code=400, data="invalid data")
            except Exception as error:
                logging.exception(error)
                response = Response(code=400, data="invalid data")
        else:
            context.data = None
        return response
        
    def process_response(self, context, response, **kwargs):
        if not response.successful:
            return response
        
        if response.data is None:
            response.data = ""
            response.headers["cache-control"] = "no-cache"
            response.headers["content-type"] = "text/plain"

        elif response.data is not None and not isinstance(response.data, basestring):
            content_type = context.request.header("content-type") \
                    or DEFAULT_CONTENT_TYPE

            format = CONTENT_TYPE_FORMAT.get(content_type, DEFAULT_FORMAT)
            response.headers["cache-control"] = "no-cache"
            response.headers["content-type"] = "%s; charset=UTF-8" \
                    % FORMAT_CONTENT_TYPE[format]

            serializer = context.resource_class.serializer
            resource_uri = context.path if context.method == "GET" else None
            response.data = serializer.serialize(
                    api=self.api,
                    resource=response.data,
                    resource_uri=resource_uri,
                    format=format)

        return response

    def process_exception(self, context, request, exception, **kwargs):
        return None
