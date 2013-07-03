from trsvcscore.db.models import DeveloperProfile
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import UserAuthorizer
from resources.user import UserResource

class DeveloperProfileResource(Resource):
    class Meta:
        resource_name = "developer_profiles"
        model_class = DeveloperProfile
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
    location = fields.StringField(nullable=True)
    developer_since = fields.DateField(nullable=True)

    user = fields.EncodedOneToOne(UserResource, backref="developer_profile", model_name="user", model_attname="user_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['user', 'user_id'], ['GET'])
