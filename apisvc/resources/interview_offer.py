from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobInterviewOffer, JobInterviewOfferType, JobInterviewOfferStatus
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.exceptions import AuthorizationError
from rest.resource import Resource
from auth import DeveloperEmployerAuthorizer, TenantAuthorizer, UserAuthorizer
from resources.user import UserResource
from resources.tenant import TenantResource
from resources.application import ApplicationResource

class InterviewOfferDeveloperAuthorizer(UserAuthorizer):
    def __init__(self, *args, **kwargs):
        super(InterviewOfferDeveloperAuthorizer, self).__init__(*args, **kwargs)
        self.allowed_methods = ['GET', 'PUT']
    
    def authorize_query(self, context, request, query):
        query = super(InterviewOfferDeveloperAuthorizer, self).authorize_query(
                context, request, query)
        if context.method not in self.allowed_methods:
            raise AuthorizationError('invalid method: %s' % context.method)
        return query

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

class InterviewOfferManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        super(InterviewOfferManager, self).__init__(*args, **kwargs)

    def build_update_query(self, **kwargs):
        #only pending offers can be updated
        kwargs["status"] = InterviewOfferStatusEnum.PENDING
        return super(InterviewOfferManager, self).build_update_query(**kwargs) 
    
class InterviewOfferResource(Resource):
    class Meta:
        resource_name = "interview_offers"
        model_class = JobInterviewOffer
        methods = ["GET", "PUT", "POST"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "tenant__id": ["eq"],
            "candidate_id": ["eq", "in"],
            "candidate__id": ["eq", "in"],
            "status": ["eq", "in"],
            "type": ["eq", "in"],
            "created": ["eq", "range"],
            "expires": ["eq", "range"],
            "application__id": ["eq"],
            "application__requisition__status": ["eq"],
            "application__requisition__title": ["eq", "in", "istartswith"]
        }    
        with_relations = [
                'application',
                'tenant'
        ]
        ordering = [
            "candidate_id",
            "created",
            "expires",
            "status",
            "type",
            "application__requisition__title"
        ]
        limit = 40

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    candidate_id = fields.EncodedField()
    employee_id = fields.EncodedField()
    application_id = fields.EncodedField()
    type= EnumField(InterviewOfferTypeEnum, model_attname="type_id")
    status = EnumField(InterviewOfferStatusEnum, model_attname="status_id")
    expires = fields.DateTimeField()
    created = fields.DateTimeField(nullable=True, readonly=True)

    tenant = fields.EncodedForeignKey(TenantResource, backref="interview_offers")
    candidate = fields.EncodedForeignKey(UserResource, backref="interview_offers")
    employee = fields.EncodedForeignKey(UserResource, backref="interview_offers+")
    application = fields.EncodedForeignKey(ApplicationResource, backref="interview_offers")

    objects = InterviewOfferManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = DeveloperEmployerAuthorizer(
            developer_authorizer=InterviewOfferDeveloperAuthorizer(['candidate', 'candidate_id']),
            employer_authorizer=TenantAuthorizer(['tenant', 'tenant_id']))
