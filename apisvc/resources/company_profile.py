from trsvcscore.db.enum import Enum
from trsvcscore.db.models import CompanyProfile, CompanySize
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import TenantAuthorizer
from resources.tenant import TenantResource


class CompanySizeEnum(Enum):
    model_class = CompanySize
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory


class CompanyProfileResource(Resource):
    class Meta:
        resource_name = "company_profiles"
        model_class = CompanyProfile
        methods = ["GET", "PUT"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "tenant__id": ["eq"]
        }
        ordering = []
        limit = 20

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    size = EnumField(CompanySizeEnum, model_attname="size_id")
    name = fields.StringField(nullable=True)
    description = fields.StringField(nullable=True)
    location = fields.StringField(nullable=True)
    url = fields.StringField(nullable=True)

    tenant = fields.EncodedOneToOne(TenantResource, backref="company_profile", model_name="tenant", model_attname="tenant_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = TenantAuthorizer(['tenant', 'tenant_id'], ['GET'])
