from trchatsvc.gen import TChatService
from trchatsvc.gen.ttypes import Message, MessageType, MessageHeader, \
        ChatStatus, ChatStatusMessage, UserStatus, UserStatusMessage, \
        InvalidMessageException, InvalidChatException
from tridlcore.gen.ttypes import RequestContext
from trsvcscore.hashring.zoo import ZookeeperServiceHashring
from trsvcscore.proxy.basic import BasicServiceProxy

from factory import zk
from rest import fields
from rest.authentication import SessionAuthenticator
from rest.authorization import ResourceAuthorizer
from rest.exceptions import InvalidQuery
from rest.manager import ResourceManager
from rest.option import Option
from rest.query import Query
from rest.resource import Resource
from rest.struct import Struct


class ChatMessageAuthorizer(ResourceAuthorizer):
    def __init__(self):
        super(ChatMessageAuthorizer, self).__init__()

    def authorize_query(self, context, request, query):
        query = super(ChatMessageAuthorizer, self).authorize_query(
                context, request, query)
        
        request_context = RequestContext(
                userId=context.user_id,
                impersonatingUserId=context.user_id,
                sessionId=context.session.get_key(),
                context="")
        query.service_request_context(request_context)
        return query

class ChatMessageManager(ResourceManager):
    def __init__(self, zookeeper_client):
        self.zookeeper_client = zookeeper_client
        self.chatsvc_hashring = ZookeeperServiceHashring(
                zookeeper_client=self.zookeeper_client,
                service_name="chatsvc")
        self.chatsvc_hashring.start()
        super(ChatMessageManager, self).__init__(query_factory=self.query_factory)
        
    def query_factory(self):
        return ChatMessageQuery(
                self.resource_class,
                self.chatsvc_hashring)

class ChatMessageQuery(Query):
    def __init__(self, resource_class, chatsvc_hashring):
        super(ChatMessageQuery, self).__init__(resource_class) 
        self.chatsvc_hashring = chatsvc_hashring
        self._request_context = None

    def service_request_context(self, context):
        self._request_context = context
    
    def create(self, **kwargs):
        if not self.empty():
            raise InvalidQuery("create query must be empty")

        resource = kwargs.pop("resource", None)
        if resource is None:
            resource = self.resource_class(**kwargs)
        
        chat_token = resource.header.chat_token
        try:
            service = self._get_service_proxy(chat_token)
            model = self.resource_to_model(resource)

            model = service.sendMessage(
                    requestContext=self._request_context,
                    message=model,
                    N=-1,
                    W=-1)

            resource = self.model_to_resource(model)
            return resource
        except InvalidChatException:
            msg = "invalid chat token: %s" % chat_token
            raise InvalidQuery(message=msg,
                    developer_message=msg)
        except InvalidMessageException:
            msg = "invalid message"
            raise InvalidQuery(message = msg,
                    developer_message=msg)

    def all(self):
        as_of = self.options.get("as_of")
        chat_token = self.options.get("chat_token")

        if chat_token is None:
            msg = "chat token is required to read chat messages"
            raise InvalidQuery(message=msg,
                    developer_message=msg)

        service = self._get_service_proxy(chat_token)
        
        try:
            messages = service.getMessages(
                    requestContext=self._request_context,
                    chatToken=chat_token,
                    asOf=as_of,
                    block=True,
                    timeout=10)
            
            resources = self.resource_class.Collection()
            resources.total_count = len(messages)
            start, end = self.slices
            messages = messages[start:end]
            for message in messages:
                resources.append(self.model_to_resource(message))
            return resources
        except InvalidChatException:
            msg = "invalid chat token: %s" % chat_token
            raise InvalidQuery(message=msg,
                    developer_message=msg,
                    user_message="Your chat has expired.")

    def _get_service_proxy(self, chat_token):
        node = self.chatsvc_hashring.find_hashring_node(chat_token)
        endpoint = node.service_info.default_endpoint()
        service = BasicServiceProxy(
                service_name="chatsvc",
                service_hostname=endpoint.address,
                service_port=endpoint.port,
                service_class=TChatService)
        return service


class MessageHeaderStruct(Struct):
    id = fields.StringField(nullable=True)
    type = fields.EnumField(MessageType._NAMES_TO_VALUES)
    chat_token = fields.StringField(model_attname="chatToken")
    user_id = fields.EncodedField(model_attname="userId")
    timestamp = fields.TimestampField(nullable=True)
    skew = fields.TimestampField(readonly=True, nullable=True)

class UserStatusMessageStruct(Struct):
    user_id = fields.EncodedField(model_attname="userId")
    status = fields.EnumField(UserStatus._NAMES_TO_VALUES)
    first_name = fields.StringField(nullable=True, model_attname="firstName")
    participant = fields.IntegerField(nullable=True)

class ChatStatusMessageStruct(Struct):
    user_id = fields.EncodedField(model_attname="userId")
    status = fields.EnumField(ChatStatus._NAMES_TO_VALUES)


class ChatMessageResource(Resource):
    class Meta:
        resource_name = "chat_messages"
        model_class = Message
        methods = ["POST"]
        bulk_methods = ["GET"]
        limit = 100
    
    #options
    as_of = Option(default=0, field=fields.FloatField())
    chat_token = Option(field=fields.StringField())

    #fields
    id = fields.StringField(primary_key=True, model_attname="header.id")

    header = fields.StructField(
            MessageHeaderStruct,
            MessageHeader)

    user_status_message = fields.StructField(
            UserStatusMessageStruct,
            UserStatusMessage,
            nullable=True,
            default=None,
            model_attname="userStatusMessage")

    chat_status_message = fields.StructField(
            ChatStatusMessageStruct,
            ChatStatusMessage,
            nullable=True,
            default=None,
            model_attname="chatStatusMessage")

    objects = ChatMessageManager(zk.zookeeper_client)
    authenticator = SessionAuthenticator()
    authorizer = ChatMessageAuthorizer()
