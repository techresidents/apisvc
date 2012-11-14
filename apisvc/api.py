import resources
from rest.api import Api
from rest.middleware.auth import AuthorizationMiddleware, QueryAuthorizationMiddleware
from rest.middleware.query import QueryBuilderMiddleware
from rest.middleware.sanitization import SanitizationMiddleware
from rest.middleware.serialization import SerializationMiddleware
from rest.middleware.transaction import TransactionMiddleware
from auth import SessionAuthenticationMiddleware

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
api_v1.add_resource(resources.LocationResource)
api_v1.add_resource(resources.TechnologyResource)
api_v1.add_resource(resources.TopicResource)
api_v1.add_resource(resources.UserResource)
api_v1.add_resource(resources.ChatResource)
api_v1.add_resource(resources.ChatSessionResource)
api_v1.add_resource(resources.SkillResource)
api_v1.add_resource(resources.ArchiveResource)
api_v1.add_resource(resources.PositionPreferenceResource)
api_v1.add_resource(resources.ChatMinuteResource)
api_v1.add_resource(resources.SpeakingMarkerResource)
api_v1.add_resource(resources.ChatTagResource)
