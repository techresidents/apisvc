from trsvcscore.db.models import JobTechnologyPref
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import UserAuthorizer
from resources.user import UserResource
from resources.technology import TechnologyResource

class TechnologyPreferenceResource(Resource):
    class Meta:
        resource_name = "technology_prefs"
        model_class = JobTechnologyPref
        methods = ["GET", "PUT", "POST", "DELETE"]
        bulk_methods = ["GET"]

        filtering = {
            "id": ["eq"],
            "user__id": ["eq"]
        }    
        with_relations = [
            '^technology$'
        ]
        ordering = ["id"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    user_id = fields.EncodedField()
    technology_id = fields.IntegerField()

    user = fields.EncodedForeignKey(UserResource, backref="technology_prefs", model_name="user", model_attname="user_id")
    technology = fields.ForeignKey(TechnologyResource, backref="technology_prefs+", model_name="technology", model_attname="technology_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['user_id'], ['GET'])
