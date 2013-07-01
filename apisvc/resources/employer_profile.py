from trsvcscore.db.models import EmployerProfile
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import UserAuthorizer
from resources.user import UserResource

class EmployerProfileResource(Resource):
    class Meta:
        resource_name = "employer_profiles"
        model_class = EmployerProfile
        methods = ["GET", "PUT"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "user__id": ["eq"]
        }    
        ordering = []
        limit = 20

    id = fields.EncodedField(primary_key=True)
    user_id = fields.EncodedField()

    user = fields.EncodedOneToOne(UserResource, backref="employer_profile", model_name="user", model_attname="user_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['user', 'user_id'], ['GET'])
