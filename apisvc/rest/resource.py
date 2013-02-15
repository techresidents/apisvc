from rest.fields import Field, BooleanField, IntegerField, \
        ListField, StringField, StructField, UriField, \
        RelatedField, ForeignKey
from rest.struct import Struct

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
        self.resource_collection_class = None

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

        if isinstance(field, RelatedField):
            self.related_fields.append(field)
            self.related_fields_by_name[field.name] = field
        else:
            self.fields.append(field)
            self.fields_by_name[field.attname] = field


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
        for key, value in attributes.items():
            new_class.add_to_class(key, value)
        
        #Add parent fields to new class.
        #Note that currently we do not add any other
        #parent attributes.
        for parent in parents:
            if parent.desc.abstract:
                for field in parent.desc.fields:
                    new_class.desc.add_field(field)

        
        #Add defaults if subclassed versions not provided
        if new_class.desc.manager is None:
            from rest.manager import ResourceManager
            new_class.add_to_class("objects",  ResourceManager())
        if new_class.desc.authenticator is None:
            from rest.authentication import ResourceAuthenticator
            new_class.add_to_class("authenticator", ResourceAuthenticator())
        if new_class.desc.authorizer is None:
            from rest.authorization import ResourceAuthorizer
            new_class.add_to_class("authorizer", ResourceAuthorizer())
        if new_class.desc.sanitizer is None:
            from rest.sanitization import ResourceSanitizer
            new_class.add_to_class("sanitizer", ResourceSanitizer())
        if new_class.desc.serializer is None:
            from rest.serialization import ResourceSerializer
            new_class.add_to_class("serializer", ResourceSerializer())
        
        #Add collection if subclassed version does not exist
        if new_class.desc.resource_collection_class is None:
            #dynamically create ResourceCollectionBase subclass
            resource_collection_class_attributes = {
                "__module__": ResourceCollection.__module__
            }
            
            resource_collection_class = type(
                    name+"Collection",
                    (ResourceCollection,),
                    resource_collection_class_attributes)

            new_class.add_to_class("Collection", resource_collection_class)
        
        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, "contribute_to_class"):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ResourceCollection(object):
    @classmethod
    def contribute_to_class(cls, resource_class, name):
        cls.resource_class = resource_class
        resource_class.desc.resource_collection_class = cls
        setattr(resource_class, name, cls)

    def __init__(self, resources=None):
        self.total_count = 0
        self.collection = list(resources) if resources else []
    
    def __iter__(self):
        return iter(self.collection)

    def __len__(self):
        return len(self.collection)

    def append(self, resource):
        self.collection.append(resource)
    
    def extend(self, resources):
        self.collection.extend(resources)
    
    def read(self, formatter, resource_uri=None):
        formatter.read_struct_begin()
        while True:
            field_name = formatter.read_field_begin()
            if field_name == Field.STOP:
                break
            elif field_name == "meta":
                ResourceMetaStruct().read(formatter)
            elif field_name == "results":
                length = formatter.read_list_begin()
                for i in range(length):
                    resource = self.resource_class()
                    resource.read(formatter)
                    self.append(resource)
                formatter.read_list_end()
            else:
                raise RuntimeError("read invalid field: %s" % field_name)
            formatter.read_field_end()
        formatter.read_struct_end()

    def write(self, formatter, resource_uri=None):
        resource_uri = resource_uri or "/%s" % self.resource_class.desc.resource_name

        formatter.write_struct_begin()
        formatter.write_field_begin("meta", StructField)
        ResourceMetaStruct(
            resource_name=self.resource_class.desc.resource_name,
            resource_uri=resource_uri,
            loaded=True,
            many=True,
            total_count=self.total_count
        ).write(formatter)
        formatter.write_field_end()
        formatter.write_field_begin("results", ListField)
        formatter.write_list_begin(len(self))
        for resource in self:
            resource.write(formatter)
        formatter.write_list_end()
        formatter.write_field_end()
        formatter.write_struct_end()


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
        primary_key_name = self.primary_key_name()
        if primary_key_name:
            return getattr(self, primary_key_name)
        else:
            return None
    
    def uri(self):
        manager = self.desc.manager
        return manager.uri(self)
        
    def save(self):
        manager = self.desc.manager
        if self.primary_key_value():
            manager.update(resource=self)
        else:
            manager.create(resource=self)
    
    def read(self, formatter, resource_uri=None):
        fields_read = 0
        formatter.read_struct_begin()
        while True:
            field_name = formatter.read_field_begin()
            if field_name == Field.STOP:
                break
            elif field_name == "meta":
                ResourceMetaStruct().read(formatter)
            elif field_name in self.desc.fields_by_name:
                field = self.desc.fields_by_name[field_name]
                field_value = field.read(formatter)
                fields_read += 1
                setattr(self, field_name, field_value)
            elif field_name in self.desc.related_fields_by_name:
                fields_read += 1
                field = self.desc.related_fields_by_name[field_name]
                if field.many:
                    resources = field.relation.Collection()
                    resources.read(formatter)
                    if len(resources):
                        setattr(self, field_name, resources)
                else:
                    resource = field.relation()
                    if resource.read(formatter):
                        setattr(self, field_name, resource)
            else:
                raise RuntimeError("read invalid field: %s" % field_name)
            field_name = formatter.read_field_end()
        formatter.read_struct_end()
        return fields_read

    def write(self, formatter, resource_uri=None):
        resource_uri = resource_uri or self.uri()

        write_fields = lambda fields: [f for f in fields if not f.hidden]

        formatter.write_struct_begin()
       
        formatter.write_field_begin("meta", StructField)        
        ResourceMetaStruct(
                resource_name=self.desc.resource_name,
                resource_uri=resource_uri,
                loaded=True,
                many=False,
                total_count=1
                ).write(formatter)
        formatter.write_field_end()
        
        for field in write_fields(self.desc.fields):
            formatter.write_field_begin(field.attname, field)
            field.write(formatter, getattr(self, field.attname))
            formatter.write_field_end()

        for field in write_fields(self.desc.related_fields):
            related_descriptor = getattr(self.__class__, field.name)

            if related_descriptor.is_loaded(self):
                resources = getattr(self, field.name)
                formatter.write_field_begin(field.name, field)
                if field.many:
                    resources.write(
                            formatter,
                            "%s/%s" % (resource_uri, field.name))
                else:
                    resources.write(formatter)
                formatter.write_field_end()
            else:
                if isinstance(field, ForeignKey):
                    fk = getattr(self, field.attname)
                    if fk is None:
                        link = None
                    else:
                        link = "/%s/%s" % (field.relation.desc.resource_name, fk)
                else:
                    link = "%s/%s" % (resource_uri, field.name)
                
                formatter.write_field_begin(field.name, field)
                formatter.write_struct_begin()
                formatter.write_field_begin("meta", StructField)
                ResourceMetaStruct(
                        resource_name=field.relation.desc.resource_name,
                        resource_uri=link,
                        loaded=False,
                        many=field.many,
                        total_count=None if field.many else 1
                        ).write(formatter)
                formatter.write_field_end()
                formatter.write_struct_end()
                formatter.write_field_end()
        
        formatter.write_field_stop()
        formatter.write_struct_end()


from schema import SchemaResourceBase, SchemaResourceManager
class SchemaMeta(ResourceMeta):
    def __new__(cls, name, bases, attributes):
        new_class = super(SchemaMeta, cls).__new__(cls, name, bases, attributes)

        #dynamically create SchemaResourceBase sublcass
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

class ResourceMetaStruct(Struct):
    resource_name = StringField()
    resource_uri = UriField(nullable=True)
    loaded = BooleanField()
    many = BooleanField()
    total_count = IntegerField(nullable=True)
