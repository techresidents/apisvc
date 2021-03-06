from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobApplication, JobApplicationStatus, JobApplicationType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import DeveloperEmployerAuthorizer, TenantAuthorizer, UserAuthorizer
from resources.user import UserResource
from resources.tenant import TenantResource
from resources.requisition import RequisitionResource

class ApplicationDeveloperAuthorizer(UserAuthorizer):
    def __init__(self, *args, **kwargs):
        super(ApplicationDeveloperAuthorizer, self).__init__(*args, **kwargs)
        self.allowed_methods = ['GET']
    
    def authorize_query(self, context, request, query):
        query = super(ApplicationDeveloperAuthorizer, self).authorize_query(
                context, request, query)
        if context.method not in self.allowed_methods:
            raise AuthorizationError('invalid method: %s' % context.method)
        return query

class ApplicationTypeEnum(Enum):
    model_class = JobApplicationType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class ApplicationStatusEnum(Enum):
    model_class = JobApplicationStatus
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class ApplicationResource(Resource):
    class Meta:
        resource_name = "applications"
        model_class = JobApplication
        methods = ["GET", "POST", "PUT"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "tenant_id": ["eq"],
            "tenant__id": ["eq"],
            "user_id" : ["eq", "in"],
            "user__id": ["eq"],
            "created": ["eq", "range"],
            "status": ["eq", "in", "istartswith"],
            "requisition__status": ["eq", "in"],
            "requisition__title": ["eq", "in", "istartswith"]
        }
        related_methods = {
            "application_logs": ["GET"],
            "application_scores": ["GET"],
            "application_votes": ["GET"],
            "interview_offers": ["GET"]
        }
        related_bulk_methods = {
            "application_logs": ["GET"],
            "application_scores": ["GET"],
            "application_votes": ["GET"],
            "interview_offers": ["GET"]
        }
        with_relations = ['requisition']
        ordering = [
            "created",
            "status",
            "user_id",
            "requisition__status",
            "requisition__title",
        ]
        limit = 40

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    user_id = fields.EncodedField()
    creator_id = fields.EncodedField()
    requisition_id = fields.EncodedField()
    created = fields.DateTimeField(nullable=True, readonly=True)
    type = EnumField(ApplicationTypeEnum, model_attname="type_id")
    status = EnumField(ApplicationStatusEnum, model_attname="status_id")
    created = fields.DateTimeField(nullable=True, readonly=True)

    tenant = fields.EncodedForeignKey(TenantResource, backref="applications")
    user = fields.EncodedForeignKey(UserResource, backref="applications")
    creator = fields.EncodedForeignKey(UserResource, backref="applications+")
    requisition = fields.EncodedForeignKey(RequisitionResource, backref="applications")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = DeveloperEmployerAuthorizer(
            developer_authorizer=ApplicationDeveloperAuthorizer(['user', 'user_id']),
            employer_authorizer=TenantAuthorizer(['tenant', 'tenant_id']))
