import gevent.queue

from trpycore import riak_gevent
from trpycore.riak_common.factory import RiakClientFactory
from trsvcscore.session.riak import RiakSessionStorePool

import settings

riak_client_factory = RiakClientFactory(
        host=settings.RIAK_HOST,
        port=settings.RIAK_PORT,
        transport_class=riak_gevent.RiakPbcTransport)

session_store_pool = RiakSessionStorePool(
        riak_client_factory,
        settings.RIAK_SESSION_BUCKET,
        settings.RIAK_SESSION_POOL_SIZE,
        queue_class=gevent.queue.Queue)
