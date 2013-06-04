import uuid

from sqlalchemy.exc import IntegrityError

from trpycore.timezone import tz
from trsvcscore.db.models import Chat, ChatParticipant
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.alchemy.query import AlchemyQuery
from rest.authentication import SessionAuthenticator
from rest.exceptions import InvalidQuery
from rest.resource import Resource
from resources.topic import TopicResource
from resources.user import UserResource

class ChatManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        kwargs["query_class"] = ChatQuery
        super(ChatManager, self).__init__(*args, **kwargs)

    def build_all_query(self, **kwargs):
        kwargs["end__lt"] = tz.utcnow()
        if "order_by" not in kwargs:
            kwargs["order_by"] = "id__desc"
        return super(ChatManager, self).build_all_query(**kwargs) 


class ChatQuery(AlchemyQuery):
    def __init__(self, resource_class, transaction_factory):
        super(ChatQuery, self).__init__(resource_class, transaction_factory)
        self.max_participants = 2

    def create(self, **kwargs):
        if not self.empty():
            raise InvalidQuery("create query must be empty")

        resource = kwargs.pop("resource", None)
        if resource is None:
            resource = self.resource_class(**kwargs)

        if resource.max_participants > self.max_participants:
            msg = "max participants may not exceed %s" % self.max_participants
            raise InvalidQuery(message=msg,
                    developer_message=msg,
                    user_message=msg)
        
        try:
            with self.transaction_factory() as db_session:
                model = self.resource_to_model(resource)
                model.token = uuid.uuid4().hex
                db_session.add(model)
                db_session.flush()
                return self.model_to_resource(model, resource)
        except IntegrityError as error:
            raise InvalidQuery("invalid create query: %s" % str(error))


class ChatResource(Resource):
    class Meta:
        resource_name = "chats"
        model_class = Chat
        methods = ["GET", "POST"]
        bulk_methods = ["GET"]
        related_methods = {
            "topic": ["GET"],
            "users": ["GET"],
            "chat_credential": ["POST"],
            "archives": ["GET"],
            "chat_participants": ["GET"],
        }
        related_bulk_methods = {
            "users": ["GET"],
            "chat_participants": ["GET"],
            "archives": ["GET"],
        }
        filtering = {
            "id": ["eq"],
            "start": ["eq", "lt", "lte", "gt", "gte"],
            "end": ["eq", "lt", "lte", "gt", "gte"],
            "users__id": ["eq"],
            "topic__id": ["eq"],
            "topic__title": ["eq", "in", "istartswith"],
        }    
        with_relations = [
            r"^archives$",
            r"^topic?(__tree)?$",
            r"^users$",
            r"^chat_participants$"
            ]
        ordering = ["id", "start"]

    id = fields.EncodedField(primary_key=True)
    topic_id = fields.EncodedField()
    start = fields.DateTimeField(nullable=True)
    end = fields.DateTimeField(nullable=True)
    max_participants = fields.IntegerField()
    no_participants = fields.IntegerField(nullable=True, readonly=True)

    topic = fields.EncodedForeignKey(TopicResource, backref="chats")
    users = fields.ManyToMany(UserResource, through=ChatParticipant, backref="chats")

    objects = ChatManager(db_session_factory)
    authenticator = SessionAuthenticator()
