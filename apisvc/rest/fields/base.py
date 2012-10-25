import datetime

import pytz

from trpycore.encode.basic import basic_encode, basic_decode
from trpycore.timezone import tz
from rest.exceptions import ValidationError

class Field(object):
    NO_DEFAULT = object()

    def __init__(self,
            name=None,
            model_class=None,
            model_name=None,
            model_attname=None,
            default=None,
            primary_key=False,
            nullable=False,
            readonly=False,
            hidden=False,
            through=None,
            to_model=None):
        self.name = name
        self.model_class = model_class
        self.model_name = model_name or name
        self.model_attname = model_attname
        self.primary_key = primary_key
        self.nullable = nullable
        self.readonly = readonly
        self.hidden = hidden
        self.through = through
        self.to_model_method = to_model
        
        #Resource or Struct class
        self.container_class = None

        self.default = default
        self.attname = self.get_attname()

    def contribute_to_class(self, container_class, name):
        self.container_class = container_class
        self.name = name
        self.model_name = self.model_name  or name
        self.attname = self.get_attname()
        self.model_attname = self.model_attname or self.get_attname()
        self.model_class = self.model_class or container_class.desc.model_class

        container_class.desc.add_field(self)
    
    def has_default(self):
        return self.default is not self.NO_DEFAULT

    def get_default(self):
        if self.default and callable(self.default):
            return self.default()
        else:
            return self.default
    
    def get_attname(self):
        return self.name

    def get_cache_name(self):
        return "_%s_cache" % (self.name)

    def to_python(self, value):
        return value

    def to_model(self, value):
        if self.to_model_method:
            value = self.to_model_method(value)
        return value
        
    def validate(self, value):
        python_value = self.to_python(value)
        if not self.primary_key and not self.nullable and python_value is None:
            msg = "'%s' not nullable" % self.name
            raise ValidationError(msg)
        return python_value

    def validate_for_model(self, value):
        model_value = self.to_model(value)
        if not self.primary_key and not self.nullable and model_value is None:
            msg = "'%s' not nullable" % self.name
            raise ValidationError(msg)
        return model_value

class StringField(Field):
    def to_python(self, value):
        result = value
        if not isinstance(value, basestring):
            result = str(value)
        return result

class EncodedField(StringField):
    def to_python(self, value):
        result = value
        if isinstance(value, int):
            result = basic_encode(value)
        elif not isinstance(value, basestring):
            result = str(value)
        return result

    def to_model(self, value):
        result = value
        if isinstance(value, basestring):
            result = basic_decode(value)
        return result

class IntegerField(Field):
    def to_python(self, value):
        try:
            if value is None:
                result = None
            else:
                result = int(value)
            return result
        except Exception:
            raise ValidationError("invalid integer '%s'" % str(value))

class FloatField(Field):
    def to_python(self, value):
        try:
            if value is None:
                result = None
            else:
                result = float(value)
            return result
        except Exception:
            raise ValidationError("invalid integer '%s'" % str(value))

class BooleanField(Field):
    def to_python(self, value):
        if value in (True, False):
            #if 0 or 1 convert to bool
            return bool(value)
        elif value in ["t", "T",  "True", "true", "1"]:
            return True
        elif value in ["f", "F", "False", "false", "0"]:
            return False
        else:
            raise ValidationError("invalid boolean '%s'" % str(value))

class DateField(Field):
    def to_python(self, value):
        result = None

        if value is None:
            result = None
        elif isinstance(value, datetime.date):
            result = value
        elif isinstance(value, datetime.datetime):
            result = datetime.date()
        elif isinstance(value, basestring):
            try:
                result = datetime.datetime.strptime(value, '%Y-%m-%d').date()
            except:
                raise ValidationError("invalid date '%s'" % str(value))
        else :
            raise ValidationError("invalid date '%s'" % str(value))
        return result

class DateTimeField(Field):
    def to_python(self, value):
        result = None

        if value is None:
            result = None
        elif isinstance(value, datetime.datetime):
            result = value.replace(tzinfo=pytz.utc)
        elif isinstance(value, datetime.date):
            dt = datetime.datetime(value.year, value.month, value.day)
            result = dt.replace(tzinfo=pytz.utc)
        elif isinstance(value, (int, float, basestring)):
            try:
                result = tz.timestamp_to_utc(float(value))
            except:
                raise ValidationError("invalid datetime '%s'" % str(value))
        else :
            raise ValidationError("invalid datetime '%s'" % str(value))
        return result

class TimestampField(FloatField):
    pass

class ListField(Field):
    pass

class DictField(Field):
    pass

class StructField(Field):
    def __init__(self, struct_class, model_struct_class, **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = lambda: struct_class()
        super(StructField, self).__init__(**kwargs)
        self.struct_class = struct_class
        self.model_struct_class = model_struct_class
    
    def to_python(self, value):
        result = None
        if value is None:
            result = None
        elif isinstance(value, self.struct_class):
            result = value
        elif isinstance(value, dict):
            result = self.struct_class(**value)
        elif isinstance(value, self.model_struct_class):
            kwargs = {}
            for field in self.struct_class.desc.fields:
                attribute = getattr(value, field.model_attname)
                kwargs[field.attname] = field.to_python(attribute)
            result = self.struct_class(**kwargs)
        else:
            raise ValidationError("invalid struct '%s'" % str(value))
        return result
    
    def to_model(self, value):
        result = None
        if value is None:
            result = None
        elif isinstance(value, self.model_struct_class):
            result = value
        elif isinstance(value, self.struct_class):
            kwargs = {}
            for field in self.struct_class.desc.fields:
                attribute = getattr(value, field.attname)
                kwargs[field.model_attname] = field.to_model(attribute)
            result = self.model_struct_class(**kwargs)
        else:
            raise ValidationError("invalid struct '%s'" % str(value))
        return result

    def validate(self, value):
        value = super(StructField, self).validate(value)
        for field in self.struct_class.desc.fields:
            attribute = getattr(value, field.attname)
            field_value = field.validate(attribute)
            setattr(value, field.attname, field_value)
        return value

    def validate_for_model(self, value):
        value = super(StructField, self).validate_for_model(value)
        for field in self.struct_class.desc.fields:
            attribute = getattr(value, field.model_attname)
            field_value = field.validate_for_model(attribute)
            setattr(value, field.model_attname, field_value)
        return value
