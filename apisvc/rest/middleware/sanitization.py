from rest.middleware.base import RestMiddleware
from rest.utils.resource import loaded_resource_map

class SanitizationMiddleware(RestMiddleware):
    def _to_list(self, value):
        if isinstance(value, (list, tuple)):
            return value
        else:
            return [value]

    def process_request(self, context, request, **kwargs):
        if context.data is None:
            return None

        resource_map = loaded_resource_map(context.data)
        for resource_class, resources in resource_map.items():
            sanitizer = resource_class.desc.sanitizer
            sanitizer.desanitize_resources(context, resources)
        return None

    def process_response(self, context, response, **kwargs):
        if not response.successful:
            return response 

        resource_map = loaded_resource_map(response.data)
        for resource_class, resources in resource_map.items():
            sanitizer = resource_class.desc.sanitizer
            sanitizer.sanitize_resources(context, resources)
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return None
