from trsvcscore.db.enum import Enum
from trsvcscore.db.models import Technology, TechnologyType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource

class TechnologyTypeEnum(Enum):
    model_class = TechnologyType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class TechnologyResource(Resource):
    class Meta:
        resource_name = "technologies"
        model_class = Technology
        methods = ["GET"]
        bulk_methods = ["GET"]
        related_methods = {
            "users": ["GET"]
        }
        related_bulk_methods = {
            "users": ["GET"]
        }
        filtering = {
            "id": ["eq"],
            "type": ["eq"],
            "users__id": ["eq"]
        }
        limit = 20
    
    id = fields.IntegerField(primary_key=True)
    name = fields.StringField()
    description = fields.StringField()
    type = EnumField(TechnologyTypeEnum, model_attname="type_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
