import re

from rest.exceptions import AuthorizationError
from rest.filter import Filter

class ResourceAuthorizer(object):
    def __init__(self):
        self.resource_class = None
    
    def _to_list(self, value):
        if isinstance(value, (list, tuple)):
            return value
        else:
            return [value]

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
            for resource in self._to_list(context.data):
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
            for resource in self._to_list(response.data):
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


class MacroResourceAuthorizer(ResourceAuthorizer):
    def __init__(self, authorizers):
        super(MacroResourceAuthorizer, self).__init__()
        self.authorizers = authorizers

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


class PerUserResourceAuthorizer(ResourceAuthorizer):
    def __init__(self, user_resource_class, user_filter, exclude_methods=None):
        super(PerUserResourceAuthorizer, self).__init__()
        self.user_resource_class = user_resource_class
        self.user_filter = user_filter
        self.exclude_methods = exclude_methods or []
        self.resource_class = None
    
    def _authorize_query(self, context, request, query):
        if request.method() == "POST":
            return query

        kwargs = {}
        kwargs[self.user_filter] = context.user_id

        user_filter = Filter.parse(context.resource_class, **kwargs)[0]
        for filter in query.filters:
            if filter.operation.target_field is user_filter.operation.target_field:
                if filter.operation.name != user_filter.operation.name or\
                        filter.operation.operands != user_filter.operation.operands:
                            raise AuthorizationError("non-user resource - invalid user fiilter")
                break
        else:
            query = query.filter(**kwargs)
        
        return query

    def _authorize_related_query(self, context, request, query):
        if request.method() == "POST":
            return query

        resource_class = context.resource_manager.resource_class
        primary_key_name = resource_class.desc.primary_key
        primary_key_field = resource_class.desc.primary_key_field
        primary_key = None
        for filter in query.filters:
            if filter.operation.target_field is primary_key_field:
                primary_key = filter.operation.operands[0]
        kwargs = {}
        kwargs[primary_key_name] = primary_key
        kwargs[self.user_filter] = context.user_id
        
        try:
            resource_class.desc.manager.one(**kwargs)
        except:
            raise AuthorizationError("non-user resource")
        return query

    def authorize_query(self, context, request, query):
        query = super(PerUserResourceAuthorizer, self).authorize_query(
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
        super(PerUserResourceAuthorizer, self).authorize_query_resources(
                context=context,
                resources=resources,
                query=query)

        if context.method in self.exclude_methods:
            return
        
        for resource in resources:
            for related_field in self.resource_class.desc.related_fields:
                if related_field.relation is self.user_resource_class \
                    and not related_field.many:
                        user_id = getattr(resource, related_field.attname)
                        user_id = related_field.validate_for_model(user_id)
                        if user_id != context.user_id:
                            raise AuthorizationError("invalid user id")


    def authorize_query_response_resources(self, context, resources, query):
        super(PerUserResourceAuthorizer, self).authorize_query_response_resources(
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
                kwargs[self.user_filter] = context.user_id
                kwargs[primary_key_filter] = primary_keys
                
                #TODO replace with count() query once supported
                authorized_resources = self.resource_class.desc.manager.all(**kwargs)
                if len(authorized_resources) != len(resources):
                    raise AuthorizationError("non-user resources")
