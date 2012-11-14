from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import settings

#Note that max_overflow must be set to -1
#in order to avoid deadlocks in SQLAlchemy's
#QueuePool. QueuePool use's a threading.Lock
#when max_overflow is not set to -1, which
#will result in a deadlock when multiple
#connections are created from a single thread.
engine = create_engine(settings.DATABASE_CONNECTION, pool_size=settings.DATABASE_POOL_SIZE, max_overflow=-1)
db_session_factory = sessionmaker(bind=engine)
