from trsvcscore.db.models import TalkingPoint
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.user import UserResource
from resources.topic import TopicResource

class TalkingPointResource(Resource):
    class Meta:
        resource_name = "talking_points"
        model_class = TalkingPoint
        methods = ["GET", "POST", "PUT", "DELETE"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "user_id": ["eq"],
            "topic__id": ["eq"]
        }
        related_methods = {
        }
        related_bulk_methods = {
        }
        with_relations = []
        ordering = ["id"]

    #fields
    id = fields.IntegerField(primary_key=True)
    user_id = fields.EncodedField()
    topic_id = fields.EncodedField()
    rank = fields.IntegerField()
    point = fields.StringField()

    #related fields
    user = fields.EncodedForeignKey(UserResource, backref="talking_points+")
    topic = fields.EncodedForeignKey(TopicResource, backref="talking_points", model_name="topic", model_attname="topic_id")

    #objects
    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
