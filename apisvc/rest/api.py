import copy
import functools
import logging

class RequestContext(object):
    def __init__(self,
            api=None,
            session=None,
            user_id=None,
            resource_manager=None,
            resource_class=None,
            related_field=None,
            method=None,
            request=None,
            data=None,
            bulk=False,
            query=None):
        self.api = api
        self.session = session
        self.user_id = user_id
        self.resource_manager = resource_manager
        self.resource_class = resource_class
        self.related_field = related_field
        self.method = method
        self.request = request
        self.data = data
        self.bulk = bulk 
        self.query = query
    
    def is_direct_resource(self):
        return self.resource_class == self.resource_manager.resource_class

    def is_related_resource(self):
        if not self.is_direct_resource() and \
                self.related_field and \
                self.related_field.relation is self.resource_class:
            return True
        else:
            return False
    
    def is_nested_resource(self):
        if not self.is_direct_resource() and not self.is_related_resource():
            return True
        else:
            return False
    
class Api(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri
        if self.base_uri.endswith("/"):
            self.base_uri = self.base_uri[:-1]

        self.uris = []
        self.request_middlewares = []
        self.response_middlewares = []
        self.resource_classes = {}

    def add_resource(self, resource_class):
        self.resource_classes[resource_class.desc.resource_name] = resource_class
        manager = resource_class.desc.manager
        uris = manager.uris()
        for uri, context, callback in uris:
            context.resource_manager = context.resource_manager or manager

            if uri.startswith("^"):
                uri = uri[1:]
            if uri.endswith("$"):
                uri = uri[:-1]

            full_uri = "^%s%s$" % (self.base_uri, uri)
            process_callback = functools.partial(self.process, context=context, callback=callback)
            self.uris.append((full_uri, process_callback))
    
    def add_middleware(self, middleware):
        middleware.api = self
        self.request_middlewares.append(middleware)
        self.response_middlewares.insert(0, middleware)

    def get_resource_class(self, resource_name):
        return self.resource_classes[resource_name]
    
    def get_resource_uri(self, resource):
        if resource.primary_key_name():
            result = "%s/%s/%s" % (
                    self.base_uri,
                    resource.desc.resource_name,
                    resource.primary_key_value())
        else:
            result = "%s/%s" % (
                    self.base_uri,
                    resource.desc.resource_name)
        return result

    def get_uris(self):
        return self.uris

    def process(self, request, context, callback, **kwargs):
        context = copy.copy(context)
        context.request = request
        context.method = request.method()

        for middleware in self.request_middlewares:
            response = middleware.process_request(context, request, **kwargs)
            if response is not None:
                break
        else:
            try:
                response = callback(context, request, **kwargs)
            except Exception as error:
                logging.exception(error)
                response = error
        
        for middleware in self.response_middlewares:
            if isinstance(response, Exception):
                response = middleware.process_exception(context, request, response, **kwargs)
            else:
                try:
                    response = middleware.process_response(context, response, **kwargs)
                except Exception as error:
                    logging.exception(error)
                    response = error

        if isinstance(response, Exception):
            raise response
        else:
            return response
