from trsvcscore.db.models import User, JobLocationPref, JobTechnologyPref
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.sanitization import ResourceSanitizer
from rest.resource import Resource
from auth import UserAuthorizer
from resources.location import LocationResource
from resources.technology import TechnologyResource
from resources.tenant import TenantResource

class UserSanitizer(ResourceSanitizer):
    def __init__(self):
        super(UserSanitizer, self).__init__()

    def sanitize_resources(self, context, resources):
        for resource in resources:
            user_id_field = resource.desc.fields_by_name['id']
            tenant_id_field = resource.desc.fields_by_name['tenant_id']

            user_id = user_id_field.to_model(resource.id)
            tenant_id = tenant_id_field.to_model(resource.tenant_id)

            if context.user_id == user_id or \
               (context.tenant_id != 1 and context.tenant_id == tenant_id):
                continue
            
            #remove personal info
            resource.first_name = ""
            resource.last_name = ""
            resource.email = ""

class UserResource(Resource):
    class Meta:
        resource_name = "users"
        model_class = User
        methods = ["GET", "PUT"]
        bulk_methods = ["GET"]
        related_methods = {
            "tenant": ["GET"],
            "developer_profile": ["GET"],
            "employer_profile": ["GET"],
            "chats": ["GET"],
            "chat_reels": ["GET"],
            "skills": ["GET"],
            "locations": ["GET"],
            "location_prefs": ["GET"],
            "technologies": ["GET"],
            "technology_prefs": ["GET"],
            "position_prefs": ["GET"],
            "applications": ["GET"],
            "job_notes": ["GET"],
            "interview_offers": ["GET"]
        }
        related_bulk_methods = {
            "chats": ["GET"],
            "chat_reels": ["GET"],
            "skills": ["GET"],
            "locations": ["GET"],
            "location_prefs": ["GET"],
            "technologies": ["GET"],
            "technology_prefs": ["GET"],
            "position_prefs": ["GET"],
            "applications": ["GET"],
            "job_notes": ["GET"],
            "interview_offers": ["GET"]
        }
        filtering = {
            "id": ["eq", "in"],
            "tenant_id": ["eq"],
            "tenant__id": ["eq"],
            "technology_prefs__id": ["eq"],
            "chats__id": ["eq"],
            "position_prefs__id": ["eq"]
        }
        with_relations = [
            r"^tenant$",
            r"^developer_profile$",
            r"^employer_profile$",
            r"^chats(__topic)?$",
            r"^chat_reels(__chat(__topic)?)?$",
            r"^locations$",
            r"^location_prefs(__location)?$",
            r"^skills(__technology)?$",
            r"^technologies$",
            r"^technology_prefs(__technology)?$",
            r"^position_prefs$"
            ]
        ordering = []
        limit = 20
    

    #fields
    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField(primary_key=True)
    first_name = fields.StringField()
    last_name = fields.StringField()
    email = fields.StringField(readonly=True)
    
    tenant = fields.EncodedForeignKey(TenantResource, backref="users")
    locations = fields.ManyToMany(LocationResource, through=JobLocationPref, backref="users+")
    technologies = fields.ManyToMany(TechnologyResource, through=JobTechnologyPref, backref="users")
    
    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = UserAuthorizer(['id'], ['GET'])
    sanitizer = UserSanitizer()


#Add subresources with cirucular dependency
from resources.user_search import UserSearchResource
UserResource.add_to_class('search', UserSearchResource())
