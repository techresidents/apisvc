from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobPositionTypePreference, JobPositionType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.exceptions import ValidationError
from rest.resource import Resource
from resources.user import UserResource

class PositionTypeEnum(Enum):
    model_class = JobPositionType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class PositionTypeField(fields.StringField):
    def to_model(self, value):
        value = super(PositionTypeField, self).to_model(value)
        if value in PositionTypeEnum.VALUES_TO_KEYS:
            pass
        elif value in PositionTypeEnum.KEYS_TO_VALUES:
            value = PositionTypeEnum.KEYS_TO_VALUES[value]
        else:
            raise ValidationError("'%s' invalid type" % value)
        return value

    def to_python(self, value):
        value = super(PositionTypeField, self).to_python(value)
        if value in PositionTypeEnum.KEYS_TO_VALUES:
            pass
        else:
            try:
                value = PositionTypeEnum.VALUES_TO_KEYS[int(value)]
            except:
                raise ValidationError("'%s' invalid type" % value)
        return value

class PositionPreferenceResource(Resource):
    class Meta:
        resource_name = "position_prefs"
        model_class = JobPositionTypePreference
        methods = ["GET"]
        bulk_methods = ["GET"]
        related_methods = {
            "user": ["GET"]
        }

        filtering = {
            "id": ["eq"],
            "user__id": ["eq"]
        }    
        with_relations = []
        ordering = ["id"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    user_id = fields.EncodedField()
    type = PositionTypeField(model_attname="position_type_id")
    salary_start = fields.IntegerField(nullable=True)
    salary_end = fields.IntegerField(nullable=True)

    user = fields.EncodedForeignKey(UserResource, backref="position_prefs", model_name="user", model_attname="user_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
