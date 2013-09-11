import logging

from factory.session import session_store_pool
from rest.authorization import ContextAuthorizer, MacroAuthorizer, FilterAuthorizer
from rest.exceptions import AuthenticationError
from rest.middleware.base import RestMiddleware
from rest.response import ExceptionResponse

class SessionAuthenticationMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        response = None

        with session_store_pool.get() as session_store:
            session = session_store.get_session(request.cookie("sessionid"))
            if session:
                context.session = session
                context.user_id = session.user_id()
                context.tenant_id = session.tenant_id()
            else:
                context.session = None
                context.user_id = None
                context.tenant_id = None
        try:
            authenticator = context.resource_class.desc.authenticator
            authenticator.authenticate_request(context, request, **kwargs)
        except AuthenticationError as error:
            logging.warning(repr(error))
            response = ExceptionResponse(error)
        except Exception as error:
            logging.exception(error)
            return ExceptionResponse(AuthenticationError(str(error)))
        
        return response

    def process_response(self, context, response, **kwargs):
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return exception

class UserAuthorizer(FilterAuthorizer):
    def __init__(self, user_filters, exclude_methods=None):
        super(UserAuthorizer, self).__init__(
                filters=user_filters,
                context_attribute='user_id',
                exclude_methods=exclude_methods)

class TenantAuthorizer(FilterAuthorizer):
    def __init__(self, tenant_filters, exclude_methods=None):
        super(TenantAuthorizer, self).__init__(
                filters=tenant_filters,
                context_attribute='tenant_id',
                exclude_methods=exclude_methods)

class TenantUserAuthorizer(MacroAuthorizer):
    def __init__(self, tenant_field_name, user_field_name):
        self.tenant_authorizer = TenantAuthorizer(tenant_field_name)
        self.user_authorizer = UserAuthorizer(user_field_name)
        super(TenantUserAuthorizer, self).__init__([
            self.tenant_authorizer,
            self.user_authorizer
        ])

class DeveloperEmployerAuthorizer(ContextAuthorizer):
    def __init__(self, developer_authorizer, employer_authorizer):
        super(DeveloperEmployerAuthorizer, self).__init__()
        self.developer_authorizer = developer_authorizer
        self.employer_authorizer = employer_authorizer
    
    def _get_authorizer(self, context):
        result = self.developer_authorizer
        if context.user_id and context.tenant_id > 1:
            result = self.employer_authorizer
        return result

    def contribute_to_class(self, resource_class, name):
        self.developer_authorizer.contribute_to_class(resource_class, name)
        self.employer_authorizer.contribute_to_class(resource_class, name)
        super(DeveloperEmployerAuthorizer, self).contribute_to_class(resource_class, name)
