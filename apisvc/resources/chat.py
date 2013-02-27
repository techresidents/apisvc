from trpycore.timezone import tz
from trsvcscore.db.enum import Enum
from trsvcscore.db.models import Chat, ChatType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.topic import TopicResource

class ChatTypeEnum(Enum):
    model_class = ChatType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class ChatManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        super(ChatManager, self).__init__(*args, **kwargs)

    def build_all_query(self, **kwargs):
        kwargs["end__lt"] = tz.utcnow()
        return super(ChatManager, self).build_all_query(**kwargs) 

class ChatResource(Resource):
    class Meta:
        resource_name = "chats"
        model_class = Chat
        methods = ["GET"]
        bulk_methods = ["GET"]
        related_methods = {
            "topic": ["GET"],
        }
        filtering = {
            "id": ["eq"],
            "type": ["eq"],
            "start": ["eq", "lt", "lte", "gt", "gte"],
            "end": ["eq", "lt", "lte", "gt", "gte"],
            r"chat_sessions\+__id": ["eq"],
        }    
        with_relations = ["topic"]

    id = fields.EncodedField(primary_key=True)
    type = EnumField(ChatTypeEnum, model_attname="type_id")
    topic_id = fields.EncodedField()
    start = fields.DateTimeField()
    end = fields.DateTimeField()
    registration_start = fields.DateTimeField(nullable=True)
    registration_end = fields.DateTimeField(nullable=True)
    checkin_start = fields.DateTimeField(nullable=True)
    checkin_end = fields.DateTimeField(nullable=True)

    topic = fields.EncodedForeignKey(TopicResource, backref="chats")

    objects = ChatManager(db_session_factory)
    authenticator = SessionAuthenticator()
