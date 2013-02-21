from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobRequisition, JobRequisitionStatus, JobPositionType, JobRequisitionTechnology
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.location import LocationResource
from resources.technology import TechnologyResource
from resources.tenant import TenantResource
from resources.user import UserResource

class RequisitionStatusEnum(Enum):
    model_class = JobRequisitionStatus
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class PositionTypeEnum(Enum):
    model_class = JobPositionType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class RequisitionResource(Resource):
    class Meta:
        resource_name = "requisitions"
        model_class = JobRequisition
        methods = ["GET", "POST", "PUT"]
        bulk_methods = ["GET", "POST", "PUT"]
        filtering = {
            "id": ["eq"],
            "tenant__id": ["eq"],
            "status": ["eq"]
        }
        related_methods = {
            "requisition_technologies": ["GET"]
        }
        related_bulk_methods = {
            "requisition_technologies": ["GET"]
        }
        with_relations = [
            r"^location$",
            r"^requisition_technologies(__technology)?$"
        ]
        ordering = ["title", "status"]

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    user_id = fields.EncodedField()
    location_id = fields.IntegerField()
    status = EnumField(RequisitionStatusEnum, model_attname="status_id")
    position_type = EnumField(PositionTypeEnum, model_attname="position_type_id")
    title = fields.StringField()
    description = fields.StringField()
    salary_start = fields.IntegerField()
    salary_end = fields.IntegerField()
    telecommute = fields.BooleanField()
    relocation = fields.BooleanField()
    employer_requisition_identifier = fields.StringField(nullable=True)

    tenant = fields.EncodedForeignKey(TenantResource, backref="requisitions")
    user = fields.EncodedForeignKey(UserResource, backref="requisitions")
    location = fields.ForeignKey(LocationResource, backref="requisitions+")
    technologies = fields.ManyToMany(TechnologyResource, through=JobRequisitionTechnology, backref="requisitions+")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
