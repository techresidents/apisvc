from trsvcscore.db.models import SpotlightChat
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.chat import ChatResource

class SpotlightChatManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        super(SpotlightChatManager, self).__init__(*args, **kwargs)

    def build_all_query(self, **kwargs):
        if "order_by" not in kwargs:
            kwargs["order_by"] = "rank"
        return super(SpotlightChatManager, self).build_all_query(**kwargs) 

class SpotlightChatResource(Resource):
    class Meta:
        resource_name = "spotlight_chats"
        model_class = SpotlightChat
        methods = ["GET"]
        bulk_methods = ["GET"]
        related_methods = {
            "chat": ["GET"]
        }

        filtering = {
            "id": ["eq"],
            "chat__id": ["eq"]
        }    
        with_relations = ["chat__topic"]
        ordering = ["id", "rank"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    chat_id = fields.EncodedField()
    rank = fields.IntegerField()

    chat = fields.EncodedForeignKey(ChatResource, backref="spotlight_chats+", model_name="chat", model_attname="chat_id")

    objects = SpotlightChatManager(db_session_factory)
    authenticator = SessionAuthenticator()
