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
    technology_id = fields.IntegerField()
    expertise_type_id = fields.IntegerField()
    name = fields.StringField(filter_ext=".raw")
    expertise_type = fields.StringField()
    yrs_experience = fields.IntegerField()

class LocationPref(Struct):
    id = fields.IntegerField()
    location_id = fields.IntegerField()
    region = fields.StringField(filter_ext=".raw")

class PositionPref(Struct):
    id = fields.IntegerField()
    type_id = fields.IntegerField()
    type = fields.StringField(filter_ext=".raw")
    salary_start = fields.IntegerField(nullable=True)
    salary_end = fields.IntegerField(nullable=True)

class TechnologyPref(Struct):
    id = fields.IntegerField()
    technology_id = fields.IntegerField()
    name = fields.StringField(filter_ext=".raw")

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
            "location_prefs__region": ["eq", "in"],
            "position_prefs__type": ["eq", "in"],
            "technology_prefs__name": ["eq", "in"]
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
    f_technology_prefs_size = Option(default=10, field=fields.IntegerField())

    #fields
    id = fields.EncodedField(primary_key=True)
    user_id = fields.EncodedField(model_attname="id")
    yrs_experience = fields.IntegerField()
    joined = fields.DateTimeField()
    skills = fields.ListField(field=fields.StructField(Skill, dict))
    location_prefs = fields.ListField(field=fields.StructField(LocationPref, dict))
    position_prefs = fields.ListField(field=fields.StructField(PositionPref, dict))
    technology_prefs = fields.ListField(field=fields.StructField(TechnologyPref, dict))
    q = MultiMatchQueryField(es_fields=['skills.name', 'location_prefs.name'],
            nullable=True)
    
    #related fields
    user = fields.EncodedForeignKey(UserResource, backref="searches+")
    
    #facets
    f_skills = TermsFacet(title="Skills",
            field="skills__name",
            es_field="skills.name.raw",
            size_option="f_skills_size")
    f_location_prefs = TermsFacet(title="Location Preferences",
            field="location_prefs__region",
            es_field="location_prefs.region.raw",
            size_option="f_location_prefs_size")
    f_position_prefs = TermsFacet(title="Position Preferences",
            field="position_prefs__type",
            es_field="position_prefs.type.raw",
            size_option="f_position_prefs_size")
    f_technology_prefs = TermsFacet(title="Technology Preferences",
            field="technology_prefs__name",
            es_field="technology_prefs.name.raw",
            size_option="f_technology_prefs_size")
    f_yrs_experience = RangeFacet(title="Years Experience",
            field="yrs_experience")\
            .add(0,2).add(3,5).add(6, 10).add(11, 100, name="10+")
    f_joined = DateRangeFacet(title="Joined", field="joined")\
            .add("now-7d", "now", name="Last 7 days")\
            .add("now-30d", "now", name="Last 30 days")\
            .add("now-3M", "now", name="Last 3 months")\
            .add("now-12M", "now", name="Last year")
    
    #objects
    objects = ElasticSearchManager(es_client_pool)
    authenticator = SessionAuthenticator()
