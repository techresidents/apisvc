from sqlalchemy.orm import joinedload

from trsvcscore.db.models import ChatSession, ChatUser, Chat
from factory.db import db_session_factory
from rest.alchemy.manager import AlchemyResourceManager
from rest.authorization import PerUserResourceAuthorizer
from rest.fields import StringField, ManyToMany, ForeignKey, DateTimeField, EncodedField, EncodedForeignKey
from rest.resource import Resource
from resources.common import TopicResource
from resources.django import UserResource

class ChatResource(Resource):
    class Meta:
        resource_name = "chat"
        model_class = Chat
        methods = ["GET"]
        related_methods = {
            "topic": ["GET"],
        }
        filtering = {
            "id": ["eq"],
            r"chat_sessions\+__id": ["eq"],
        }    
    id = EncodedField(primary_key=True)
    topic = ForeignKey(TopicResource, backref="chats")
    start = DateTimeField()

    objects = AlchemyResourceManager(db_session_factory)

class ChatSessionResource(Resource):
    class Meta:
        resource_name = "chat_sessions"
        model_class = ChatSession
        methods = ["GET", "PUT", "POST", "DELETE"]
        bulk_methods = ["GET", "POST"]
        related_methods = {
            "users": ["GET"],
            "chatTest": ["GET"]
        }
        related_bulk_methods = {
            "users": ["GET"],
        }

        filtering = {
            "id": ["eq"],
            "users__id": ["eq"],
            "chatTest__id": ["eq"],
            "tokenTest": ["eq"],
        }    
        with_relations = ["chatTest", "users"]
        ordering = ["id", "tokenTest", "chatTest__id"]
        limit = 20

        alchemy_query_options = [joinedload(ChatSession.chat)]

    id = EncodedField(primary_key=True)
    tokenTest = StringField(model_attname="chat.id", readonly=True, model_class=Chat, through=Chat)
    users = ManyToMany(UserResource, through=ChatUser, backref="chat_sessions")
    chatTest = EncodedForeignKey(ChatResource, backref="chat_sessions+", model_name="chat", model_attname="chat_id")

    objects = AlchemyResourceManager(db_session_factory)
    authorizer = PerUserResourceAuthorizer(UserResource, "users__id")
