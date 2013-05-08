from rest import fields
from rest.struct import Struct

class Facet(object):
    def contribute_to_class(self, container_class, name):
        self.container_class = container_class
        self.name = name
        container_class.desc.add_facet(self)

class FacetItemStruct(Struct):
    name = fields.StringField()
    enable_filter = fields.StringField()
    disable_filter = fields.StringField()
    count = fields.IntegerField()
    enabled = fields.BooleanField()

class FacetStruct(Struct):
    name = fields.StringField()
    title = fields.StringField()
    filter = fields.StringField()
    items = fields.ListField(fields.StructField(FacetItemStruct))
