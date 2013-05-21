from trsvcscore.db.models import JobApplicationLog
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.authorization import MultiAuthorizer
from rest.resource import Resource
from auth import TenantAuthorizer, TenantUserAuthorizer
from resources.user import UserResource
from resources.tenant import TenantResource
from resources.application import ApplicationResource

class ApplicationLogResource(Resource):
    class Meta:
        resource_name = "application_logs"
        model_class = JobApplicationLog
        methods = ["GET", "POST"]
        bulk_methods = ["GET"]
        filtering = {
            "id": ["eq"],
            "application__id": ["eq"]
        }    
        with_relations = ["user"]
        ordering = ["created"]

    id = fields.EncodedField(primary_key=True)
    tenant_id = fields.EncodedField()
    user_id = fields.EncodedField()
    application_id = fields.EncodedField()
    note = fields.StringField(nullable=True)
    created = fields.DateTimeField(nullable=True, readonly=True)

    tenant = fields.EncodedForeignKey(TenantResource, backref="application_logs+")
    user = fields.EncodedForeignKey(UserResource, backref="application_logs+")
    application = fields.EncodedForeignKey(ApplicationResource, backref="application_logs")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
    authorizer = MultiAuthorizer({
        "GET": TenantAuthorizer(['tenant', 'tenant_id']),
        ("POST", "PUT", "DELETE"): TenantUserAuthorizer(
            ['tenant', 'tenant_id'],
            ['user', 'user_id'])
    })
