from sqlalchemy.exc import IntegrityError

from trsvcscore.db.models import Chat, ChatParticipant
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.alchemy.query import AlchemyQuery
from rest.authentication import SessionAuthenticator
from rest.exceptions import InvalidQuery
from rest.resource import Resource
from auth import UserAuthorizer
from resources.chat import ChatResource
from resources.user import UserResource

class ChatParticipantManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        kwargs["query_class"] = ChatParticipantQuery
        super(ChatParticipantManager, self).__init__(*args, **kwargs)

    def build_all_query(self, **kwargs):
        if "order_by" not in kwargs:
            kwargs["order_by"] = "participant"
        return super(ChatParticipantManager, self).build_all_query(**kwargs) 


class ChatParticipantQuery(AlchemyQuery):
    def __init__(self, resource_class, transaction_factory):
        super(ChatParticipantQuery, self).__init__(
                resource_class, transaction_factory)

    def create(self, **kwargs):
        if not self.empty():
            raise InvalidQuery("create query must be empty")

        resource = kwargs.pop("resource", None)
        if resource is None:
            resource = self.resource_class(**kwargs)

        try:
            with self.transaction_factory() as db_session:
                model = self.resource_to_model(resource)
                participant = self._increment_no_participants(
                        db_session, model.chat_id)
                if participant is None:
                    msg = "max participants already in chat"
                    raise InvalidQuery(message=msg,
                            developer_message=msg,
                            user_message=msg)
                model.participant = participant
                db_session.add(model)
                db_session.flush()
                return self.model_to_resource(model, resource)
        except IntegrityError as error:
            raise InvalidQuery("invalid create query: %s" % str(error))

    def _increment_no_participants(self, db_session, chat_id):
        """Atomically Increment no_participants count on chat model.

        participants count will only be incremented if doing so if the
        new value will be <= max_participants.

        Returns:
            Incremented participants count if successful, None otherwise.
        """

        chat = Chat.__table__
        update_statement = chat.update() \
                .values(no_participants=chat.c.no_participants+1) \
                .where(chat.c.id==chat_id) \
                .where(chat.c.no_participants < chat.c.max_participants) \
                .returning(chat.c.no_participants)
        row = db_session.execute(update_statement).fetchone()
        if row is None:
            result = None
        else:    
            result = row[0]
        return result


class ChatParticipantResource(Resource):
    class Meta:
        resource_name = "chat_participants"
        model_class = ChatParticipant
        methods = ["GET", "POST"]
        bulk_methods = ["GET"]
        related_methods = {
            "chat": ["GET"],
            "user": ["GET"]
        }
        filtering = {
            "id": ["eq"],
            "chat__id": ["eq"]
        }    
        with_relations = [
            r"^chat$",
            r"^user$",
            ]
        ordering = ["id", "participant"]

    id = fields.IntegerField(primary_key=True)
    chat_id = fields.EncodedField()
    user_id = fields.EncodedField()
    participant = fields.IntegerField(nullable=True, readonly=True)

    chat = fields.EncodedForeignKey(ChatResource, backref="chat_participants")
    user = fields.EncodedForeignKey(UserResource, backref="chat_participants+")

    objects = ChatParticipantManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['user', 'user_id'], ["GET"])
