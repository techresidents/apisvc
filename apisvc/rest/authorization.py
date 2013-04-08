import re

from rest.exceptions import AuthorizationError
from rest.filter import Filter
from rest.utils.resource import to_collection

class ResourceAuthorizer(object):
    def __init__(self):
        self.resource_class = None
    
    def contribute_to_class(self, resource_class, name):
        resource_class.desc.authorizer = self
        setattr(resource_class, name, self)
        self.resource_class = resource_class

    def authorize_request(self, context, request, **kwargs):
        allowed_methods = []
        if context.resource_class is self.resource_class:
            if context.bulk:
                allowed_methods = self.resource_class.desc.allowed_bulk_methods
            else:
                allowed_methods = self.resource_class.desc.allowed_methods
        elif context.resource_class and context.related_field:
            resource_class = context.resource_manager.resource_class
            if context.bulk:
                methods = resource_class.desc.allowed_related_bulk_methods
            else:
                methods = resource_class.desc.allowed_related_methods
            
            if context.related_field.name in methods:
                allowed_methods = methods[context.related_field.name]
        
        if request.method() not in allowed_methods:
            resource_name = context.resource_class.__name__
            msg = "'%s' not in %s's allowed methods %s" % \
                    (request.method(), resource_name, allowed_methods)
            raise AuthorizationError(msg)
    
    def authorize_response(self, context, response, **kwargs):
        return response

    def authorize_query_resources(self, context, resources, query):
        for resource in resources:
            if not isinstance(resource, self.resource_class):
                msg =  "invalid response, expected %s not %s" % \
                        (self.resource_class.__name__, resource.__class__.__name__)
                raise AuthorizationError(msg)

    def authorize_query(self, context, request, query):
        resource_class = context.resource_class
        resource_class_name = resource_class.__name__
        
        if context.data:
            for resource in to_collection(context.data):
                if not isinstance(resource, resource_class):
                    msg =  "invalid response, expected %s not %s" % \
                            (resource_class.__name__, resource.__class__.__name__)
                    raise AuthorizationError(msg)

        allowed_filters = resource_class.desc.allowed_filters
        for filter in query.filters:
            name, operation = filter.name().rsplit("__", 1)
            for name_regex, operations in allowed_filters.items():
                if re.match(name_regex, name) and operation in operations:
                    break
            else:
                msg = "'%s' not in %s allowed filters %s" % \
                        (name, resource_class_name, allowed_filters)
                raise AuthorizationError(msg)
        
        allowed_order_bys = resource_class.desc.allowed_order_bys
        for order_by in query.order_bys:
            name = order_by.name()
            for name_regex in allowed_order_bys:
                if re.match(name_regex, name):
                    break
            else:
                msg = "'%s' not in %s allowed order bys %s" % \
                        (name, resource_class_name, allowed_order_bys)
                raise AuthorizationError(msg)

        allowed_with_relations = resource_class.desc.allowed_with_relations
        for with_relation in query.with_relations:
            name = with_relation.name()
            for name_regex in allowed_with_relations:
                if re.match(name_regex, name):
                    break
            else:
                msg = "'%s' not in %s allowed with relations %s" % \
                        (name, resource_class_name, allowed_with_relations)
                raise AuthorizationError(msg)
        
        allowed_limit = resource_class.desc.allowed_limit
        if not query.slices:
            if request.method() != "POST":
                query.slice(0, allowed_limit)
        else:
            start, stop = query.slices
            if (stop-start) > allowed_limit:
                msg = "%s max limit exceeded" % resource_class_name
                raise AuthorizationError(msg)

        return self.authorize_exact_query(context, request, query)

    def authorize_exact_query(self, context, request, query):
        if context.resource_class is self.resource_class:
            if request.method() == "GET":
                if context.bulk:
                    query = self.authorize_all_query(context, request, query)
                else:
                    query = self.authorize_one_query(context, request, query)
            elif request.method() == "POST":
                if context.bulk:
                    query = self.authorize_bulk_create_query(context, request, query)
                else:
                    query = self.authorize_bulk_create_query(context, request, query)
            elif request.method() == "PUT":
                if context.bulk:
                    query = self.authorize_bulk_update_query(context, request, query)
                else:
                    query = self.authorize_update_query(context, request, query)
            elif request.method() == "DELETE":
                if context.bulk:
                    query = self.authorize_bulk_delete_query(context, request, query)
                else:
                    query = self.authorize_delete_query(context, request, query)
        elif context.resource_class and context.related_field:
            if request.method() == "GET":
                query = self.authorize_get_related_query(context, request, query)
            elif request.method() == "POST":
                query = self.authorize_create_related_query(context, request, query)
            elif request.method() == "PUT":
                query = self.authorize_update_related_query(context, request, query)
            elif request.method() == "DELETE":
                query = self.authorize_delete_related_query(context, request, query)
        return query

    def authorize_all_query(self, context, request, query):
        return query

    def authorize_one_query(self, context, request, query):
        return query

    def authorize_create_query(self, context, request, query):
        return query

    def authorize_bulk_create_query(self, context, request, query):
        return query

    def authorize_update_query(self, context, request, query):
        return query

    def authorize_bulk_update_query(self, context, request, query):
        return query

    def authorize_delete_query(self, context, request, query):
        return query

    def authorize_bulk_delete_query(self, context, request, query):
        return query

    def authorize_get_related_query(self, context, request, query):
        return query

    def authorize_create_related_query(self, context, request, query):
        return query

    def authorize_update_related_query(self, context, request, query):
        return query

    def authorize_delete_related_query(self, context, request, query):
        return query
    
    def authorize_query_response_resources(self, context, resources, query):
        for resource in resources:
            if not isinstance(resource, self.resource_class):
                msg =  "invalid response, expected %s not %s" % \
                        (self.resource_class.__name__, resource.__class__.__name__)
                raise AuthorizationError(msg)

    def authorize_query_response(self, context, response, query):
        resource_class = context.resource_class
        if response.data:
            for resource in to_collection(response.data):
                if not isinstance(resource, resource_class):
                    msg =  "invalid response, expected %s not %s" % \
                            (resource_class.__name__, resource.__class__.__name__)
                    raise AuthorizationError(msg)

        return self.authorize_exact_query_response(context, response, query)

    def authorize_exact_query_response(self, context, response, query):
        if context.resource_class is self.resource_class:
            if context.method == "GET":
                if context.bulk:
                    response = self.authorize_all_query_response(context, response, query)
                else:
                    response = self.authorize_one_query_response(context, response, query)
            elif context.method == "POST":
                if context.bulk:
                    response = self.authorize_bulk_create_query_response(context, response, query)
                else:
                    response = self.authorize_bulk_create_query_response(context, response, query)
            elif context.method == "PUT":
                if context.bulk:
                    response = self.authorize_bulk_update_query_response(context, response, query)
                else:
                    response = self.authorize_update_query_response(context, response, query)
            elif context.method == "DELETE":
                if context.bulk:
                    response = self.authorize_bulk_delete_query_response(context, response, query)
                else:
                    response = self.authorize_delete_query_response(context, response, query)
        elif context.resource_class and context.related_field:
            if context.method == "GET":
                response = self.authorize_get_related_query_response(context, response, query)
            elif context.method == "POST":
                response = self.authorize_create_related_query_response(context, response, query)
            elif context.method == "PUT":
                response = self.authorize_update_related_query_response(context, response, query)
            elif context.method == "DELETE":
                response = self.authorize_delete_related_query(context, response, query)
        return response

    def authorize_all_query_response(self, context, response, query):
        return response

    def authorize_one_query_response(self, context, response, query):
        return response

    def authorize_create_query_response(self, context, response, query):
        return response

    def authorize_bulk_create_query_response(self, context, response, query):
        return response

    def authorize_update_query_response(self, context, response, query):
        return response

    def authorize_bulk_update_query_response(self, context, response, query):
        return response

    def authorize_delete_query_response(self, context, response, query):
        return response

    def authorize_bulk_delete_query_response(self, context, response, query):
        return response

    def authorize_get_related_query_response(self, context, response, query):
        return response

    def authorize_create_related_query_response(self, context, response, query):
        return response

    def authorize_update_related_query_response(self, context, response, query):
        return response

    def authorize_delete_related_query_response(self, context, response, query):
        return response


class MacroAuthorizer(ResourceAuthorizer):
    def __init__(self, authorizers):
        super(MacroAuthorizer, self).__init__()
        self.authorizers = authorizers

    def contribute_to_class(self, resource_class, name):
        for authorizer in self.authorizers:
            authorizer.contribute_to_class(resource_class, name)
        super(MacroAuthorizer, self).contribute_to_class(resource_class, name)

    def authorize_request(self, context, request, **kwargs):
        for auth in self.authorizers:
            auth.authorize_request(context, request, **kwargs)
    
    def authorize_response(self, context, response, **kwargs):
        for auth in self.authorizers:
            response = auth.authorize_response(context, response, **kwargs)
        return response

    def authorize_query_resources(self, context, resources, query):
        for auth in self.authorizers:
            auth.authorize_query_resources(context, resources, query)

    def authorize_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_query(context, request, query)
        return query

    def authorize_exact_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_exact_query(context, request, query)
        return query

    def authorize_all_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_all_query(context, request, query)
        return query

    def authorize_one_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_one_query(context, request, query)
        return query

    def authorize_create_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_create_query(context, request, query)
        return query

    def authorize_bulk_create_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_bulk_create_query(context, request, query)
        return query

    def authorize_update_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_update_query(context, request, query)
        return query

    def authorize_bulk_update_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_bulk_update_query(context, request, query)
        return query

    def authorize_delete_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_delete_query(context, request, query)
        return query

    def authorize_bulk_delete_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_bulk_delete_query(context, request, query)
        return query

    def authorize_get_related_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_get_related_query(context, request, query)
        return query

    def authorize_create_related_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_create_related_query(context, request, query)
        return query

    def authorize_update_related_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_update_related_query(context, request, query)
        return query

    def authorize_delete_related_query(self, context, request, query):
        for auth in self.authorizers:
            query = auth.authorize_delete_related_query(context, request, query)
        return query
    
    def authorize_query_response_resources(self, context, resources, query):
        for auth in self.authorizers:
            auth.authorize_query_response_resources(context, resources, query)

    def authorize_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_query_response(context, response, query)
        return response

    def authorize_exact_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_exact_query_response(context, response, query)
        return response

    def authorize_all_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_all_query_response(context, response, query)
        return response

    def authorize_one_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_one_query_response(context, response, query)
        return response

    def authorize_create_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_create_query_response(context, response, query)
        return response

    def authorize_bulk_create_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_bulk_create_query_response(context, response, query)
        return response

    def authorize_update_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_update_query_response(context, response, query)
        return response

    def authorize_bulk_update_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_bulk_update_query_response(context, response, query)
        return response

    def authorize_delete_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_delete_query_response(context, response, query)
        return response

    def authorize_bulk_delete_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_bulk_delete_query_response(context, response, query)
        return response

    def authorize_get_related_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_get_related_query_response(context, response, query)
        return response

    def authorize_create_related_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_create_related_query_response(context, response, query)
        return response

    def authorize_update_related_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_update_related_query_response(context, response, query)
        return response

    def authorize_delete_related_query_response(self, context, response, query):
        for auth in self.authorizers:
            response = auth.authorize_delete_related_query_response(context, response, query)
        return response


class MultiAuthorizer(ResourceAuthorizer):
    def __init__(self, authorizer_map):
        super(MultiAuthorizer, self).__init__()
        self.authorizer_map = self._normalize_authorizer_map(authorizer_map)
    
    def _normalize_authorizer_map(self, authorizer_map):
        result = {}
        for methods, authorizer in authorizer_map.items():
            if isinstance(methods, basestring):
                result[methods] = authorizer
            else:
                for method in methods:
                    result[method] = authorizer
        return result

    def _get_authorizer(self, context):
        return self.authorizer_map.get(context.method, None)

    def contribute_to_class(self, resource_class, name):
        for authorizer in self.authorizer_map.values():
            authorizer.contribute_to_class(resource_class, name)
        super(MultiAuthorizer, self).contribute_to_class(resource_class, name)

    def authorize_request(self, context, request, **kwargs):
        auth = self._get_authorizer(context)
        if auth is not None:
            auth.authorize_request(context, request, **kwargs)
    
    def authorize_response(self, context, response, **kwargs):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_response(context, response, **kwargs)
        return response

    def authorize_query_resources(self, context, resources, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            auth.authorize_query_resources(context, resources, query)

    def authorize_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_query(context, request, query)
        return query

    def authorize_exact_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_exact_query(context, request, query)
        return query

    def authorize_all_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_all_query(context, request, query)
        return query

    def authorize_one_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_one_query(context, request, query)
        return query

    def authorize_create_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_create_query(context, request, query)
        return query

    def authorize_bulk_create_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_bulk_create_query(context, request, query)
        return query

    def authorize_update_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_update_query(context, request, query)
        return query

    def authorize_bulk_update_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_bulk_update_query(context, request, query)
        return query

    def authorize_delete_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_delete_query(context, request, query)
        return query

    def authorize_bulk_delete_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_bulk_delete_query(context, request, query)
        return query

    def authorize_get_related_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_get_related_query(context, request, query)
        return query

    def authorize_create_related_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_create_related_query(context, request, query)
        return query

    def authorize_update_related_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_update_related_query(context, request, query)
        return query

    def authorize_delete_related_query(self, context, request, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            query = auth.authorize_delete_related_query(context, request, query)
        return query
    
    def authorize_query_response_resources(self, context, resources, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            auth.authorize_query_response_resources(context, resources, query)

    def authorize_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_query_response(context, response, query)
        return response

    def authorize_exact_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_exact_query_response(context, response, query)
        return response

    def authorize_all_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_all_query_response(context, response, query)
        return response

    def authorize_one_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_one_query_response(context, response, query)
        return response

    def authorize_create_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_create_query_response(context, response, query)
        return response

    def authorize_bulk_create_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_bulk_create_query_response(context, response, query)
        return response

    def authorize_update_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_update_query_response(context, response, query)
        return response

    def authorize_bulk_update_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_bulk_update_query_response(context, response, query)
        return response

    def authorize_delete_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_delete_query_response(context, response, query)
        return response

    def authorize_bulk_delete_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_bulk_delete_query_response(context, response, query)
        return response

    def authorize_get_related_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_get_related_query_response(context, response, query)
        return response

    def authorize_create_related_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_create_related_query_response(context, response, query)
        return response

    def authorize_update_related_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_update_related_query_response(context, response, query)
        return response

    def authorize_delete_related_query_response(self, context, response, query):
        auth = self._get_authorizer(context)
        if auth is not None:
            response = auth.authorize_delete_related_query_response(context, response, query)
        return response


class RelatedAuthorizer(ResourceAuthorizer):
    def __init__(self,
            related_field_name,
            context_attribute,
            exclude_methods=None):
        super(RelatedAuthorizer, self).__init__()
        self.related_field_name = related_field_name
        self.context_attribute = context_attribute
        self.exclude_methods = exclude_methods or []

    def _get_related_field(self):
        return self.resource_class.desc\
                .related_fields_by_name[self.related_field_name]

    def _get_context_value(self, context):
        return getattr(context, self.context_attribute, None)

    def _authorize_query(self, context, request, query):
        if context.method == "POST":
            return query
        
        related_field = self._get_related_field()
        kwargs = {}
        kwargs[related_field.name] = self._get_context_value(context)
        kwargs[related_field.attname] = self._get_context_value(context)
        related_filters = Filter.parse(context.resource_class, **kwargs)

        for filter in query.filters:
            if filter in related_filters:
                break
            elif filter.name() in [r.name() for r in related_filters]:
                raise AuthorizationError("non-%s resource filter" %
                        self.related_field_name)
        else:
            kwargs = {}
            kwargs[related_field.name] = self._get_context_value(context)
            uri_key_filter = self.resource_class.desc.manager.uri_key() + '__eq'

            #if the query contains the uri key filter
            #add the required filter as a convenience
            if uri_key_filter in [f.name() for f in query.filters]:
                query = query.filter(**kwargs)
            #Or if this resource is being access through a related resource
            #also add filter
            elif context.base_resource_instance:
                query = query.filter(**kwargs)
            else:
                raise AuthorizationError("%s resource filter missing" %
                        self.related_field_name)

        return query

    def _authorize_related_query(self, context, request, query):
        if request.method() == "POST":
            return query

        related_field = self._get_related_field()
        resource_class = context.resource_manager.resource_class
        resource_key_name = context.resource_manager.uri_key()
        resource_key = getattr(context.base_resource_instance, resource_key_name)
        
        kwargs = {}
        kwargs[resource_key_name] = resource_key
        kwargs[related_field.attname] = self._get_context_value(context)

        try:
            resource_class.desc.manager.one(**kwargs)
        except:
            raise AuthorizationError("non-%s resource in related query" %
                    self.related_field_name)
        return query

    def authorize_query(self, context, request, query):
        query = super(RelatedAuthorizer, self).authorize_query(
                context=context,
                request=request,
                query=query)

        if context.method in self.exclude_methods:
            return query

        if context.resource_class is self.resource_class:
            query = self._authorize_query(context, request, query)
        elif context.resource_class and context.related_field:
            query = self._authorize_related_query(context, request, query)
        else:
            raise RuntimeError("Unknown resource type")
        
        return query

    def authorize_query_resources(self, context, resources, query):
        super(RelatedAuthorizer, self).authorize_query_resources(
                context=context,
                resources=resources,
                query=query)

        if context.method in self.exclude_methods:
            return
        
        related_field = self._get_related_field()
        for resource in resources:
            value = getattr(resource, related_field.attname)
            value = related_field.validate_for_model(value)
            if value != self._get_context_value(context):
                raise AuthorizationError("non-%s resource in query" %
                        self.related_field_name)

    def authorize_query_response_resources(self, context, resources, query):
        super(RelatedAuthorizer, self).authorize_query_response_resources(
                context=context,
                resources=resources,
                query=query)
        
        if context.method in self.exclude_methods:
            return

        if context.resource_class is self.resource_class:
            pass
        elif context.resource_class and \
                context.related_field and \
                context.related_field.relation is self.resource_class:
                    pass
        else:
            #resources came from with relations.
            #no easy way to authorize resources except
            #by issuing another query joining with user.
            if resources:
                primary_keys = [r.primary_key_value() for r in resources]
                primary_key_filter = "%s__in" % self.resource_class.desc.primary_key

                kwargs = {}
                kwargs[self.related_field_name] = self._get_context_value(context)
                kwargs[primary_key_filter] = primary_keys
                
                #TODO replace with count() query once supported
                authorized_resources = self.resource_class.desc.manager.all(**kwargs)
                if len(authorized_resources) != len(resources):
                    raise AuthorizationError("non-%s resource in query response" %
                            self.related_field_name)

class FilterAuthorizer(ResourceAuthorizer):
    def __init__(self,
            filters,
            context_attribute,
            exclude_methods=None):
        super(FilterAuthorizer, self).__init__()
        if isinstance(filters, basestring):
            self.filters = [filters]
        else:
            self.filters = filters
        self.context_attribute = context_attribute
        self.exclude_methods = exclude_methods or []

    def _get_context_value(self, context):
        return getattr(context, self.context_attribute, None)

    def _authorize_query(self, context, request, query):
        if context.method == "POST":
            return query
        
        kwargs = {}
        for filter in self.filters:
            kwargs[filter] = self._get_context_value(context)
        filters = Filter.parse(context.resource_class, **kwargs)

        for filter in query.filters:
            if filter in filters:
                break
            elif filter.name() in [r.name() for r in filters]:
                raise AuthorizationError("non-%s resource filter" %
                        self.filters[0])
        else:
            kwargs = {}
            kwargs[self.filters[0]] = self._get_context_value(context)
            uri_key_filter = self.resource_class.desc.manager.uri_key() + '__eq'

            #if the query contains the uri key filter
            #add the required filter as a convenience
            if uri_key_filter in [f.name() for f in query.filters]:
                query = query.filter(**kwargs)
            #Or if this resource is being access through a related resource
            #also add filter
            elif context.base_resource_instance:
                query = query.filter(**kwargs)
            else:
                raise AuthorizationError("%s resource filter missing" %
                        self.filters[0])

        return query

    def _authorize_related_query(self, context, request, query):
        if request.method() == "POST":
            return query

        resource_class = context.resource_manager.resource_class
        resource_key_name = context.resource_manager.uri_key()
        resource_key = getattr(context.base_resource_instance, resource_key_name)
        
        kwargs = {}
        kwargs[resource_key_name] = resource_key
        kwargs[self.filters[0]] = self._get_context_value(context)

        try:
            resource_class.desc.manager.one(**kwargs)
        except:
            raise AuthorizationError("non-%s resource in related query" %
                    self.filters[0])
        return query

    def authorize_query(self, context, request, query):
        query = super(FilterAuthorizer, self).authorize_query(
                context=context,
                request=request,
                query=query)

        if context.method in self.exclude_methods:
            return query

        if context.resource_class is self.resource_class:
            query = self._authorize_query(context, request, query)
        elif context.resource_class and context.related_field:
            query = self._authorize_related_query(context, request, query)
        else:
            raise RuntimeError("Unknown resource type")
        
        return query

    def authorize_query_resources(self, context, resources, query):
        super(FilterAuthorizer, self).authorize_query_resources(
                context=context,
                resources=resources,
                query=query)

        if context.method in self.exclude_methods:
            return
        
        kwargs = {}
        for filter in self.filters:
            kwargs[filter] = self._get_context_value(context)
        filters = Filter.parse(context.resource_class, **kwargs)
    
        field = None
        for filter in filters:
            if not filter.related_fields:
                field = filter.operation.target_field
                break
        
        if field:
            for resource in resources:
                value = getattr(resource, field.attname)
                value = field.validate_for_model(value)
                if value != self._get_context_value(context):
                    raise AuthorizationError("non-%s resource in query" %
                            self.filters[0])

    def authorize_query_response_resources(self, context, resources, query):
        super(FilterAuthorizer, self).authorize_query_response_resources(
                context=context,
                resources=resources,
                query=query)
        
        if context.method in self.exclude_methods:
            return

        if context.resource_class is self.resource_class:
            pass
        elif context.resource_class and \
                context.related_field and \
                context.related_field.relation is self.resource_class:
                    pass
        else:
            #resources came from with relations.
            #no easy way to authorize resources except
            #by issuing another query joining with user.
            if resources:
                primary_keys = [r.primary_key_value() for r in resources]
                primary_key_filter = "%s__in" % self.resource_class.desc.primary_key

                kwargs = {}
                kwargs[self.filters[0]] = self._get_context_value(context)
                kwargs[primary_key_filter] = primary_keys
                
                #TODO replace with count() query once supported
                authorized_resources = self.resource_class.desc.manager.all(**kwargs)
                if len(authorized_resources) != len(resources):
                    raise AuthorizationError("non-%s resource in query response" %
                            self.filters[0])
