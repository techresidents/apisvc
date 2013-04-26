import StringIO
from rest.format.factory import FormatterFactory

def serialize(api, obj, format, formatter_factory=FormatterFactory()):
    buffer = StringIO.StringIO()
    formatter = formatter_factory.create(format, buffer, api)
    obj.write(formatter)
    return buffer.getvalue()

def deserialize(self, api, obj, format, data):
    buffer = StringIO.StringIO(data)
    formatter = self.formatter_factory.create(format, buffer, api)
    obj.read(formatter)
    return obj


class ResourceSerializer(object):
    def __init__(self, formatter_factory=FormatterFactory()):
        self.formatter_factory = formatter_factory

    def contribute_to_class(self, resource_class, name):
        resource_class.desc.serializer = self
        setattr(resource_class, name, self)
        self.resource_class = resource_class

    def serialize(self, api, resource_uri, resource, format):
        buffer = StringIO.StringIO()
        formatter = self.formatter_factory.create(format, buffer, api)
        resource.write(formatter, resource_uri)
        return buffer.getvalue()
    
    def deserialize(self, api, resource_uri, resource, format, data):
        buffer = StringIO.StringIO(data)
        formatter = self.formatter_factory.create(format, buffer, api)
        resource.read(formatter, resource_uri)
        return resource
