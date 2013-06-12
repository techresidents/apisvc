import settings

from trpycore.zookeeper_gevent.client import GZookeeperClient
zookeeper_client = GZookeeperClient(settings.ZOOKEEPER_HOSTS)
zookeeper_client.start()
