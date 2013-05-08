from trsvcscore.db.models import JobNote
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.authorization import MultiAuthorizer
from rest.resource import Resource
from auth import TenantAuthorizer, TenantUserAuthorizer
from resources.user import UserResource
from resources.tenant import TenantResource

class JobNoteResource(Resource):
    class Meta:
        resource_name = "job_notes"
        model_class = JobNote
        methods = ["GET", "POST", "PUT"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "tenant_id": ["eq"],
            "tenant__id": ["eq"],
            "employee_id": ["eq"],
            "employee__id": ["eq"],
            "candidate_id": ["eq"],
            "candidate__id": ["eq"]
        }    
        related_methods = {
        }
        with_relations = ['candidate']

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    employee_id = fields.EncodedField()
    candidate_id = fields.EncodedField()
    note = fields.StringField()
    modified = fields.DateTimeField(nullable=True, readonly=True)

    tenant = fields.EncodedForeignKey(TenantResource, backref="job_notes")
    employee = fields.EncodedForeignKey(UserResource, backref="job_notes")
    candidate = fields.EncodedForeignKey(UserResource, backref="candidate_job_notes+")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = MultiAuthorizer({
        "GET": TenantAuthorizer(['tenant', 'tenant_id']),
        ("POST", "PUT", "DELETE"): TenantUserAuthorizer(
            ['tenant', 'tenant_id'],
            ['employee', 'employee_id'])
    })
