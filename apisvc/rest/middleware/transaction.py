from rest.middleware.base import RestMiddleware
from rest.transaction import TransactionManager

class TransactionMiddleware(RestMiddleware):
    def process_request(self, context, request, **kwargs):
        tx_manager = TransactionManager()
        tx_manager.clear()
        tx_manager.begin()

    def process_response(self, context, response, **kwargs):
        if response.successful:
            TransactionManager().end()
        else:
            TransactionManager().rollback()
        return response

    def process_exception(self, context, request, exception, **kwargs):
        TransactionManager().rollback()
        return exception
