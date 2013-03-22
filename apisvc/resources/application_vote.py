from trsvcscore.db.models import JobApplicationVote
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.user import UserResource
from resources.tenant import TenantResource
from resources.application import ApplicationResource

class ApplicationVoteResource(Resource):
    class Meta:
        resource_name = "application_votes"
        model_class = JobApplicationVote
        methods = ["GET", "POST", "PUT"]
        bulk_methods = ["GET", "POST"]
        filtering = {
            "id": ["eq"],
            "user_id": ["eq"],
            "application__id":["eq"]
        }    
        with_relations = []

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    user_id = fields.EncodedField()
    application_id = fields.EncodedField()
    yes = fields.BooleanField(nullable=True)

    tenant = fields.EncodedForeignKey(TenantResource, backref="application_votes+")
    user = fields.EncodedForeignKey(UserResource, backref="application_votes+")
    application = fields.EncodedForeignKey(ApplicationResource, backref="application_votes")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
