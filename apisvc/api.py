from rest.api import Api
from rest.middleware.auth import AuthorizationMiddleware, QueryAuthorizationMiddleware
from rest.middleware.query import QueryBuilderMiddleware
from rest.middleware.sanitization import SanitizationMiddleware
from rest.middleware.serialization import SerializationMiddleware
from rest.middleware.transaction import TransactionMiddleware
from auth import SessionAuthenticationMiddleware
from resources import UserResource, ChatResource, ChatSessionResource, TopicResource

api_v1 = Api("/api/v1/")

#middlewares
api_v1.add_middleware(SessionAuthenticationMiddleware())
api_v1.add_middleware(AuthorizationMiddleware())
api_v1.add_middleware(TransactionMiddleware())
api_v1.add_middleware(SerializationMiddleware())
api_v1.add_middleware(SanitizationMiddleware())
api_v1.add_middleware(QueryBuilderMiddleware())
api_v1.add_middleware(QueryAuthorizationMiddleware())

#resources
api_v1.add_resource(UserResource)
api_v1.add_resource(ChatResource)
api_v1.add_resource(ChatSessionResource)
api_v1.add_resource(TopicResource)
