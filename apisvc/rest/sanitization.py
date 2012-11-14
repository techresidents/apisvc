class ResourceSanitizer(object):
    def __init__(self):
        self.resource_class = None
    
    def contribute_to_class(self, resource_class, name):
        resource_class.desc.sanitizer = self
        setattr(resource_class, name, self)
        self.resource_class = resource_class

    def sanitize_resources(self, context, resources):
        pass

    def desanitize_resources(self, context, resources):
        pass
