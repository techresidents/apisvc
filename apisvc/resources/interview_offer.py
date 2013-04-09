from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobInterviewOffer, JobInterviewOfferType, JobInterviewOfferStatus
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import TenantAuthorizer
from resources.user import UserResource
from resources.tenant import TenantResource
from resources.application import ApplicationResource

class InterviewOfferTypeEnum(Enum):
    model_class = JobInterviewOfferType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class InterviewOfferStatusEnum(Enum):
    model_class = JobInterviewOfferStatus
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class InterviewOfferResource(Resource):
    class Meta:
        resource_name = "interview_offers"
        model_class = JobInterviewOffer
        methods = ["GET", "PUT", "POST"]
        bulk_methods = ["GET", "PUT", "POST"]
        filtering = {
            "id": ["eq"],
            "application__id": ["eq"]
        }    
        with_relations = []

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    candidate_id = fields.EncodedField()
    employee_id = fields.EncodedField()
    application_id = fields.EncodedField()
    type= EnumField(InterviewOfferTypeEnum, model_attname="type_id")
    status = EnumField(InterviewOfferStatusEnum, model_attname="status_id")
    expires = fields.DateTimeField()
    created = fields.DateTimeField(nullable=True, readonly=True)

    tenant = fields.EncodedForeignKey(TenantResource, backref="interview_offers+")
    candidate = fields.EncodedForeignKey(UserResource, backref="interview_offers")
    employee = fields.EncodedForeignKey(UserResource, backref="interview_offers+")
    application = fields.EncodedForeignKey(ApplicationResource, backref="interview_offers")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = TenantAuthorizer(['tenant', 'tenant_id'])
