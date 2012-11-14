from rest.alchemy.transaction import AlchemyTransaction
from rest.alchemy.query import AlchemyQuery
from rest.manager import ResourceManager

class AlchemyResourceManager(ResourceManager):
    def __init__(self,
            db_session_factory,
            query_class=None,
            transaction_factory=None,
            query_factory=None):
        self.db_session_factory = db_session_factory
        self.query_class = query_class or AlchemyQuery

        transaction_factory = transaction_factory or \
                (lambda: AlchemyTransaction(self.db_session_factory))

        query_factory = query_factory or \
                (lambda: self.query_class(
                self.resource_class,
                self.transaction_factory))

        super(AlchemyResourceManager, self).__init__(
                query_factory = query_factory,
                transaction_factory = transaction_factory)
