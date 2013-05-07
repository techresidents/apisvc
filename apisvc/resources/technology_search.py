from factory.es import es_client_pool

from rest import fields
from rest.authentication import SessionAuthenticator
from rest.es.fields import MatchQueryField, MultiMatchQueryField
from rest.es.manager import ElasticSearchManager
from rest.resource import Resource
from resources.technology import TechnologyResource

class TechnologySearchResource(Resource):
    class Meta:
        resource_name = "search"
        es_index = "technologies"
        es_doc = "technology"
        bulk_methods = ["GET"]
        filtering = {
            "q": ["eq"],
            "ac": ["eq"],
            "name": ["eq", "in"]
        }
        with_relations = [
            "^technology$"
        ]
        ordering = []
        limit = 20
    
    #fields
    id = fields.IntegerField(primary_key=True)
    technology_id = fields.IntegerField(model_attname='id')
    name = fields.StringField()
    description = fields.StringField()
    type = fields.StringField()
    q = MultiMatchQueryField(es_fields=['name', 'description'],
            nullable=True)
    ac = MatchQueryField(es_field='name.autocomplete', nullable=True)

    #related fields
    technology = fields.ForeignKey(TechnologyResource, model_attname='id')

    #objects
    objects = ElasticSearchManager(es_client_pool)
    authenticator = SessionAuthenticator()
