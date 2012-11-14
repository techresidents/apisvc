from trsvcscore.db.models import ChatMinute
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.chat_session import ChatSessionResource
from resources.topic import TopicResource

class ChatMinuteResource(Resource):
    class Meta:
        resource_name = "chat_minutes"
        model_class = ChatMinute
        methods = ["GET"]
        bulk_methods = ["GET"]

        filtering = {
            "id": ["eq"],
            "chat_session__id": ["eq"]
        }    

        with_relations = [
            r"^topic$"
            ]

        ordering = ["id", "start"]

        limit = 20

    id = fields.IntegerField(primary_key=True)
    chat_session_id = fields.EncodedField()
    topic_id = fields.EncodedField()
    start = fields.DateTimeField()
    end = fields.DateTimeField()

    chat_session = fields.EncodedForeignKey(ChatSessionResource, backref="chat_minutes", model_name="chat_session", model_attname="chat_session_id")
    topic = fields.EncodedForeignKey(TopicResource, model_name="topic", backref="+chat_minutes",  model_attname="topic_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()

