from trsvcscore.db.models import ChatSession, ChatUser
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.authorization import PerUserResourceAuthorizer
from rest.resource import Resource
from resources.user import UserResource
from resources.chat import ChatResource


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
            "archives": ["GET"]
        }

        filtering = {
            "id": ["eq"],
            "end": ["isnull"],
            "users__id": ["eq"],
            "chat__id": ["eq"]
        }    
        with_relations = ["chat", "users"]
        ordering = ["id"]
        limit = 20

    id = fields.EncodedField(primary_key=True)
    chat_id = fields.EncodedField()
    participants = fields.IntegerField()
    start = fields.DateTimeField(nullable=True)
    end = fields.DateTimeField(nullable=True)

    users = fields.ManyToMany(UserResource, through=ChatUser, backref="chat_sessions")
    chat = fields.EncodedForeignKey(ChatResource, backref="chat_sessions+", model_name="chat", model_attname="chat_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = PerUserResourceAuthorizer(UserResource, "users__id")
