from trsvcscore.db.enum import Enum
from trsvcscore.db.models import Technology, TechnologyType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.exceptions import ValidationError
from rest.resource import Resource

class TechnologyTypeEnum(Enum):
    model_class = TechnologyType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class TechnologyTypeField(fields.StringField):
    def to_model(self, value):
        value = super(TechnologyTypeField, self).to_model(value)
        if value in TechnologyTypeEnum.VALUES_TO_KEYS:
            pass
        elif value in TechnologyTypeEnum.KEYS_TO_VALUES:
            value = TechnologyTypeEnum.KEYS_TO_VALUES[value]
        else:
            raise ValidationError("'%s' invalid type" % value)
        return value

    def to_python(self, value):
        value = super(TechnologyTypeField, self).to_python(value)
        if value in TechnologyTypeEnum.KEYS_TO_VALUES:
            pass
        else:
            try:
                value = TechnologyTypeEnum.VALUES_TO_KEYS[int(value)]
            except:
                raise ValidationError("'%s' invalid type" % value)
        return value

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
    type = TechnologyTypeField(model_attname="type_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
