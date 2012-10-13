import gevent.local

class TransactionManager(object):
    tls = gevent.local.local()
    
    def __init__(self, transaction=None):
        self.transaction = transaction
        if not hasattr(self.tls, "count"):
            self.tls.count = 0
        if not hasattr(self.tls, "transactions"):
            self.tls.transactions = {}
        if not hasattr(self.tls, "rollback"):
            self.tls.rollback = False
    
    def __enter__(self):
        return self.begin()
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None or self.tls.rollback:
            self.end()
        else:
            self.rollback()
    
    def clear(self):
        self.tls.count = 0
        self.tls.transactions = {}
        self.rollback = False

    def begin(self):
        result = None
        if hasattr(self.tls, "count"):
            self.tls.count += 1
        else:
            self.tls.count = 1

        if self.transaction:
            if self.transaction not in self.tls.transactions:
                self.tls.transactions[self.transaction] = self.transaction
                self.transaction.begin()
            result = self.tls.transactions[self.transaction]
        return result
    
    def end(self):
        self.tls.count -= 1
        if self.tls.count == 0:
            for transaction in self.tls.transactions.values():
                transaction.commit()
                transaction.end()
            self.clear()

    def rollback(self):
        self.tls.count -= 1
        if self.tls.count == 0:
            for transaction in self.tls.transactions.values():
                transaction.rollback()
                transaction.end()
            self.clear()
        else:
            self.tls.rollback = True


class Transaction(object):
    def __init__(self):
        self.transaction_manager = TransactionManager(self)
    
    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __hash__(self):
        return self.__class__.__name__.__hash__()

    def __enter__(self):
        return self.transaction_manager.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        self.transaction_manager.__exit__(
                exc_type,
                exc_value,
                traceback)
    
    def begin(self):
        pass

    def commit(self):
        pass
    
    def rollback(self):
        pass

    def end(self):
        pass
