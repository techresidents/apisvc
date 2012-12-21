from trsvcscore.db.models import User, JobLocationPreference, JobTechnologyPreference
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.sanitization import ResourceSanitizer
from rest.resource import Resource
from resources.location import LocationResource
from resources.technology import TechnologyResource


class UserSanitizer(ResourceSanitizer):
    def __init__(self):
        super(UserSanitizer, self).__init__()

    def sanitize_resources(self, context, resources):
        for resource in resources:
            field = resource.desc.fields_by_name['id']
            if context.user_id == field.to_model(resource.id):
                continue
            
            #remove personal info
            resource.first_name = ""
            resource.last_name = ""
            resource.email = ""

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
            "technology_prefs": ["GET"],
            "position_prefs": ["GET"],
            "highlight_sessions": ["GET"]
        }
        related_bulk_methods = {
            "chat_sessions": ["GET"],
            "skills": ["GET"],
            "location_prefs": ["GET"],
            "technology_prefs": ["GET"],
            "position_prefs": ["GET"],
            "highlight_sessions": ["GET"]
        }
        filtering = {
            "id": ["eq"],
            "technology_prefs__id": ["eq"],
            "chat_sessions__id": ["eq"],
            "position_prefs__id": ["eq"],
            "highlight_sessions__id": ["eq"]
        }
        with_relations = [
            r"^chat_sessions(__chat)?(__topic)?$",
            r"^location_prefs$",
            r"^skills(__technology)?$",
            r"^technology_prefs$",
            r"^position_prefs$",
            r"^highlight_sessions$",
            ]
        ordering = []
        limit = 20
    
    id = fields.EncodedField(primary_key=True)
    first_name = fields.StringField()
    last_name = fields.StringField()
    email = fields.StringField(readonly=True)

    location_prefs = fields.ManyToMany(LocationResource, through=JobLocationPreference, backref="users+")
    technology_prefs = fields.ManyToMany(TechnologyResource, through=JobTechnologyPreference, backref="users")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    sanitizer = UserSanitizer()
