from trsvcscore.db.models import JobApplicationScore
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.user import UserResource
from resources.tenant import TenantResource
from resources.application import ApplicationResource

class ApplicationScoreResource(Resource):
    class Meta:
        resource_name = "application_scores"
        model_class = JobApplicationScore
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
    technical_score = fields.IntegerField()
    communication_score = fields.IntegerField()
    cultural_fit_score = fields.IntegerField()

    tenant = fields.EncodedForeignKey(TenantResource, backref="application_scores+")
    user = fields.EncodedForeignKey(UserResource, backref="application_scores+")
    application = fields.EncodedForeignKey(ApplicationResource, backref="application_scores")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
