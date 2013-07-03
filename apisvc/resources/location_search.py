from factory.es import es_client_pool

from rest import fields
from rest.authentication import SessionAuthenticator
from rest.es.fields import MatchQueryField, MultiMatchQueryField
from rest.es.manager import ElasticSearchManager
from rest.resource import Resource
from resources.location import LocationResource

class LocationSearchResource(Resource):
    class Meta:
        resource_name = "search"
        es_index = "locations"
        es_doc = "location"
        bulk_methods = ["GET"]
        filtering = {
            "q": ["eq"],
            "ac": ["eq"],
            "region": ["eq", "in"]
        }
        with_relations = [
            "^location$"
        ]
        ordering = []
        limit = 20

    #fields
    id = fields.IntegerField(primary_key=True)
    location_id = fields.IntegerField(model_attname='id')
    region = fields.StringField()
    q = MultiMatchQueryField(es_fields=['region'], nullable=True)
    ac = MatchQueryField(es_field='region.autocomplete', nullable=True)

    #related fields
    location = fields.ForeignKey(LocationResource, model_attname='id')

    #objects
    objects = ElasticSearchManager(es_client_pool)
    authenticator = SessionAuthenticator()