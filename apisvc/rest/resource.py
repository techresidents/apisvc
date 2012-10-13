from rest.authentication import ResourceAuthenticator
from rest.authorization import ResourceAuthorizer
from rest.fields import RelatedField
from rest.manager import ResourceManager
from rest.sanitization import ResourceSanitizer
from rest.serialization import ResourceSerializer

class ResourceDescription(object):
    def __init__(self, **kwargs):
        self.abstract = False
        self.resource_name = None
        self.parent_resource_class=None
        self.subresources = []
        self.model_class = None
        self.primary_key = None
        self.primary_key_field = None
        self.fields = []
        self.fields_by_name = {}
        self.related_fields = []
        self.related_fields_by_name = {}
        self.allowed_methods = []
        self.allowed_bulk_methods = []
        self.allowed_related_methods = {}
        self.allowed_related_bulk_methods = {}
        self.allowed_filters = {}
        self.allowed_order_bys = []
        self.allowed_with_relations = []
        self.allowed_limit = None
        self.resource_class = None
        self.authenticator = None
        self.authorizer = None
        self.manager = None
        self.sanitizer = None
        self.serializer = None

        self.update(**kwargs)

    def update(self, **kwargs):
        for name, value in kwargs.items():
            if value:
                setattr(self, name, value)

    def contribute_to_class(self, resource_class, name):
        self.resource_class = resource_class
        setattr(resource_class, name, self)
    
    def add_subresource(self, resource):
        self.subresources.append(resource)

    def add_field(self, field):
        if field.primary_key:
            self.primary_key = field.attname
            self.primary_key_field = field

        if isinstance(field, RelatedField) and field.many:
            self.related_fields.append(field)
            self.related_fields_by_name[field.name] = field
        else:
            self.fields.append(field)
            self.fields_by_name[field.attname] = field
            if isinstance(field, RelatedField):
                self.related_fields.append(field)
                self.related_fields_by_name[field.name] = field


class ResourceMeta(type):
    def __new__(cls, name, bases, attributes):
        
        #parent classes derived from ResourceMeta
        parents = [base for base in bases if isinstance(base, ResourceMeta)]
        
        #create new class
        module = attributes.pop("__module__")
        new_class = super(ResourceMeta, cls).__new__(
                cls,
                name,
                bases,
                {"__module__": module})
        
        #Get 'Meta' class from parent, but only use it if no 'Meta'
        #class is provided by this class.
        meta = getattr(new_class, "Meta", None)
        
        #If 'Meta' class is provided in attributes, use this in
        #place of any parent 'Meta' class. In the future it may
        #be better to change this to attempt to merge
        #'Meta' class attributes.
        attr_meta = attributes.get("Meta", {})
        if attr_meta:
            meta = attr_meta

        #create resource description
        desc_kwargs = {}

        desc_kwargs["Meta"] = meta
        desc_kwargs["abstract"] = getattr(meta, "abstract", False)
        desc_kwargs["resource_name"] = getattr(meta, "resource_name", None)
        desc_kwargs["model_class"] = getattr(meta, "model_class", None)
        desc_kwargs["allowed_methods"] = getattr(meta, "methods", None)
        desc_kwargs["allowed_bulk_methods"] = getattr(meta, "bulk_methods", None)
        desc_kwargs["allowed_related_methods"] = getattr(meta, "related_methods", None)
        desc_kwargs["allowed_related_bulk_methods"] = getattr(meta, "related_bulk_methods", None)
        desc_kwargs["allowed_filters"] = getattr(meta, "filtering", None)
        desc_kwargs["allowed_order_bys"] = getattr(meta, "ordering", None)
        desc_kwargs["allowed_with_relations"] = getattr(meta, "with_relations", None)
        desc_kwargs["allowed_limit"] = getattr(meta, "limit", 20)
        
        new_class.add_to_class("desc", ResourceDescription(**desc_kwargs))
        
        #Add class attributes to new class
        for name, value in attributes.items():
            new_class.add_to_class(name, value)
        
        #Add parent fields to new class.
        #Note that currently we do not add any other
        #parent attributes.
        for parent in parents:
            if parent.desc.abstract:
                for field in parent.desc.fields:
                    new_class.desc.add_field(field)
        
        #Add defaults if subclassed versions not provided
        if new_class.desc.manager is None:
            new_class.add_to_class("objects",  ResourceManager())
        if new_class.desc.authenticator is None:
            new_class.add_to_class("authenticator", ResourceAuthenticator())
        if new_class.desc.authorizer is None:
            new_class.add_to_class("authorizer", ResourceAuthorizer())
        if new_class.desc.sanitizer is None:
            new_class.add_to_class("sanitizer", ResourceSanitizer())
        if new_class.desc.serializer is None:
            new_class.add_to_class("serializer", ResourceSerializer())
        
        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, "contribute_to_class"):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

class ResourceBase(object):
    __metaclass__ = ResourceMeta

    def __init__(self, **kwargs):
        for field in self.desc.fields:
            if field.attname in kwargs:
                value = kwargs.pop(field.attname)
                setattr(self, field.attname, value)
            elif field.name in kwargs:
                value = kwargs.pop(field.name)
                setattr(self, field.name, value)
            else:
                if field.has_default():
                    setattr(self, field.attname, field.get_default())
        
        if kwargs:
            raise TypeError("'%s' is an invalid argument" % kwargs.keys()[0])

    def contribute_to_class(self, resource_class, name):
        #Invoked for nested resources
        setattr(resource_class, name, self)
        resource_class.desc.add_subresource(self)
        self.desc.parent_resource_class = resource_class

    def primary_key_name(self):
        return self.desc.primary_key

    def primary_key_value(self):
        return getattr(self, self.primary_key_name())
    
    def save(self):
        manager = self.desc.manager
        if self.primary_key_value():
            manager.update(resource=self)
        else:
            manager.create(resource=self)


from schema import SchemaResourceBase, SchemaResourceManager
class SchemaMeta(ResourceMeta):
    def __new__(cls, name, bases, attributes):
        new_class = super(SchemaMeta, cls).__new__(cls, name, bases, attributes)
        schema_class_attributes = {
            "__module__": SchemaResourceBase.__module__,
            "objects": SchemaResourceManager()
        }

        schema_class = type(
                name+"Schema",
                (SchemaResourceBase,),
                schema_class_attributes)

        new_class.add_to_class("schema", schema_class())
        return new_class


class Resource(ResourceBase):
    __metaclass__ = SchemaMeta
