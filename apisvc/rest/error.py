import rest.fields as fields
from rest.struct import Struct

class Error(Struct):
    code = fields.IntegerField()
    message = fields.StringField()
    developerMessage = fields.StringField(nullable=True)
