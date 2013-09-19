from trsvcscore.db.models import Tag
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource

class TagResource(Resource):
    class Meta:
        resource_name = "tags"
        model_class = Tag
        methods = ["GET"]
        bulk_methods = ["GET"]

        filtering = {
            "id": ["eq"],
            r"topics\+__id": ["eq"]
        }    
        ordering = ["id"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    name = fields.StringField()

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
