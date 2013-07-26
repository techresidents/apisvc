from rest.exceptions import ValidationError
from rest.fields import ListField

class Option(object):
    NO_DEFAULT = object()

    @staticmethod
    def parse(resource_class, **kwargs):
        options = {}
        for name, value in kwargs.items():
            option = resource_class.desc.options_by_name.get(name, None)
            if option is None:
                raise ValidationError("invalid option")
            options[option.name] = option.validate(value)
        return options

    @staticmethod
    def default_options(resource_class):
        options = {}
        for option in resource_class.desc.options:
            if option.has_default():
                options[option.name] = option.get_default()
        return options

    def __init__(self, name=None, field=None, default=NO_DEFAULT):
        self.name = name
        self.default = default
        self.field = field

    def contribute_to_class(self, container_class, name):
        self.container_class = container_class
        self.name = name
        container_class.desc.add_option(self)

    def has_default(self):
        return self.default is not self.NO_DEFAULT

    def get_default(self):
        if self.default and callable(self.default):
            return self.default()
        else:
            return self.default
    
    def validate(self, value):
        if self.field:
            if isinstance(self.field, ListField):
                value = value.split(',')
            return self.field.validate(value)
        else:
            return value
