import logging 

from rest.exceptions import InvalidQuery, ValidationError
from rest.middleware.base import RestMiddleware
from rest.response import Response

class QueryBuilderMiddleware(RestMiddleware):

    def _parse_url_params(self, request):
        result = {}
        if request.url_params:
            for param, value in request.url_params.items():
                if isinstance(value, list):
                    value = value[0]
                result[param] = value
        return result
    
    def _build_query(self, context, request, **kwargs):
        query = None
        url_kwargs = self._parse_url_params(request)

        query_kwargs = dict(**url_kwargs)
        query_kwargs.update(kwargs)

        if request.method() == "GET":
            if context.bulk:
                query = context.resource_manager.build_all_query(**query_kwargs)
            else:
                query = context.resource_manager.build_get_query(**query_kwargs)
        elif request.method() == "POST":
            if context.bulk:
                query = context.resource_manager.build_bulk_create_query(**query_kwargs)
            else:
                query = context.resource_manager.build_create_query(**query_kwargs)
        elif request.method() == "PUT":
            if context.bulk:
                query = context.resource_manager.build_bulk_update_query(**query_kwargs)
            else:
                query = context.resource_manager.build_update_query(**query_kwargs)
        elif request.method() == "DELETE":
            if context.bulk:
                query = context.resource_manager.build_bulk_delete_query(**query_kwargs)
            else:
                query = context.resource_manager.build_delete_query(**query_kwargs)
        return query
    
    def _build_related_query(self, context, request, **kwargs):
        query = None
        url_kwargs = self._parse_url_params(request)
        
        base_resource_name = context.resource_manager.resource_class.desc.resource_name
        base_uri_key_name = context.resource_manager.uri_key()

        query_kwargs = dict(**url_kwargs)
        query_kwargs.update(kwargs)
        
        base_uri_key = query_kwargs.pop("%s__%s" % (base_resource_name, base_uri_key_name))
        instance_kwargs = {base_uri_key_name: base_uri_key}
        instance = context.resource_manager.resource_class(**instance_kwargs)
        context.base_resource_instance = instance

        if request.method() == "GET":
            query = context.resource_manager.build_get_related_query(context.related_field, instance, **query_kwargs)
        elif request.method() == "POST":
            query = context.resource_manager.build_create_related_query(context.related_field, instance, **query_kwargs)
        elif request.method() == "PUT":
            query = context.resource_manager.build_update_related_query(context.related_field, instance, **query_kwargs)
        elif request.method() == "DELETE":
            query = context.resource_manager.build_delete_related_query(context.related_field, instance, **query_kwargs)
        return query

    def process_request(self, context, request, **kwargs):
        response = None

        try:
            if context.resource_manager.resource_class is context.resource_class and context.related_field is None:
                query = self._build_query(context, request, **kwargs)
            elif context.resource_class and context.related_field:
                query = self._build_related_query(context, request, **kwargs)
            context.query = query

        except InvalidQuery as error:
            logging.warning(str(error))
            response = Response(data="invalid request", code=400)
        except ValidationError as error:
            logging.warning(str(error))
            response = Response(data="invalid request", code=400)
        except Exception as error:
            logging.exception(error)
            response = Response(data="invalid request", code=400)

        return response

    def process_response(self, context, response, **kwargs):
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return None
