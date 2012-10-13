import StringIO
from rest.format.factory import FormatterFactory

class ResourceSerializer(object):
    def __init__(self, formatter_factory=FormatterFactory()):
        self.formatter_factory = formatter_factory

    def contribute_to_class(self, resource_class, name):
        resource_class.desc.serializer = self
        setattr(resource_class, name, self)
        self.resource_class = resource_class

    def serialize(self, api, resource, format):
        buffer = StringIO.StringIO()
        formatter = self.formatter_factory.create(format, buffer)
        formatter.write(api, resource)
        return buffer.getvalue()
    
    def deserialize(self, api, data, format, result):
        buffer = StringIO.StringIO(data)
        formatter = self.formatter_factory.create(format, buffer)
        resource = formatter.read(api, result)
        return resource
