from rest.exceptions import AuthenticationError

class ResourceAuthenticator(object):
    def __init__(self):
        self.resource_class = None

    def contribute_to_class(self, resource_class, name):
        resource_class.desc.authenticator = self
        setattr(resource_class, name, self)
        self.resource_class = resource_class

    def authenticate_request(self, context, request, **kwargs):
        return

class SessionAuthenticator(ResourceAuthenticator):
    def authenticate_request(self, context, request, **kwargs):
        if context.session is None or context.user_id is None:
            raise AuthenticationError("invalid session")
