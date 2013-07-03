from trsvcscore.db.enum import Enum
from trsvcscore.db.models import Skill, ExpertiseType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from auth import UserAuthorizer
from resources.user import UserResource
from resources.technology import TechnologyResource

class ExpertiseTypeEnum(Enum):
    model_class = ExpertiseType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class SkillResource(Resource):
    class Meta:
        resource_name = "skills"
        model_class = Skill
        methods = ["GET", "POST", "PUT", "DELETE"]
        bulk_methods = ["GET"]
        related_methods = {
            "user": ["GET"],
            "technology": ["GET"]
        }

        filtering = {
            "id": ["eq"],
            "expertise": ["eq", "in"],
            "yrs_experience": ["eq", "lt", "lte", "gt", "gte", "ranges"],
            "user__id": ["eq"],
            "technology__id": ["eq"]
        }    
        with_relations = ["user", "technology"]
        ordering = ["id"]
        limit = 20

    id = fields.IntegerField(primary_key=True)
    yrs_experience = fields.IntegerField()
    user_id = fields.EncodedField()
    technology_id = fields.IntegerField()
    expertise = EnumField(ExpertiseTypeEnum, model_attname="expertise_type_id")

    user = fields.EncodedForeignKey(UserResource, backref="skills", model_name="user", model_attname="user_id")
    technology = fields.ForeignKey(TechnologyResource, backref="skills+", model_name="technology", model_attname="technology_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['user_id'], ['GET'])
