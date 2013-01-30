from trsvcscore.db.enum import Enum
from trsvcscore.db.models import JobPositionTypePref, JobPositionType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.user import UserResource

class PositionTypeEnum(Enum):
    model_class = JobPositionType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class PositionPreferenceResource(Resource):
    class Meta:
        resource_name = "position_prefs"
        model_class = JobPositionTypePref
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
    type = EnumField(PositionTypeEnum, model_attname="position_type_id")
    salary_start = fields.IntegerField(nullable=True)
    salary_end = fields.IntegerField(nullable=True)

    user = fields.EncodedForeignKey(UserResource, backref="position_prefs", model_name="user", model_attname="user_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
