from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobRequisition, JobRequisitionStatus, \
    JobPositionType, JobRequisitionTechnology, Location
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import DeveloperEmployerAuthorizer, TenantAuthorizer, UserAuthorizer
from resources.location import LocationResource
from resources.technology import TechnologyResource
from resources.tenant import TenantResource
from resources.user import UserResource

class RequisitionManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        super(RequisitionManager, self).__init__(*args, **kwargs)

    def build_get_query(self, **kwargs):
        if "deleted" not in kwargs:
            kwargs["deleted"] = False
        return super(RequisitionManager, self).build_get_query(**kwargs)

    def build_one_query(self, **kwargs):
        if "deleted" not in kwargs:
            kwargs["deleted"] = False
        return super(RequisitionManager, self).build_one_query(**kwargs)

    def build_all_query(self, **kwargs):
        if "deleted" not in kwargs:
            kwargs["deleted"] = False
        return super(RequisitionManager, self).build_all_query(**kwargs)


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

class LocationEnum(Enum):
    model_class = Location
    key_column = "region"
    value_column = "id"
    db_session_factory = db_session_factory

class RequisitionResource(Resource):
    class Meta:
        resource_name = "requisitions"
        model_class = JobRequisition
        methods = ["GET", "POST", "PUT", "DELETE"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "tenant__id": ["eq"],
            "tenant_id": ["eq"],
            "status": ["eq"],
            "title": ["eq", "istartswith"],
            "deleted": ["eq"]
        }
        related_methods = {
            "requisition_technologies": ["GET"]
        }
        related_bulk_methods = {
            "requisition_technologies": ["GET"]
        }
        with_relations = [
            r"^requisition_technologies(__technology)?$"
        ]
        ordering = [
            "created",
            "employer_requisition_identifier",
            "title",
            "status"
        ]
        limit = 40

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    user_id = fields.EncodedField()
    location = EnumField(LocationEnum, model_attname="location_id")
    created = fields.DateTimeField(nullable=True, readonly=True)
    status = EnumField(RequisitionStatusEnum, model_attname="status_id")
    position_type = EnumField(PositionTypeEnum, model_attname="position_type_id")
    title = fields.StringField()
    description = fields.StringField()
    salary = fields.StringField()
    telecommute = fields.BooleanField()
    relocation = fields.BooleanField()
    equity = fields.StringField(nullable=True)
    employer_requisition_identifier = fields.StringField(nullable=True)
    deleted = fields.BooleanField(hidden=True)

    tenant = fields.EncodedForeignKey(TenantResource, backref="requisitions")
    user = fields.EncodedForeignKey(UserResource, backref="requisitions")
    technologies = fields.ManyToMany(TechnologyResource, through=JobRequisitionTechnology, backref="requisitions+")

    objects = AlchemyResourceManager(db_session_factory)
    # TODO objects = RequisitionManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = TenantAuthorizer(['tenant', 'tenant_id'], ['GET'])
