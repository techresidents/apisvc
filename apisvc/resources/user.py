from trsvcscore.db.models import User, JobLocationPreference, JobTechnologyPreference
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.location import LocationResource
from resources.technology import TechnologyResource

class UserResource(Resource):
    class Meta:
        resource_name = "users"
        model_class = User
        methods = ["GET"]
        bulk_methods = ["GET"]
        related_methods = {
            "chat_sessions": ["GET"],
            "skills": ["GET"],
            "location_prefs": ["GET"],
            "technology_prefs": ["GET"]
        }
        related_bulk_methods = {
            "chat_sessions": ["GET"],
            "skills": ["GET"],
            "location_prefs": ["GET"],
            "technology_prefs": ["GET"]
        }
        filtering = {
            "id": ["eq"],
            "technology_prefs__id": ["eq"]
        }
        with_relations = [r"^chat_sessions$", "chat_sessions"]
        ordering = []
        limit = 20
    
    id = fields.IntegerField(primary_key=True)
    first_name = fields.StringField()
    last_name = fields.StringField()
    email = fields.StringField()

    location_prefs = fields.ManyToMany(LocationResource, through=JobLocationPreference, backref="users+")
    technology_prefs = fields.ManyToMany(TechnologyResource, through=JobTechnologyPreference, backref="users")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
