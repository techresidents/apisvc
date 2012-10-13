import logging

from rest.exceptions import AuthenticationError
from rest.middleware.base import RestMiddleware

from factory.session import session_store_pool

class SessionAuthenticationMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        with session_store_pool.get() as session_store:
            session = session_store.get_session(request.cookie("sessionid"))
            if session:
                context.session = session
                context.user_id = session.user_id()
            else:
                context.session = None
                context.user_id = None
        try:
            authenticator = context.resource_class.desc.authenticator
            authenticator.authenticate_request(context, request, **kwargs)
        except AuthenticationError:
            raise
        except Exception as error:
            logging.exception(error)
            raise AuthenticationError(str(error))

        return None

    def process_response(self, context, response, **kwargs):
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return None
