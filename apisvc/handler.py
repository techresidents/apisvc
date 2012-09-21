import logging

import gevent.queue

from trpycore import riak_gevent
from trpycore.greenlet.util import join
from trpycore.riak_common.factory import RiakClientFactory
from trsvcscore.mongrel2.decorator import session_required
from trsvcscore.service_gevent.handler.service import GServiceHandler
from trsvcscore.service_gevent.handler.mongrel2 import GMongrel2Handler
from trsvcscore.session.riak import RiakSessionStorePool
from tridlcore.gen.ttypes import RequestContext
from trapisvc.gen import TApiService

import settings

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
                database_connection=settings.DATABASE_CONNECTION)
        
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

    URL_HANDLERS = [
    ]

    def __init__(self, service_handler):
        """ApiMongrel2Handler constructor.

        Args:
            service_handler: ApiServiceHandler object.
        """
        super(ApiMongrel2Handler, self).__init__(
                url_handlers=self.URL_HANDLERS)

        self.service_handler = service_handler
        self.log = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

        self.riak_client_factory = RiakClientFactory(
                host=settings.RIAK_HOST,
                port=settings.RIAK_PORT,
                transport_class=riak_gevent.RiakPbcTransport)

        self.session_store_pool = RiakSessionStorePool(
                self.riak_client_factory,
                settings.RIAK_SESSION_BUCKET,
                settings.RIAK_SESSION_POOL_SIZE,
                queue_class=gevent.queue.Queue)
        
    def _handle_message(self, request, session):
        """Message helper..

        Args:
            request: Mongrel SafeRequest object.
            session: Session object.
        Returns:
            RequestContext object
        """
        request_context = RequestContext(
                userId=session.user_id(),
                sessionId=session.get_key())

        return request_context

    def handle_disconnect(self, request):
        """Mongrel connection disconnect handler."""
        pass
