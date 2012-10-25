from trsvcscore.db.enum import Enum
from trsvcscore.db.models import ChatArchive, ChatArchiveType, MimeType
from factory.db import db_session_factory
from rest import fields
from rest.alchemy.manager import AlchemyResourceManager
from rest.authentication import SessionAuthenticator
from rest.exceptions import ValidationError
from rest.resource import Resource
from resources.chat_session import ChatSessionResource
from settings import CDN_URL, CDN_SSL_URL, CDN_STREAMING_URL

class ArchiveTypeEnum(Enum):
    model_class = ChatArchiveType
    key_column = "name"
    value_column = "id"
    db_session_factory = db_session_factory

class ArchiveTypeField(fields.StringField):
    def to_model(self, value):
        value = super(ArchiveTypeField, self).to_model(value)
        if value in ArchiveTypeEnum.VALUES_TO_KEYS:
            pass
        elif value in ArchiveTypeEnum.KEYS_TO_VALUES:
            value = ArchiveTypeEnum.KEYS_TO_VALUES[value]
        else:
            raise ValidationError("'%s' invalid type" % value)
        return value

    def to_python(self, value):
        value = super(ArchiveTypeField, self).to_python(value)
        if value in ArchiveTypeEnum.KEYS_TO_VALUES:
            pass
        else:
            try:
                value = ArchiveTypeEnum.VALUES_TO_KEYS[int(value)]
            except:
                raise ValidationError("'%s' invalid type" % value)
        return value

class MimeTypeEnum(Enum):
    model_class = MimeType
    key_column = "type"
    value_column = "id"
    db_session_factory = db_session_factory

class MimeTypeField(fields.StringField):
    def to_model(self, value):
        value = super(MimeTypeField, self).to_model(value)
        if value in MimeTypeEnum.VALUES_TO_KEYS:
            pass
        elif value in MimeTypeEnum.KEYS_TO_VALUES:
            value = MimeTypeEnum.KEYS_TO_VALUES[value]
        else:
            raise ValidationError("'%s' invalid type" % value)
        return value

    def to_python(self, value):
        value = super(MimeTypeField, self).to_python(value)
        if value in MimeTypeEnum.KEYS_TO_VALUES:
            pass
        else:
            try:
                value = MimeTypeEnum.VALUES_TO_KEYS[int(value)]
            except:
                raise ValidationError("'%s' invalid type" % value)
        return value

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
        value = "%s/%s" % (self.cdn_url, value)
        return value

class ArchiveResource(Resource):
    class Meta:
        resource_name = "archives"
        model_class = ChatArchive
        methods = ["GET"]
        bulk_methods = ["GET"]

        filtering = {
            "id": ["eq"],
            "chat_session__id": ["eq"]
        }    

        limit = 20

    id = fields.IntegerField(primary_key=True, readonly=True)
    type = ArchiveTypeField(model_attname="type_id", readonly=True)
    mime_type = MimeTypeField(model_attname="mime_type_id", readonly=True)
    chat_session_id = fields.EncodedField(readonly=True)
    path = fields.StringField(readonly=True)
    url = CdnUrlField(cdn_url=CDN_URL, model_attname="path", readonly=True)
    ssl_url = CdnUrlField(cdn_url=CDN_SSL_URL, model_attname="path", readonly=True)
    streaming_url = CdnUrlField(cdn_url=CDN_STREAMING_URL, model_attname="path", readonly=True)
    public = fields.BooleanField(readonly=True)
    length = fields.IntegerField(nullable=True, readonly=True)
    offset = fields.IntegerField(nullable=True, readonly=True)

    chat_session = fields.EncodedForeignKey(ChatSessionResource, backref="archives", model_name="chat_session", model_attname="chat_session_id")

    objects = AlchemyResourceManager(db_session_factory)
    authenticator = SessionAuthenticator()

