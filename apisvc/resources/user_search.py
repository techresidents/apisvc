from factory.es import es_client_pool

from rest import fields
from rest.authentication import SessionAuthenticator
from rest.struct import Struct
from rest.es.facet import TermsFacet, RangeFacet, DateRangeFacet
from rest.es.fields import MultiMatchQueryField
from rest.es.manager import ElasticSearchManager
from rest.option import Option
from rest.resource import Resource
from resources.user import UserResource

class Skill(Struct):
    id = fields.IntegerField()
    name = fields.StringField(filter_ext=".raw")

class Location(Struct):
    id = fields.IntegerField()
    city = fields.StringField(filter_ext=".raw")

class Position(Struct):
    id = fields.IntegerField()
    type = fields.StringField(filter_ext=".raw")

class UserSearchResource(Resource):
    class Meta:
        resource_name = "search"
        es_index = "users"
        es_doc = "user"
        bulk_methods = ["GET"]
        filtering = {
            "q": ["eq"],
            "yrs_experience": ["eq", "in", "range", "ranges"],
            "joined": ["eq", "in", "range", "ranges"],
            "skills__name": ["eq", "in"],
            "location_prefs__city": ["eq", "in"],
            "position_prefs__type": ["eq", "in"]
        }
        with_relations = [
            "^user(__skills)?$"
        ]
        ordering = []
        limit = 20
    
    #options
    f_skills_size = Option(default=10, field=fields.IntegerField())
    f_location_prefs_size = Option(default=10, field=fields.IntegerField())
    f_position_prefs_size = Option(default=10, field=fields.IntegerField())

    #fields
    id = fields.EncodedField(primary_key=True)
    user_id = fields.EncodedField(model_attname="id")
    yrs_experience = fields.IntegerField()
    joined = fields.DateTimeField()
    skills = fields.ListField(field=fields.StructField(Skill, dict))
    location_prefs = fields.ListField(field=fields.StructField(Location, dict))
    position_prefs = fields.ListField(field=fields.StructField(Position, dict))
    q = MultiMatchQueryField(es_fields=['skills.name'], nullable=True)
    
    #related fields
    user = fields.EncodedForeignKey(UserResource, backref="searches+")
    
    #facets
    f_skills = TermsFacet(field="skills__name",
            es_field="skills.name.raw",
            size_option="f_skills_size")
    f_location_prefs = TermsFacet(field="location_prefs__city",
            es_field="location_prefs.city.raw",
            size_option="f_location_prefs_size")
    f_position_prefs = TermsFacet(field="position_prefs__type",
            es_field="position_prefs.type.raw",
            size_option="f_position_prefs_size")
    f_yrs_experience = RangeFacet(field="yrs_experience")\
            .add(0,2).add(3,5).add(6, 100, name="6+")
    f_joined = DateRangeFacet(field="joined")\
            .add("now-7d", "now", name="Last 7 days")\
            .add("now-30d", "now", name="Last 30 days")
    
    #objects
    objects = ElasticSearchManager(es_client_pool)
    authenticator = SessionAuthenticator()
