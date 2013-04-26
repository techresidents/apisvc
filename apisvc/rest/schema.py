from rest.context import RequestContext
from rest.fields import BooleanField, DateField, DateTimeField, DictField, FloatField, \
        IntegerField, ListField, RelatedField, StringField, TimestampField, StructField
from rest.manager import ResourceManager
from rest.query import Query
from rest.resource import ResourceBase

def field_to_type(field):
    result = None
    if isinstance(field, BooleanField):
        result = "boolean"
    elif isinstance(field, DateField):
        result = "date"
    elif isinstance(field, DateTimeField):
        result = "datetime"
    elif isinstance(field, DictField):
        result = "dict"
    elif isinstance(field, FloatField):
        result = "float"
    elif isinstance(field, IntegerField):
        result = "integer"
    elif isinstance(field, ListField):
        result = "list"
    elif isinstance(field, RelatedField):
        result = "related"
    elif isinstance(field, StringField):
        result = "string"
    elif isinstance(field, TimestampField):
        result = "timestamp"
    elif isinstance(field, StructField):
        result = "struct"
    return result


class SchemaQuery(Query):
    def _get_fields(self, container):
        fields = {}

        for field in container.desc.fields:
            if field.hidden:
                continue

            field_dict = {}
            field_dict = {
                "nullable": field.nullable,   
                "readonly": field.readonly,
                "type": field_to_type(field)
            }
            if isinstance(field, StructField):
                field_dict["fields"] = self._get_fields(field.struct_class)

            fields[field.attname] = field_dict

        for field in container.desc.related_fields:
            if field.hidden:
                continue

            field_dict = {}
            field_dict = {
                "nullable": field.nullable,   
                "readonly": field.readonly,
                "type": field_to_type(field)
            }
            fields[field.name] = field_dict

        return fields   

    def one(self):
        parent = self.resource_class.desc.parent_resource_class

        fields = self._get_fields(parent)
        methods = parent.desc.allowed_methods
        filters = parent.desc.allowed_filters
        order_bys = parent.desc.allowed_order_bys
        with_relations = parent.desc.allowed_with_relations
        limit = parent.desc.allowed_limit
        
        schema = self.resource_class(
                methods=methods,
                fields=fields,
                filters=filters,
                order_bys=order_bys,
                with_relations=with_relations,
                limit=limit)

        return schema


class SchemaResourceManager(ResourceManager):
    def __init__(self):
        super(SchemaResourceManager, self).__init__(query_factory=self.query_factory)
    
    def query_factory(self):
        return SchemaQuery(self.resource_class, None)

    def uris(self):
        results = []
        resource_name = self.resource_class.desc.resource_name
        uri = r"^/%s$" % resource_name
        context = RequestContext(
                resource_class=self.resource_class,
                bulk=False,
                resource_manager=self)
        results.append((uri, context, self.dispatch))
        return results

class SchemaResourceBase(ResourceBase):
    class Meta:
        abstract = True
        resource_name = "schema"
        methods = ["GET"]

    methods = ListField()
    fields = DictField()
    filters = DictField()
    order_bys = ListField()
    with_relations = ListField()
    limit = IntegerField()
