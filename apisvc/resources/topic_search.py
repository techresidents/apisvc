from factory.es import es_client_pool

from rest import fields
from rest.authentication import SessionAuthenticator
from rest.es.facet import RangeFacet
from rest.es.fields import MultiMatchQueryField
from rest.es.manager import ElasticSearchManager
from rest.resource import Resource
from rest.struct import Struct
from resources.topic import TopicResource

class TopicSearchManager(ElasticSearchManager):
    def __init__(self, *args, **kwargs):
        super(TopicSearchManager, self).__init__(*args, **kwargs)

    def build_all_query(self, **kwargs):
        if "active" not in kwargs:
            kwargs["active"] = True
        if "order_by" not in kwargs:
            kwargs["order_by"] = "title__asc"
        return super(TopicSearchManager, self).build_all_query(**kwargs) 

class TopicStruct(Struct):
    id = fields.IntegerField()
    type_id = fields.IntegerField()
    type = fields.StringField()
    duration = fields.IntegerField()
    title = fields.StringField()
    description = fields.StringField()
    recommended_participants = fields.IntegerField()
    rank = fields.IntegerField()
    public = fields.BooleanField()
    active = fields.BooleanField()
    level = fields.IntegerField()

class TopicSearchResource(Resource):
    class Meta:
        resource_name = "search"
        es_index = "topics"
        es_doc = "topic"
        bulk_methods = ["GET"]
        filtering = {
            "q": ["eq"],
            "active": ["eq"],
            "duration": ["eq", "in", "range", "ranges"]
        }
        with_relations = [
            "^topic$"
        ]
        ordering = [
            "title"
        ]
        limit = 20

    #fields
    id = fields.EncodedField(primary_key=True)
    topic_id = fields.EncodedField(model_attname='id')
    type = fields.StringField()
    #type = EnumField(TopicTypeEnum, model_attname="type_id")
    title = fields.StringField(sort_ext=".raw")
    description = fields.StringField()
    tree = fields.ListField(field=fields.StructField(TopicStruct, dict))
    duration = fields.IntegerField()
    active = fields.BooleanField()
    q = MultiMatchQueryField(
        es_fields=['title^6', 'description^3', 'subtopic_summary^1'],
        nullable=True)

    #related fields
    topic = fields.EncodedForeignKey(TopicResource, backref="searches+")

    #facets
    f_duration = RangeFacet(title="Duration", field="duration").\
        add(0, 301, name="under 5 mins").\
        add(302, 601, name="5 to 10 mins").\
        add(602, 3600, name="10+ mins")

    #objects
    objects = TopicSearchManager(es_client_pool)
    authenticator = SessionAuthenticator()
