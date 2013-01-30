from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobApplication, JobApplicationStatus, JobApplicationType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.user import UserResource
from resources.tenant import TenantResource
from resources.requisition import RequisitionResource

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
            "id": ["eq"]
        }    
        with_relations = []

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    user_id = fields.EncodedField()
    requisition_id = fields.EncodedField()
    type = EnumField(ApplicationTypeEnum, model_attname="type_id")
    status = EnumField(ApplicationStatusEnum, model_attname="status_id")

    tenant = fields.EncodedForeignKey(TenantResource, backref="applications+")
    user = fields.EncodedForeignKey(UserResource, backref="applications")
    requisition = fields.EncodedForeignKey(RequisitionResource, backref="applications")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
