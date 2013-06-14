from trsvcscore.db.models import Location
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource

class LocationResource(Resource):
    class Meta:
        resource_name = "locations"
        model_class = Location
        methods = ["GET"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            r"users\+__id": ["eq"],
            "city": ["eq", "in"]
        }
        limit = 20
        ordering = ["city", "state"]
    
    id = fields.IntegerField(primary_key=True)
    region = fields.StringField()
    country = fields.StringField()
    state = fields.StringField()
    city = fields.StringField(nullable=True)
    county = fields.StringField(nullable=True)
    zip = fields.StringField(nullable=True)

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
