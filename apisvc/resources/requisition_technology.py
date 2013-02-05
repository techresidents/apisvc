from trsvcscore.db.models import JobRequisitionTechnology
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.requisition import RequisitionResource
from resources.technology import TechnologyResource

class RequisitionTechnologyResource(Resource):
    class Meta:
        resource_name = "requisition_technologies"
        model_class = JobRequisitionTechnology
        methods = ["GET", "POST", "PUT"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "requisition__id": ["eq"]
        }
        with_relations = []

    id = fields.EncodedField(primary_key=True)
    requisition_id = fields.EncodedField()
    technology_id = fields.IntegerField()
    yrs_experience = fields.IntegerField()
    
    requisition = fields.EncodedForeignKey(RequisitionResource, backref="requisition_technologies")
    technology = fields.ForeignKey(TechnologyResource, backref="requisition_technologies+")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
