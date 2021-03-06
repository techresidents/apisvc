import datetime

import pytz

from trpycore.encode.basic import basic_encode, basic_decode
from trpycore.timezone import tz
from rest.exceptions import ValidationError

class Field(object):
    STOP = "__STOP__"

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
            to_model=None,
            **kwargs):
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
        self.options = kwargs

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

    def read(self, formatter):
        raise RuntimeError("read not supported")

    def write(self, formatter, value):
        raise RuntimeError("write not supported")

class StringField(Field):
    def to_python(self, value):
        result = value
        if value is None:
            pass
        elif not isinstance(value, basestring):
            result = str(value)
        return result

    def read(self, formatter):
        return self.validate(formatter.read_string())

    def write(self, formatter, value):
        formatter.write_string(self.validate(value))

class UriField(Field):
    def read(self, formatter):
        return self.validate(formatter.read_uri())

    def write(self, formatter, value):
        formatter.write_uri(self.validate(value))

class EncodedField(StringField):
    def to_python(self, value):
        result = value
        if value is None:
            pass
        elif isinstance(value, int):
            result = basic_encode(value)
        elif not isinstance(value, basestring):
            result = str(value)
        return result

    def to_model(self, value):
        result = value
        if value is None:
            pass
        elif isinstance(value, basestring):
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

    def read(self, formatter):
        return self.validate(formatter.read_integer())

    def write(self, formatter, value):
        formatter.write_integer(self.validate(value))

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

    def read(self, formatter):
        return self.validate(formatter.read_float())

    def write(self, formatter, value):
        formatter.write_float(self.validate(value))

class BooleanField(Field):
    def to_python(self, value):
        result = value
        if value is None:
            pass
        elif value in (True, False):
            #if 0 or 1 convert to bool
            result = bool(value)
        elif value in ["t", "T",  "True", "true", "1"]:
            result = True
        elif value in ["f", "F", "False", "false", "0"]:
            result = False
        else:
            raise ValidationError("invalid boolean '%s'" % str(value))
        return result

    def read(self, formatter):
        return self.validate(formatter.read_boolean())

    def write(self, formatter, value):
        formatter.write_boolean(self.validate(value))

class DateField(Field):
    def to_python(self, value):
        result = None

        if value is None:
            result = None
        elif isinstance(value, datetime.datetime):
            result = value.replace(tzinfo=pytz.utc)
        elif isinstance(value, datetime.date):
            dt = datetime.datetime(value.year, value.month, value.day)
            result = dt.replace(tzinfo=pytz.utc)
        elif isinstance(value, (int, float)):
            result = tz.timestamp_to_utc(value)
        elif isinstance(value, basestring):
            result = tz.iso_to_utc(value) or tz.now_to_utc(value)
            if result is None:
                try:
                    result = tz.timestamp_to_utc(float(value))
                except:
                    raise ValidationError("invalid date '%s'" % str(value))
        else :
            raise ValidationError("invalid date '%s'" % str(value))
        return result

    def read(self, formatter):
        return self.validate(formatter.read_date())

    def write(self, formatter, value):
        formatter.write_date(self.validate(value))

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
        elif isinstance(value, (int, float)):
            result = tz.timestamp_to_utc(value)
        elif isinstance(value, basestring):
            result = tz.iso_to_utc(value) or tz.now_to_utc(value)
            if result is None:
                try:
                    result = tz.timestamp_to_utc(float(value))
                except:
                    raise ValidationError("invalid datetime '%s'" % str(value))
        else :
            raise ValidationError("invalid datetime '%s'" % str(value))
        return result

    def read(self, formatter):
        return self.validate(formatter.read_datetime())

    def write(self, formatter, value):
        formatter.write_datetime(self.validate(value))

class TimestampField(FloatField):
    def read(self, formatter):
        return self.validate(formatter.read_timestamp())

    def write(self, formatter, value):
        formatter.write_timestamp(self.validate(value))

class ListField(Field):
    def __init__(self, field=None, **kwargs):
        self.field = field
        if "default" not in kwargs:
            kwargs["default"] = lambda: []
        super(ListField, self).__init__(**kwargs)

    def read(self, formatter):
        result = []
        length = formatter.read_list_begin()
        for i in range(length):
            if self.field:
                value = self.field.read(formatter)
            else:
                value = formatter.read_dynamic()
            result.append(value)
        formatter.read_list_end()
        return result

    def write(self, formatter, values):
        values = values or []
        formatter.write_list_begin(len(values))
        for value in values:
            if self.field:
                self.field.write(formatter, value)
            else:
                formatter.write_dynamic(value)
        formatter.write_list_end()

class DictField(Field):
    def __init__(self, key_field=None, value_field=None, **kwargs):
        self.key_field = key_field
        self.value_field = value_field
        if "default" not in kwargs:
            kwargs["default"] = lambda: {}
        super(DictField, self).__init__(**kwargs)

    def read(self, formatter):
        result = {}
        length = formatter.read_dict_begin()
        for i in range(length):
            if self.key_field:
                key = self.key_field.read(formatter)
            else:
                key = formatter.read_dynamic()
            
            if self.value_field:
                value = self.value_field.read(formatter)
            else:
                value = formatter.read_dynamic()
            result[key] = value
        formatter.read_dict_end()
        return result

    def write(self, formatter, values):
        values = values or {}
        formatter.write_dict_begin(len(values))
        for key, value in values.items():
            if self.key_field:
                self.key_field.write(formatter, key)
            else:
                formatter.write_dynamic(key)
            
            if self.value_field:
                self.value_field.write(formatter, value)
            else:
                formatter.write_dynamic(value)
        formatter.write_dict_end()

class EnumField(StringField):
    def __init__(self, keys_to_values, values_to_keys=None,  **kwargs):
        super(EnumField, self).__init__(**kwargs)
        self.keys_to_values = keys_to_values
        self.values_to_keys = values_to_keys
        if self.values_to_keys is None:
            self.values_to_keys = {}
            for key, value in self.keys_to_values.items():
                self.values_to_keys[value] = key

    def to_model(self, value):
        value = super(EnumField, self).to_model(value)
        if value in self.values_to_keys:
            pass
        elif value in self.keys_to_values:
            value = self.keys_to_values[value]
        else:
            raise ValidationError("'%s' invalid type" % value)
        return value

    def to_python(self, value):
        value = super(EnumField, self).to_python(value)
        if value in self.keys_to_values:
            pass
        else:
            try:
                value = self.values_to_keys[int(value)]
            except:
                raise ValidationError("'%s' invalid type" % value)
        return value

class StructField(Field):
    def __init__(self, struct_class, model_struct_class=None, **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = lambda: struct_class()
        super(StructField, self).__init__(**kwargs)
        self.struct_class = struct_class
        self.model_struct_class = model_struct_class or dict
    
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
        if value is not None:
            for field in self.struct_class.desc.fields:
                attribute = getattr(value, field.attname)
                field_value = field.validate(attribute)
                setattr(value, field.attname, field_value)
        return value

    def validate_for_model(self, value):
        value = super(StructField, self).validate_for_model(value)
        if value is not None:
            for field in self.struct_class.desc.fields:
                attribute = getattr(value, field.model_attname)
                field_value = field.validate_for_model(attribute)
                setattr(value, field.model_attname, field_value)
        return value

    def read(self, formatter):
        result = self.get_default() or self.struct_class()
        formatter.read_struct_begin()
        fields_read = 0
        while True:
            field_name = formatter.read_field_begin()
            if field_name == Field.STOP:
                break
            
            fields_read += 1
            field = self.struct_class.desc.fields_by_name.get(field_name)
            if field is None:
                raise RuntimeError("invalid field: %s" % field_name)
            field_value = field.read(formatter)
            if not field.readonly:
                setattr(result, field.attname, field_value)
            formatter.read_field_end()
        formatter.read_struct_end()

        if fields_read == 0:
            result = None

        return result

    def write(self, formatter, value):
        write_fields = lambda fields: [f for f in fields if not f.hidden]
        value = self.validate(value)

        if value is None:
            formatter.write_dynamic(None)
        else:
            formatter.write_struct_begin()
            for field in write_fields(self.struct_class.desc.fields):
                formatter.write_field_begin(field.attname, field)
                field_value = getattr(value, field.attname)
                field.write(formatter, field_value)
                formatter.write_field_end()
            formatter.write_field_stop()
            formatter.write_struct_end()
