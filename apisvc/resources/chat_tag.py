from sqlalchemy.orm import joinedload

from trsvcscore.db.models import ChatTag
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.chat_minute import ChatMinuteResource
from resources.chat_session import ChatSessionResource
from resources.user import UserResource

class ChatTagResource(Resource):
    class Meta:
        resource_name = "chat_tags"
        model_class = ChatTag
        alchemy_query_options = [joinedload(ChatTag.chat_minute)]
        methods = ["GET"]
        bulk_methods = ["GET"]

        filtering = {
            "id": ["eq"],
            "public": ["eq"],
            "chat_minute__id": ["eq"],
            "chat_session__id": ["eq"]
        }    

        ordering = ["id", "start"]

        limit = 20

    id = fields.IntegerField(primary_key=True)
    user_id = fields.EncodedField()
    chat_minute_id = fields.IntegerField()
    chat_session_id = fields.EncodedField(model_attname='chat_minute.chat_session_id', readonly=True)
    time = fields.DateTimeField()
    name = fields.StringField()

    user = fields.EncodedForeignKey(UserResource, backref="chat_tags+", model_name="user", model_attname="user_id")
    chat_minute = fields.ForeignKey(ChatMinuteResource, backref="chat_tags", model_name="chat_minute", model_attname="chat_minute_id")
    chat_session = fields.EncodedForeignKey(ChatSessionResource, through="chat_minute", backref="chat_tags", model_name="chat_minute.chat_session", model_attname="chat_minute.chat_session_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
