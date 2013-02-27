import copy
import functools
import logging

from rest.context import RequestContext
from rest.fields import ListField
from rest.manager import ResourceManager
from rest.query import Query
from rest.resource import ResourceBase

class ApiResourceQuery(Query):

    def __init__(self, api, resource_class, transaction_factory):
        self.api = api
        super(ApiResourceQuery, self).__init__(
                resource_class=resource_class,
                transaction_factory = transaction_factory)

    def _get_entities(self):
        entities = []

        for resource_class in self.api.resource_classes.values():
            location = self.api.get_resource_class_uri(resource_class)
            entity = {
                "name": resource_class.desc.resource_name,
                "location": location,
                "schema": "%s/schema" % location,
            }
            entities.append(entity)
        return entities

    def one(self):
        entities = self._get_entities()
        api = self.resource_class(
                entities=entities)
        return api


class ApiResourceManager(ResourceManager):
    def __init__(self, api):
        self.api = api
        super(ApiResourceManager, self).__init__(query_factory=self.query_factory)
    
    def query_factory(self):
        return ApiResourceQuery(self.api, self.resource_class, None)

    def uris(self):
        results = []
        uri = r"^$"
        context = RequestContext(
                resource_class=self.resource_class,
                bulk=False,
                resource_manager=self)
        results.append((uri, context, self.dispatch))
        return results


class ApiResourceBase(ResourceBase):
    class Meta:
        abstract = True
        resource_name = "api"
        methods = ["GET"]

    entities = ListField()


class Api(object):
    def __init__(self, base_uri):
        self.base_uri = base_uri
        if self.base_uri.endswith("/"):
            self.base_uri = self.base_uri[:-1]

        self.uris = []
        self.request_middlewares = []
        self.response_middlewares = []
        self.resource_classes = {}

        #dynamically create ApiResourceBase sublcass
        api_class_attributes = {
            "__module__": ApiResourceBase.__module__,
            "objects": ApiResourceManager(self)
        }

        api_resource_class = type(
                self.base_uri.replace("/", "_")+"Api",
                (ApiResourceBase,),
                api_class_attributes)

        self.add_resource(api_resource_class)

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

    def get_resource_class_uri(self, resource_class):
        return "%s/%s" % (
               self.base_uri,
               resource_class.desc.resource_name)
    
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
        context.path = context.request.req.path
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
