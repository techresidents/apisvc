from trsvcscore.db.models import JobEvent, JobEventCandidate
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.user import UserResource

class JobEventResource(Resource):
    class Meta:
        resource_name = "job_events"
        model_class = JobEvent
        methods = ["GET"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"]
        }    
        with_relations = []

    id = fields.EncodedField(primary_key=True)
    start = fields.DateTimeField()
    end = fields.DateTimeField()
    description = fields.StringField()

    candidates = fields.ManyToMany(UserResource, through=JobEventCandidate, backref="job_events+")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
