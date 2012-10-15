class RequestContext(object):
    def __init__(self,
            api=None,
            session=None,
            user_id=None,
            resource_manager=None,
            resource_class=None,
            related_field=None,
            method=None,
            request=None,
            data=None,
            bulk=False,
            query=None):
        self.api = api
        self.session = session
        self.user_id = user_id
        self.resource_manager = resource_manager
        self.resource_class = resource_class
        self.related_field = related_field
        self.method = method
        self.request = request
        self.data = data
        self.bulk = bulk 
        self.query = query
    
    def is_direct_resource(self):
        return self.resource_class == self.resource_manager.resource_class

    def is_related_resource(self):
        if not self.is_direct_resource() and \
                self.related_field and \
                self.related_field.relation is self.resource_class:
            return True
        else:
            return False
    
    def is_nested_resource(self):
        if not self.is_direct_resource() and not self.is_related_resource():
            return True
        else:
            return False
