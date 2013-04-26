from rest.facet import FacetStruct
from rest.fields import Field, BooleanField, IntegerField, \
        ListField, StringField, StructField, UriField
from rest.struct import Struct

class ResourceCollection(object):
    @classmethod
    def contribute_to_class(cls, resource_class, name):
        cls.resource_class = resource_class
        resource_class.desc.resource_collection_class = cls
        setattr(resource_class, name, cls)

    def __init__(self, resources=None):
        self.total_count = 0
        self.facets = []
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
                ResourceCollectionMetaStruct().read(formatter)
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
        ResourceCollectionMetaStruct(
            resource_name=self.resource_class.desc.resource_name,
            resource_uri=resource_uri,
            loaded=True,
            many=True,
            total_count=self.total_count,
            facets=self.facets
        ).write(formatter)
        formatter.write_field_end()
        formatter.write_field_begin("results", ListField)
        formatter.write_list_begin(len(self))
        for resource in self:
            resource.write(formatter)
        formatter.write_list_end()
        formatter.write_field_end()
        formatter.write_struct_end()

class ResourceCollectionMetaStruct(Struct):
    resource_name = StringField()
    resource_uri = UriField(nullable=True)
    loaded = BooleanField()
    many = BooleanField()
    total_count = IntegerField(nullable=True)
    facets = ListField(StructField(FacetStruct))
