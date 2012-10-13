from rest.middleware.base import RestMiddleware

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
        body = request.body()
        if body:
            content_type = request.header("content-type") or DEFAULT_CONTENT_TYPE
            format = CONTENT_TYPE_FORMAT.get(content_type, DEFAULT_FORMAT)
            result = [] if context.bulk else context.resource_class()
            try:
                serializer = context.resource_class.serializer
                context.data = serializer.deserialize(
                        api=self.api,
                        data=body,
                        format=format,
                        result=result)
            except:                
                result = context.resource_class()
                context.data = serializer.deserialize(
                        api=self.api,
                        data=body,
                        format=format,
                        result=result)
                context.bulk = False
        else:
            context.data = None
        
    def process_response(self, context, response, **kwargs):
        if not response.successful:
            return response

        if not isinstance(response.data, basestring):
            content_type = context.request.header("content-type") \
                    or DEFAULT_CONTENT_TYPE

            format = CONTENT_TYPE_FORMAT.get(content_type, DEFAULT_FORMAT)
            response.headers["cache-control"] = "no-cache"
            response.headers["content-type"] = "%s; charset=UTF-8" \
                    % FORMAT_CONTENT_TYPE[format]

            serializer = context.resource_class.serializer
            response.data = serializer.serialize(
                    api=self.api,
                    resource=response.data,
                    format=format)
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return None
