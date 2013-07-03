from trsvcscore.db.models import JobLocationPref
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import UserAuthorizer
from resources.user import UserResource
from resources.location import LocationResource

class LocationPreferenceResource(Resource):
    class Meta:
        resource_name = "location_prefs"
        model_class = JobLocationPref
        methods = ["GET", "POST", "PUT", "DELETE"]
        bulk_methods = ["GET"]

        filtering = {
            "id": ["eq"],
            "user__id": ["eq"]
        }    
        with_relations = [
            '^location$'
        ]
        ordering = ["id"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    user_id = fields.EncodedField()
    location_id = fields.IntegerField()

    user = fields.EncodedForeignKey(UserResource, backref="location_prefs", model_name="user", model_attname="user_id")
    location = fields.ForeignKey(LocationResource, backref="location_prefs+", model_name="location", model_attname="location_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['user_id'], ['GET'])
