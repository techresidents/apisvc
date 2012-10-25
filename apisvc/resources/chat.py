from trsvcscore.db.enum import Enum
from trsvcscore.db.models import Chat, ChatType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.exceptions import ValidationError
from rest.resource import Resource
from resources.topic import TopicResource

class ChatTypeEnum(Enum):
    model_class = ChatType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class ChatTypeField(fields.StringField):
    def to_model(self, value):
        value = super(ChatTypeField, self).to_model(value)
        if value in ChatTypeEnum.VALUES_TO_KEYS:
            pass
        elif value in ChatTypeEnum.KEYS_TO_VALUES:
            value = ChatTypeEnum.KEYS_TO_VALUES[value]
        else:
            raise ValidationError("'%s' invalid type" % value)
        return value

    def to_python(self, value):
        value = super(ChatTypeField, self).to_python(value)
        if value in ChatTypeEnum.KEYS_TO_VALUES:
            pass
        else:
            try:
                value = ChatTypeEnum.VALUES_TO_KEYS[int(value)]
            except:
                raise ValidationError("'%s' invalid type" % value)
        return value

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
            r"chat_sessions\+__id": ["eq"],
        }    
        with_relations = ["topic"]

    id = fields.EncodedField(primary_key=True)
    type = ChatTypeField(model_attname="type_id")
    topic_id = fields.IntegerField()
    start = fields.DateTimeField()
    end = fields.DateTimeField()
    registration_start = fields.DateTimeField(nullable=True)
    registration_end = fields.DateTimeField(nullable=True)
    checkin_start = fields.DateTimeField(nullable=True)
    checkin_end = fields.DateTimeField(nullable=True)

    topic = fields.ForeignKey(TopicResource, backref="chats")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
