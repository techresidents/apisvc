from trsvcscore.db.models import TopicTag
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.topic import TopicResource
from resources.tag import TagResource

class TopicTagResource(Resource):
    class Meta:
        resource_name = "topic_tags"
        model_class = TopicTag
        methods = ["GET"]
        bulk_methods = ["GET"]
        related_methods = {
            "topic": ["GET"],
            "tag": ["GET"]
        }

        filtering = {
            "id": ["eq"]
        }    
        with_relations = [
            "^topic$",
            "^tag$"
        ]
        ordering = ["id"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    topic_id = fields.EncodedField()
    tag_id = fields.IntegerField()

    topic = fields.EncodedForeignKey(TopicResource, backref="topic_tags", model_name="topic", model_attname="topic_id")
    tag = fields.EncodedForeignKey(TagResource, backref="topic_tags+", model_name="tag", model_attname="tag_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
