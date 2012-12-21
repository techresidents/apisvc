from trsvcscore.db.models import ChatHighlightSession
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.authorization import PerUserResourceAuthorizer
from rest.resource import Resource
from resources.user import UserResource
from resources.chat_session import ChatSessionResource

class HighlightSessionResource(Resource):
    class Meta:
        resource_name = "highlight_sessions"
        model_class = ChatHighlightSession
        methods = ["GET", "POST", "PUT", "DELETE"]
        bulk_methods = ["GET", "POST", "PUT", "DELETE"]
        related_methods = {
            "user": ["GET"],
            "chat_session": ["GET"]
        }

        filtering = {
            "id": ["eq"],
            "user__id": ["eq"],
            "chat_session__id": ["eq"]
        }    
        with_relations = ["user", "chat_session"]
        ordering = ["id", "rank"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    user_id = fields.EncodedField()
    chat_session_id = fields.EncodedField()
    rank = fields.IntegerField()

    user = fields.EncodedForeignKey(UserResource, backref="highlight_sessions", model_name="user", model_attname="user_id")
    chat_session = fields.EncodedForeignKey(ChatSessionResource, backref="highlight_sessions+", model_name="chat_session", model_attname="chat_session_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = PerUserResourceAuthorizer(UserResource, "user_id", ["GET"])
