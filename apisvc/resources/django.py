from trsvcscore.db.models import User
from factory.db import db_session_factory
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.fields import IntegerField, StringField
from rest.resource import Resource

class UserResource(Resource):
    class Meta:
        resource_name = "users"
        model_class = User
        user_filter = "id"
        methods = ["GET"]
        related_methods = {
            "chat_sessions": ["GET"]
        }
        related_bulk_methods = {
            "chat_sessions": ["GET"]
        }
        filtering = {
            "id": ["eq"],
            "first_name": ["eq", "startswith"],
            "chat_sessions__": ["eq", "startswith"],
        }
        with_relations = [r"^chat_sessions$", "chat_sessions"]
        ordering = ["id", "first_name"]
        limit = 5
    
    id = IntegerField(primary_key=True)
    first_name = StringField()

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()
