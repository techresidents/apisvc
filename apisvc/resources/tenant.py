from trsvcscore.db.models import Tenant
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource

class TenantResource(Resource):
    class Meta:
        resource_name = "tenants"
        model_class = Tenant
        methods = ["GET"]
        related_methods = {
            "users": ["GET"],
            "applications": ["GET"],
            "requisitions": ["GET"],
            "job_notes": ["GET"],
            "job_offers": ["GET"],
            "interview_offers": ["GET"],
            "company_profile": ["GET"]

        }
        related_bulk_methods = {
            "users": ["GET"],
            "applications": ["GET"],
            "requisitions": ["GET"],
            "job_notes": ["GET"],
            "job_offers": ["GET"],
            "interview_offers": ["GET"]
        }
        filtering = {
            "id": ["eq"],
            "users__id": ["eq"]
        }
        with_relations = [
            r"^company_profile$"
            ]
        ordering = []
        limit = 20
    
    id = fields.EncodedField(primary_key=True)
    name = fields.StringField()
    domain = fields.StringField(readonly=True)

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
