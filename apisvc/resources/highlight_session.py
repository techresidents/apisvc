from trsvcscore.db.models import ChatHighlightSession
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import UserAuthorizer
from resources.user import UserResource
from resources.chat_session import ChatSessionResource

class HighlightSessionManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        super(HighlightSessionManager, self).__init__(*args, **kwargs)

    def build_all_query(self, **kwargs):
        if "order_by" not in kwargs:
            kwargs["order_by"] = "rank"
        return super(HighlightSessionManager, self).build_all_query(**kwargs) 

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
        with_relations = ["user", "chat_session__chat__topic"]
        ordering = ["id", "rank"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    user_id = fields.EncodedField()
    chat_session_id = fields.EncodedField()
    rank = fields.IntegerField()

    user = fields.EncodedForeignKey(UserResource, backref="highlight_sessions", model_name="user", model_attname="user_id")
    chat_session = fields.EncodedForeignKey(ChatSessionResource, backref="highlight_sessions+", model_name="chat_session", model_attname="chat_session_id")

    objects = HighlightSessionManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['user', 'user_id'], ["GET"])
