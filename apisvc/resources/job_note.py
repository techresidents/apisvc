from trsvcscore.db.models import JobNote
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.user import UserResource
from resources.tenant import TenantResource

class JobNoteResource(Resource):
    class Meta:
        resource_name = "job_notes"
        model_class = JobNote
        methods = ["GET", "POST", "PUT"]
        bulk_methods = ["GET", "POST"]
        filtering = {
            "id": ["eq"],
            "tenant_id": ["eq"],
            "employee_id": ["eq"]
        }    
        with_relations = []

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    employee_id = fields.EncodedField()
    candidate_id = fields.EncodedField()
    note = fields.StringField()

    tenant = fields.EncodedForeignKey(TenantResource, backref="job_notes+")
    employee = fields.EncodedForeignKey(UserResource, backref="job_notes+")
    candidate = fields.EncodedForeignKey(UserResource, backref="job_notes+")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
