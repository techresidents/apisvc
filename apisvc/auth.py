import logging

from factory.session import session_store_pool
from rest.exceptions import AuthenticationError
from rest.middleware.base import RestMiddleware
from rest.response import Response


class SessionAuthenticationMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        response = None

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
        except AuthenticationError as error:
            logging.warning(str(error))
            response = Response(data="unauthorized", code=401)
        except Exception as error:
            logging.exception(error)
            response = Response(data="unauthorized", code=401)

        return response

    def process_response(self, context, response, **kwargs):
        return response

    def process_exception(self, context, request, exception, **kwargs):
        return None
