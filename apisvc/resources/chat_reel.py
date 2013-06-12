from trsvcscore.db.models import ChatReel
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import UserAuthorizer
from resources.user import UserResource
from resources.chat import ChatResource

class ChatReelManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        super(ChatReelManager, self).__init__(*args, **kwargs)

    def build_all_query(self, **kwargs):
        if "order_by" not in kwargs:
            kwargs["order_by"] = "rank"
        return super(ChatReelManager, self).build_all_query(**kwargs) 

class ChatReelResource(Resource):
    class Meta:
        resource_name = "chat_reels"
        model_class = ChatReel
        methods = ["GET", "POST", "PUT", "DELETE"]
        bulk_methods = ["GET"]
        related_methods = {
            "user": ["GET"],
            "chat": ["GET"]
        }

        filtering = {
            "id": ["eq"],
            "user_id": ["eq"],
            "user__id": ["eq"],
            "chat__id": ["eq"]
        }    
        with_relations = ["user", "chat__topic"]
        ordering = ["id", "rank"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    user_id = fields.EncodedField()
    chat_id = fields.EncodedField()
    rank = fields.IntegerField()

    user = fields.EncodedForeignKey(UserResource, backref="chat_reels", model_name="user", model_attname="user_id")
    chat = fields.EncodedForeignKey(ChatResource, backref="chat_reels+", model_name="chat", model_attname="chat_id")

    objects = ChatReelManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['user', 'user_id'], ["GET"])
