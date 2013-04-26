from rest.manager import ResourceManager
from rest.es.query import ElasticSearchQuery

class ElasticSearchManager(ResourceManager):
    def __init__(self, es_client_pool, query_class=None, query_factory=None):
        self.es_client_pool = es_client_pool
        self.query_class = query_class or ElasticSearchQuery

        query_factory = query_factory or \
                (lambda: self.query_class(
                    self.resource_class,
                    self.index_name(),
                    self.doc_name(),
                    self.es_client_pool))

        super(ElasticSearchManager, self).__init__(
            query_factory=query_factory)

    
    def index_name(self):
        return self.resource_class.Meta.index

    def doc_name(self):
        return self.resource_class.Meta.doc

