import logging

from trpycore.greenlet.util import join
from trsvcscore.service_gevent.handler.service import GServiceHandler
from trsvcscore.service_gevent.handler.mongrel2 import GMongrel2Handler
from trapisvc.gen import TApiService

import settings
from api import api_v1

class ApiServiceHandler(TApiService.Iface, GServiceHandler):
    """Api service handler."""

    def __init__(self, service):
        """ApiServiceHandler constructor.

        Args:
            service: Service object. Note that this will not be fully initialized
                until start() is called. It may be neccessary delay some handler
                instantiation until then.
        """
        super(ApiServiceHandler, self).__init__(
                service,
                zookeeper_hosts=settings.ZOOKEEPER_HOSTS,
                database_connection=settings.DATABASE_CONNECTION,
                database_connection_pool_size=settings.DATABASE_POOL_SIZE)
        
        self.log = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def start(self):
        """Start handler."""
        super(ApiServiceHandler, self).start()
    
    def stop(self):
        """Stop handler."""
        super(ApiServiceHandler, self).stop()

    def join(self, timeout=None):
        """Join service handler.

        Join the handler, waiting for the completion of all threads 
        or greenlets.

        Args:
            timeout: Optional timeout in seconds to observe before returning.
                If timeout is specified, the status() method must be called
                to determine if the handler is still running.
        """
        greenlets = [
                super(ApiServiceHandler, self)
                ]
        join(greenlets, timeout)
    

class ApiMongrel2Handler(GMongrel2Handler):
    """API mongrel2 handler."""
        
    def __init__(self, service_handler):
        """ApiMongrel2Handler constructor.

        Args:
            service_handler: ApiServiceHandler object.
        """
        super(ApiMongrel2Handler, self).__init__(
                url_handlers=api_v1.get_uris())

        self.service_handler = service_handler
        self.log = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def handle_disconnect(self, request):
        """Mongrel connection disconnect handler."""
        pass
