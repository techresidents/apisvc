from trsvcscore.db.enum import Enum
from trsvcscore.db.models import ChatArchive, ChatArchiveType, MimeType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.fields import EnumField
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.resource import Resource
from resources.chat import ChatResource
from settings import CDN_URL, CDN_SSL_URL, CDN_STREAMING_URL

class ChatArchiveTypeEnum(Enum):
    model_class = ChatArchiveType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class MimeTypeEnum(Enum):
    model_class = MimeType
    key_column = "type"
    value_column = "id"
    db_session_factory = db_session_factory

class CdnUrlField(fields.StringField):
    def __init__(self, cdn_url, **kwargs):
        super(CdnUrlField, self).__init__(**kwargs)
        self.cdn_url = cdn_url
    def to_model(self, value):
        value = super(CdnUrlField, self).to_model(value)
        value = value.replace(self.cdn_url, "")
        return value
    def to_python(self, value):
        value = super(CdnUrlField, self).to_model(value)
        if value is not None and not value.startswith(self.cdn_url):
            value = "%s/%s" % (self.cdn_url, value)
        return value

class ArchiveManager(AlchemyResourceManager):
    def __init__(self, *args, **kwargs):
        super(ArchiveManager, self).__init__(*args, **kwargs)

    def build_get_query(self, **kwargs):
        kwargs["public"] = "True"
        return super(ArchiveManager, self).build_get_query(**kwargs) 
    
    def build_one_query(self, **kwargs):
        kwargs["public"] = "True"
        return super(ArchiveManager, self).build_one_query(**kwargs) 

    def build_all_query(self, **kwargs):
        kwargs["public"] = "True"
        return super(ArchiveManager, self).build_all_query(**kwargs) 

class ArchiveResource(Resource):
    class Meta:
        resource_name = "archives"
        model_class = ChatArchive
        methods = ["GET"]
        bulk_methods = ["GET"]

        filtering = {
            "id": ["eq"],
            "public": ["eq"],
            "chat_session__id": ["eq"]
        }    

        limit = 20

    id = fields.IntegerField(primary_key=True, readonly=True)
    type = EnumField(ChatArchiveTypeEnum, model_attname="type_id", readonly=True)
    mime_type = EnumField(MimeTypeEnum, model_attname="mime_type_id", readonly=True)
    chat_id = fields.EncodedField(readonly=True)
    path = fields.StringField(readonly=True)
    url = CdnUrlField(cdn_url=CDN_URL, model_attname="path", readonly=True)
    ssl_url = CdnUrlField(cdn_url=CDN_SSL_URL, model_attname="path", readonly=True)
    streaming_url = CdnUrlField(cdn_url=CDN_STREAMING_URL, model_attname="path", readonly=True)
    public = fields.BooleanField(readonly=True)
    length = fields.IntegerField(nullable=True, readonly=True)
    offset = fields.IntegerField(nullable=True, readonly=True)
    waveform = fields.StringField(nullable=True, readonly=True)
    waveform_path = fields.StringField(nullable=True, readonly=True)
    waveform_url = CdnUrlField(cdn_url=CDN_URL, model_attname="waveform_path", nullable=True, readonly=True)

    chat = fields.EncodedForeignKey(ChatResource, backref="archives", model_name="chat", model_attname="chat_id")

    objects = ArchiveManager(db_session_factory)
    authenticator = SessionAuthenticator()

