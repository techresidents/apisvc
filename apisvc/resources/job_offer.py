from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobOffer, JobOfferStatus
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import TenantAuthorizer
from resources.tenant import TenantResource
from resources.user import UserResource
from resources.application import ApplicationResource

class JobOfferStatusEnum(Enum):
    model_class = JobOfferStatus
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class JobOfferResource(Resource):
    class Meta:
        resource_name = "job_offers"
        model_class = JobOffer
        methods = ["GET", "POST", "PUT"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"]
        }    
        with_relations = []

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    candidate_id = fields.EncodedField()
    employee_id = fields.EncodedField()
    application_id = fields.EncodedField()
    status = EnumField(JobOfferStatusEnum, model_attname="status_id")
    salary = fields.IntegerField()

    tenant = fields.EncodedForeignKey(TenantResource, backref="job_offers")
    candidate = fields.EncodedForeignKey(UserResource, backref="job_offers")
    employee = fields.EncodedForeignKey(UserResource, backref="job_offers+")
    application = fields.ForeignKey(ApplicationResource, backref="job_offers")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = TenantAuthorizer(['tenant', 'tenant_id'])
