class RestMiddleware(object):
    def __init__(self):
        self.api = None

    def process_request(self, context, request, **kwargs):
        return None

    def process_response(self, context, response, **kwargs):
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return None
