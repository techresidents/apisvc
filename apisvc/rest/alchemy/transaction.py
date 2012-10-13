from rest.transaction import Transaction

class AlchemyTransaction(Transaction):
    def __init__(self, db_session_factory):
        super(AlchemyTransaction, self).__init__()
        self.db_session_factory  = db_session_factory
        self.session = None

    def __eq__(self, other):
        return self.db_session_factory == other.db_session_factory

    def __hash__(self):
        return id(self.db_session_factory)

    def __enter__(self):
        transaction = self.transaction_manager.__enter__()
        if transaction is not self:
            self.session = transaction.session
        return self.session

    def begin(self):
        if self.session is None:
            self.session = self.db_session_factory()
        else:
            self.session.begin()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
    
    def end(self):
        self.session.close()
