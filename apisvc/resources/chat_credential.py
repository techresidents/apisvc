import uuid

import settings
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload
from twilio.util import TwilioCapability

from trsvcscore.db.models import Chat

from factory.db import db_session_factory
from rest import fields
from rest.alchemy.transaction import AlchemyTransaction
from rest.authorization import ResourceAuthorizer
from rest.exceptions import AuthorizationError, ResourceNotFound
from rest.alchemy.manager import AlchemyResourceManager
from rest.alchemy.query import AlchemyQuery
from rest.resource import Resource
from resources.chat import ChatResource

class ChatCredentialAuthorizer(ResourceAuthorizer):
    def __init__(self, db_session_factory):
        super(ChatCredentialAuthorizer, self).__init__()
        self.transaction_factory = lambda: AlchemyTransaction(db_session_factory)

    def authorize_create_query(self, context, request, query):
        resource = context.data

        with self.transaction_factory() as db_session:
            user_id = context.user_id
            chat_id_field = resource.desc.fields_by_name["chat_id"]
            chat_id = chat_id_field.validate_for_model(resource.chat_id)
            db_query = db_session.query(Chat) \
                    .filter(Chat.id == chat_id) \
                    .options([joinedload(Chat.chat_participants)])
            chat = db_query.one()
            
            if chat.end is not None:
                msg = "chat credentials cannot be created for ended chat"
                raise AuthorizationError(message=msg,
                        developer_message=msg,
                        user_message=msg)

            participant_ids = [p.user_id for p in chat.chat_participants]
            if user_id not in participant_ids:
                msg = "non-participants cannot create chat credentials"
                raise AuthorizationError(message=msg,
                        developer_message=msg,
                        user_message=msg)
        return query

class ChatCredentialManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        kwargs["query_class"] = ChatCredentialQuery
        super(ChatCredentialManager, self).__init__(*args, **kwargs)


class ChatCredentialQuery(AlchemyQuery):
    def __init__(self, resource_class, transaction_factory):
        super(ChatCredentialQuery, self).__init__(
                resource_class, transaction_factory)

    def create(self, **kwargs):
        resource = kwargs.pop("resource", None)
        if resource is None:
            resource = self.resource_class(**kwargs)

        resource.id = uuid.uuid4().hex
        resource.token = self._get_chat_token(resource)
        resource.twilio_capability = self._get_twilio_capability(resource)
        return resource
    
    def _get_chat_token(self, resource):
        chat_id_field = self.resource_class.desc.fields_by_name["chat_id"]
        chat_id = chat_id_field.validate_for_model(resource.chat_id)

        with self.transaction_factory() as db_session:
            query = db_session.query(Chat) \
                    .filter(Chat.id == chat_id)
            try: 
                chat = query.one()
                return chat.token
            except NoResultFound:
                raise ResourceNotFound()

    def _get_twilio_capability(self, resource):
        cap = TwilioCapability(settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN)
        cap.allow_client_outgoing(settings.TWILIO_APPLICATION_SID)
        return cap.generate(expires=60)



class ChatCredentialResource(Resource):
    class Meta:
        resource_name = "chat_credentials"
        model_class = dict
        methods = ["POST"]
        filtering = {
            "id": ["eq"]
        }
    id = fields.StringField(primary_key=True)        
    chat_id = fields.EncodedField()
    token = fields.StringField(readonly=True, nullable=True)
    twilio_capability = fields.StringField(readonly=True, nullable=True)

    chat = fields.EncodedForeignKey(ChatResource, backref="chat_credentials")

    objects = ChatCredentialManager(db_session_factory)
    authorizer = ChatCredentialAuthorizer(db_session_factory)
