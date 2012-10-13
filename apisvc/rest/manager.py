from rest.api import RequestContext
from rest.fields import ForeignKey
from rest.response import Response
from rest.query import Query
from rest.transaction import Transaction

class ResourceManager(object):
    def __init__(self, query_factory=None, transaction_factory=None):
        self.resource_class = None
        self.query_factory = query_factory or \
                (lambda: Query(self.resource_class, self.transaction_factory))
        self.transaction_factory = transaction_factory or \
                (lambda: Transaction())

    def contribute_to_class(self, resource_class, name):
        self.resource_class = resource_class
        resource_class.desc.manager = self
        setattr(resource_class, name, self)

    def uris(self):
        result = []

        resource_name = self.resource_class.desc.resource_name
        primary_key = self.resource_class.desc.primary_key
        base_uri = r"/%s" % resource_name
        
        #Add subresource uris
        for subresource in self.resource_class.desc.subresources:
            for uri, context, method in subresource.desc.manager.uris():
                if uri.startswith("^"):
                    uri = uri[1:]
                if uri.endswith("$"):
                    uri = uri[:-1]
                uri = r"%s/%s$" % (base_uri, uri)
            result.append((uri, context, method))
        
        uri = r"%s/(?P<%s>\w+)(\?.*)?$" % (base_uri, primary_key)
        context = RequestContext(resource_class=self.resource_class, bulk=False)
        result.append((uri, context, self.dispatch))

        for field in self.resource_class.desc.related_fields:
            if field.hidden:
                continue
            uri = r"%s/(?P<%s__%s>\w+)/%s(\?.*)?$" % (base_uri, resource_name, primary_key, field.name)
            context = RequestContext(resource_class=field.relation, related_field=field, bulk=field.many)
            result.append((uri, context, self.dispatch))
            
            related_primary_key = field.relation.desc.primary_key
            uri = r"%s/(?P<%s__%s>\w+)/%s/(?P<%s>\w+)(\?.*)?$" % (base_uri, resource_name, primary_key, field.name, related_primary_key)
            context = RequestContext(resource_class=field.relation, related_field=field, bulk=False)
            result.append((uri, context, self.dispatch))
        
        uri = r"%s(\?.*)?$" % base_uri
        context = RequestContext(resource_class=self.resource_class, bulk=True)
        result.append((uri, context, self.dispatch))
        return result

    def dispatch(self, context, request, **kwargs):
        response_code = 200

        if context.resource_class is self.resource_class and context.related_field is None:
            if request.method() == "GET":
                if context.bulk:
                    result = context.query.all()
                else:
                    result = context.query.one()
            elif request.method() == "POST":
                if context.bulk:
                    result = context.query.bulk_create(resources=context.data)
                else:
                    result = context.query.create(resource=context.data)
                response_code = 201
            elif request.method() == "PUT":
                if context.bulk:
                    result = context.query.bulk_update(resources=context.data)
                else:
                    result = context.query.update(resource=context.data)
            elif request.method() == "DELETE":
                if context.bulk:
                    result = context.query.bulk_delete(resources=context.data)
                else:
                    result = context.query.delete()
        
        elif context.resource_class and context.related_field:
            if request.method() == "GET":
                if context.bulk:
                    result = context.query.all()
                else:
                    result = context.query.one()
            elif request.method() == "POST":
                if context.bulk:
                    result = context.query.create_bulk(context.data)
                else:    
                    result = context.query.create(context.data)
                response_code = 201
            elif request.method() == "PUT":
                if context.bulk:
                    result = context.query.bulk_update(context.data)
                else:
                    result = context.query.update(context.data)
            elif request.method() == "DELETE":
                if context.bulk:
                    result = context.query.bulk_delete(context.data)
                else:
                    result = context.query.delete()
        else:
            result = None
        
        result = Response(code=response_code, data=result)
        return result
        
    def build_query(self, **kwargs):
        query = self.query_factory()
        query.parse(**kwargs)
        return query

    def build_create_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_get_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_one_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_all_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_update_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_delete_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_bulk_create_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_bulk_update_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_bulk_delete_query(self, **kwargs):
        return self.build_query(**kwargs)

    def build_related_query_kwargs(self, related_field, resource_instance, **kwargs):
        if related_field.self_referential:
            if isinstance(related_field, ForeignKey):
                arg = related_field.resource_class.desc.primary_key
                value = getattr(resource_instance, related_field.attname, None)
                if value is None:
                    #Fetch resource and double check
                    primary_key = getattr(resource_instance, arg)
                    resource_instance = resource_instance.desc.manager.get(primary_key)
                    value = getattr(resource_instance, related_field.attname, None)
            else:
                arg = related_field.reverse.attname
                value = getattr(resource_instance, resource_instance.desc.primary_key)
        else:
            arg = "%s__%s" % (related_field.reverse.name, resource_instance.desc.primary_key)
            value = getattr(resource_instance, resource_instance.desc.primary_key)
        
        if arg in kwargs and kwargs[arg] != value:
            raise RuntimeError()
        kwargs[arg] = value
        return kwargs

    def build_create_related_query(self, related_field, resource_instance, **kwargs):
        relation = related_field.relation
        if related_field.many:
            query = relation.desc.manager.build_bulk_create_query(**kwargs)
        else:
            query = relation.desc.manager.build_create_query(**kwargs)
        return query
    
    def build_get_related_query(self, related_field, resource_instance, **kwargs):
        relation = related_field.relation
        kwargs = self.build_related_query_kwargs(related_field, resource_instance, **kwargs)
        if related_field.many:
            query = relation.desc.manager.build_all_query(**kwargs)
        else:
            query = relation.desc.manager.build_one_query(**kwargs)
        return query

    def build_update_related_query(self, related_field, resource_instance, **kwargs):
        relation = related_field.relation
        kwargs = self.build_related_query_kwargs(related_field, resource_instance, **kwargs)
        if related_field.many:
            query = relation.desc.manager.build_bulk_update_query(**kwargs)
        else:
            query = relation.desc.manager.build_update_query(**kwargs)
        return query

    def build_delete_related_query(self, related_field, resource_instance, **kwargs):
        relation = related_field.relation
        kwargs = self.build_related_query_kwargs(related_field, resource_instance, **kwargs)
        if related_field.many:
            query = relation.desc.manager.build_bulk_delete_query(**kwargs)
        else:
            query = relation.desc.manager.build_delete_query(**kwargs)
        return query

    def create(self, **kwargs):
        query = self.build_create_query()
        return query.create(**kwargs)

    def get(self, primary_key, **kwargs):
        query = self.build_get_query(**kwargs)
        return query.get(primary_key)

    def one(self, **kwargs):
        query = self.build_one_query(**kwargs)
        return query.one()

    def all(self, **kwargs):
        query = self.build_all_query(**kwargs)
        result = query.all()
        return result
    
    def filter(self, **kwargs):
        query = self.build_query()
        query = query.filter(**kwargs)
        return query

    def update(self, **kwargs):
        query = self.build_update_query()
        return query.update(**kwargs)

    def delete(self, **kwargs):
        query = self.build_delete_query()
        return query.delete(**kwargs)

    def bulk_create(self, resources):
        query = self.build_bulk_create_query()
        return query.bulk_create(resources)

    def bulk_update(self, resources):
        query = self.build_bulk_update_query()
        return query.bulk_update(resources)

    def bulk_delete(self, resources):
        query = self.build_bulk_delete_query()
        return query.bulk_delete(resources)

    def create_relation(self, related_field, resource_instance, **kwargs):
        query = self.build_create_related_query(related_field, resource_instance, **kwargs)
        return query.create(**kwargs)

    def get_relation(self, related_field, resource_instance, **kwargs):
        query = self.build_get_related_query(related_field, resource_instance, **kwargs)
        if related_field.many:
            result = query.all()
        else:
            result = query.one()
        return result

    def update_relation(self, related_field, resource_instance, **kwargs):
        query = self.build_update_related_query(related_field, resource_instance, **kwargs)
        return query.update(**kwargs)

    def delete_relation(self, related_field, resource_instance, **kwargs):
        query = self.build_delete_related_query(related_field, resource_instance, **kwargs)
        return query.delete(**kwargs)
