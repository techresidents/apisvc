import logging

from rest.exceptions import AuthenticationError, AuthorizationError
from rest.middleware.base import RestMiddleware
from rest.resource import ResourceCollection
from rest.utils.resource import loaded_resource_map
from rest.response import ExceptionResponse

class AuthenticationMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        try:
            if context.is_direct_resource():
                authenticator = context.resource_class.desc.authenticator
                authenticator.authenticate_request(context, request, **kwargs)
            elif context.is_related_resource():
                base_authenticator = context.resource_manager.resource_class.desc.authenticator
                base_authenticator.authenticate_request(context, request, **kwargs)
                related_authenticator = context.resource_class.desc.authenticator
                related_authenticator.authenticate_request(context, request, **kwargs)
            else:
                logging.error("Unknown resource type.")
                return ExceptionResponse(AuthenticationError())
        
        except AuthenticationError as error:
            logging.warning(repr(error))
            return ExceptionResponse(error)

        except Exception as error:
            logging.exception(error)
            return ExceptionResponse(AuthenticationError())

        return None

    def process_response(self, context, response, **kwargs):
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return exception

class AuthorizationMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        response = None
        try:
            if context.is_direct_resource():
                authorizer = context.resource_class.desc.authorizer
                authorizer.authorize_request(context, request, **kwargs)
            elif context.is_related_resource():
                base_authorizer = context.resource_manager.resource_class.desc.authorizer
                base_authorizer.authorize_request(context, request, **kwargs)
                related_authorizer = context.resource_class.desc.authorizer
                related_authorizer.authorize_request(context, request, **kwargs)
            else:
                logging.error("Unknown resource type.")
                response = ExceptionResponse(AuthorizationError())
        
        except AuthorizationError as error:
            logging.warning(repr(error))
            response = ExceptionResponse(error)
        except Exception as error:
            logging.exception(error)
            response = ExceptionResponse(AuthorizationError())
        
        return response

    def process_response(self, context, response, **kwargs):
        if not response.successful:
            return response

        try:
            if context.is_direct_resource():
                authorizer = context.resource_class.desc.authorizer
                authorizer.authorize_response(context, response, **kwargs)
            elif context.is_related_resource():
                base_authorizer = context.resource_manager.resource_class.desc.authorizer
                response = base_authorizer.authorize_response(context, response, **kwargs)
                related_authorizer = context.resource_class.desc.authorizer
                response = related_authorizer.authorize_response(context, response, **kwargs)
            else:
                logging.error("Unknown resource type.")
                response = ExceptionResponse(AuthorizationError())
        
        except AuthorizationError as error:
            logging.warning(repr(error))
            response = ExceptionResponse(error)
        except Exception as error:
            logging.exception(error)
            response = ExceptionResponse(AuthorizationError())

        return response

    def process_exception(self, context, request, exception, **kwargs):
        return exception


class QueryAuthorizationMiddleware(RestMiddleware):
    def _to_list(self, value):
        if isinstance(value, ResourceCollection):
            return value
        else:
            return [value]

    def process_request(self, context, request, **kwargs):
        response = None

        try:
            if context.is_direct_resource():
                authorizer = context.resource_class.desc.authorizer
                context.query = authorizer.authorize_query(context, request, context.query)
            elif context.is_related_resource():
                base_authorizer = context.resource_manager.resource_class.desc.authorizer
                context.query = base_authorizer.authorize_query(context, request, context.query)
                related_authorizer = context.resource_class.desc.authorizer
                context.query = related_authorizer.authorize_query(context, request, context.query)
            else:
                logging.error("Unknown resource type.")
                response = ExceptionResponse(AuthorizationError())

            resource_map = loaded_resource_map(context.data)
            for resource_class, resources in resource_map.items():
                authorizer = resource_class.desc.authorizer
                authorizer.authorize_query_resources(
                        context=context,
                        resources=resources,
                        query=context.query)
        
        except AuthorizationError as error:
            logging.warning(repr(error))
            response = ExceptionResponse(error)
        except Exception as error:
            logging.exception(error)
            response = ExceptionResponse(AuthorizationError())

        return response

    def process_response(self, context, response, **kwargs):
        if not response.successful:
            return response

        try:
            if context.is_direct_resource():
                authorizer = context.resource_class.desc.authorizer
                response = authorizer.authorize_query_response(context, response, context.query)
            elif context.is_related_resource():
                base_authorizer = context.resource_manager.resource_class.desc.authorizer
                response = base_authorizer.authorize_query_response(context, response, context.query)
                related_authorizer = context.resource_class.desc.authorizer
                response = related_authorizer.authorize_query_response(context, response, context.query)
            else:
                logging.error("Unknown resource type.")
                response = ExceptionResponse(AuthorizationError())
            
            resource_map = loaded_resource_map(response.data)
            for resource_class, resources in resource_map.items():
                authorizer = resource_class.desc.authorizer
                authorizer.authorize_query_response_resources(
                        context=context,
                        resources=resources,
                        query=context.query)

        except AuthorizationError as error:
            logging.warning(repr(error))
            response = ExceptionResponse(error)
        except Exception as error:
            logging.exception(error)
            response = ExceptionResponse(AuthorizationError())
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return exception
