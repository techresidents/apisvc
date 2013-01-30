from rest import fields
from rest.exceptions import ValidationError

class EnumField(fields.StringField):
    def __init__(self, enum_class, **kwargs):
        super(EnumField, self).__init__(**kwargs)
        self.enum_class = enum_class

    def to_model(self, value):
        value = super(EnumField, self).to_model(value)
        if value in self.enum_class.VALUES_TO_KEYS:
            pass
        elif value in self.enum_class.KEYS_TO_VALUES:
            value = self.enum_class.KEYS_TO_VALUES[value]
        else:
            raise ValidationError("'%s' invalid type" % value)
        return value

    def to_python(self, value):
        value = super(EnumField, self).to_python(value)
        if value in self.enum_class.KEYS_TO_VALUES:
            pass
        else:
            try:
                value = self.enum_class.VALUES_TO_KEYS[int(value)]
            except:
                raise ValidationError("'%s' invalid type" % value)
        return value
