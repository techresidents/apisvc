from tres_gevent.factory import GESClientFactory
from tres_gevent.pool import GESClientPool


import settings

es_client_factory = GESClientFactory(endpoint=settings.ES_ENDPOINT)
es_client_pool = GESClientPool(es_client_factory, settings.ES_POOL_SIZE)
