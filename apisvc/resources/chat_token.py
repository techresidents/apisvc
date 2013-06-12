from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import joinedload

from trsvcscore.db.models import Chat

from factory.db import db_session_factory
from rest import fields
from rest.alchemy.transaction import AlchemyTransaction
from rest.authorization import ResourceAuthorizer
from rest.exceptions import AuthorizationError, ResourceNotFound
from rest.alchemy.manager import AlchemyResourceManager
from rest.alchemy.query import AlchemyQuery
from rest.exceptions import InvalidQuery
from rest.resource import Resource

class ChatTokenAuthorizer(ResourceAuthorizer):
    def __init__(self, db_session_factory):
        super(ChatTokenAuthorizer, self).__init__()
        self.transaction_factory = lambda: AlchemyTransaction(db_session_factory)

    def authorize_query_response_resources(self, context, resources, query):
        with self.transaction_factory() as db_session:
            user_id = context.user_id
            for resource in resources:
                chat_id_field = resource.desc.fields_by_name["id"]
                chat_id = chat_id_field.validate_for_model(resource.id)
                query = db_session.query(Chat) \
                        .filter(Chat.id == chat_id) \
                        .options([joinedload(Chat.chat_participants)])
                chat = query.one()
                participant_ids = [p.user_id for p in chat.chat_participants]
                if user_id not in participant_ids:
                    msg = "non-participants cannot access chat tokens"
                    raise AuthorizationError(message=msg,
                            developer_message=msg,
                            user_message=msg)
            return chat.token


class ChatTokenManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        kwargs["query_class"] = ChatTokenQuery
        super(ChatTokenManager, self).__init__(*args, **kwargs)


class ChatTokenQuery(AlchemyQuery):
    def __init__(self, resource_class, transaction_factory):
        super(ChatTokenQuery, self).__init__(
                resource_class, transaction_factory)

    def one(self):
        if len(self.filters) != 1:
            raise InvalidQuery("id filter is required")
        
        filter = self.filters[0]
        if filter.name() != "id__eq":
            raise InvalidQuery("invalid filter: %s" % filter.name())
        
        operation = filter.operation
        encoded_chat_id = operation.operands[0]
        chat_id = operation.target_field.to_model(encoded_chat_id)
        token = self._get_chat_token(chat_id)
        return self.resource_class(id=encoded_chat_id, token=token);

    def _get_chat_token(self, chat_id):
        with self.transaction_factory() as db_session:
            query = db_session.query(Chat) \
                    .filter(Chat.id == chat_id)
            try: 
                chat = query.one()
                return chat.token
            except NoResultFound:
                raise ResourceNotFound()


class ChatTokenResource(Resource):
    class Meta:
        resource_name = "chat_tokens"
        methods = ["GET"]
        filtering = {
            "id": ["eq"]
        }
    id = fields.EncodedField(primary_key=True)        
    token = fields.StringField()

    objects = ChatTokenManager(db_session_factory)
    authorizer = ChatTokenAuthorizer(db_session_factory)
