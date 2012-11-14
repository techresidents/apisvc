from trpycore.timezone import tz
from trsvcscore.db.models import ChatSession, ChatUser
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.user import UserResource
from resources.chat import ChatResource

class ChatSessionManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        super(ChatSessionManager, self).__init__(*args, **kwargs)

    def build_all_query(self, **kwargs):
        kwargs["end__lt"] = tz.utcnow()
        return super(ChatSessionManager, self).build_all_query(**kwargs) 

class ChatSessionResource(Resource):
    class Meta:
        resource_name = "chat_sessions"
        model_class = ChatSession
        methods = ["GET"]
        bulk_methods = ["GET"]
        related_methods = {
            "users": ["GET"],
            "chat": ["GET"],
            "archives": ["GET"]
        }
        related_bulk_methods = {
            "users": ["GET"],
            "archives": ["GET"],
            "speaking_markers": ["GET"],
            "chat_tags": ["GET"]
        }

        filtering = {
            "id": ["eq"],
            "start": ["eq", "lt", "lte", "gt", "gte"],
            "end": ["eq", "lt", "lte", "gt", "gte"],
            "users__id": ["eq"]
        }    
        with_relations = [
            r"^archives$",
            r"^chat(__topic)?(__tree)?$",
            r"^users$",
            r"^chat_minutes(__topic)?$",
            r"^speaking_markers$",
            r"^chat_tags$"
            ]
        ordering = ["id"]
        limit = 20

    id = fields.EncodedField(primary_key=True)
    chat_id = fields.EncodedField()
    participants = fields.IntegerField()
    connect = fields.DateTimeField(nullable=True)
    publish = fields.DateTimeField(nullable=True)
    start = fields.DateTimeField(nullable=True)
    end = fields.DateTimeField(nullable=True)

    users = fields.ManyToMany(UserResource, through=ChatUser, backref="chat_sessions")
    chat = fields.EncodedForeignKey(ChatResource, backref="chat_sessions+", model_name="chat", model_attname="chat_id")

    objects = ChatSessionManager(db_session_factory)
    authenticator = SessionAuthenticator()
