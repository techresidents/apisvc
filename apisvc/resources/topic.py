from trsvcscore.db.enum import Enum
from trsvcscore.db.models import Topic, TopicType
from trsvcscore.db.managers.tree import TreeManager
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.fields.related import RelatedDescriptor
from rest.resource import Resource
from rest.alchemy.query import AlchemyQuery
from rest.authorization import PerUserResourceAuthorizer
from resources.user import UserResource

class TopicTypeEnum(Enum):
    model_class = TopicType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class TopicTreeField(fields.RelatedField):
    def __init__(self, relation, **kwargs):
        super(TopicTreeField, self).__init__(many=True, **kwargs)
        self.relation = relation

    def contribute_to_class(self, resource_class, name):
        super(TopicTreeField, self).contribute_to_class(resource_class, name)
        if self.relation == "self":
            self.relation = resource_class
            self.self_referential = True

        setattr(resource_class, name, RelatedDescriptor(self))

class TopicQuery(AlchemyQuery):
    def model_to_resource(self, model, resource=None, excludes=None):
        return super(TopicQuery, self).model_to_resource(
                model, resource, excludes=["level"])

    def resource_to_model(self, resource, model=None, excludes=None):
        return super(TopicQuery, self).resource_to_model(
                resource, model, excludes=["level"])

class TopicTreeQuery(TopicQuery):
    def __init__(self, resource_class, transaction_factory, primary_key):
        super(TopicTreeQuery, self).__init__(
                resource_class=resource_class,
                transaction_factory=transaction_factory)
        self.primary_key = primary_key
    
    def all(self):
        with self.transaction_factory() as db_session:
            results = []
            tree_manager = TreeManager(self.resource_class.desc.model_class)
            for model, level in tree_manager.tree_by_rank(db_session, self.primary_key):
                resource = self.model_to_resource(model)
                resource.level = level
                results.append(resource)
            return results

class TopicManager(AlchemyResourceManager):
    def __init__(self, db_session_factory):
        super(TopicManager, self).__init__(
                db_session_factory=db_session_factory,
                query_class=TopicQuery)

    def build_get_related_query(self, related_field, resource_instance, **kwargs):
        if related_field.name == "tree":
            field = resource_instance.desc.fields_by_name["id"]
            primary_key = field.to_model(resource_instance.primary_key_value())
            return TopicTreeQuery(
                    resource_class=self.resource_class,
                    transaction_factory=self.transaction_factory,
                    primary_key=primary_key)
        else:
            return super(TopicManager, self).build_get_related_query(
                    related_field,
                    resource_instance,
                    **kwargs)

class TopicResource(Resource):
    class Meta:
        resource_name = "topics"
        model_class = Topic
        methods = ["GET"]
        bulk_methods = ["GET"]
        related_methods = {
            "children": ["GET"],
        }
        filtering = {
            "id": ["eq"],
            "parent_id": ["eq"],
            "children": ["eq"],
            "parent": ["eq"],
        }    
        ordering = ["id"]
        limit = 20
    
    id = fields.EncodedField(primary_key=True)
    parent_id = fields.EncodedField(nullable=True)
    type = EnumField(TopicTypeEnum, model_attname="type_id")
    title = fields.StringField()
    description = fields.StringField()
    duration = fields.IntegerField()
    tree = TopicTreeField("self")
    rank = fields.IntegerField()
    level = fields.IntegerField(nullable=True)
    user_id = fields.EncodedField()
    public = fields.BooleanField()
    recommended_participants = fields.IntegerField()

    parent = fields.EncodedForeignKey("self", backref="children", nullable=True)
    user = fields.EncodedForeignKey(UserResource, backref="topics+")

    objects = TopicManager(db_session_factory)
    authorizer = PerUserResourceAuthorizer(UserResource, "user_id", ["GET"])
