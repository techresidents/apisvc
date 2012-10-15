from rest.fields import BooleanField, DateField, DateTimeField, DictField, FloatField, \
        ForeignKey, IntegerField, ListField, RelatedField, StringField, TimestampField

class Format:
    JSON = "JSON"

class Formatter(object):
    def __init__(self, buffer):
        self.buffer = buffer
        self.api = None

    def read(self, api, result):
        self.api = api
        if isinstance(result, (list, tuple)):
            return self.read_resources(api, result)
        else:
            return self.read_resource(api, result)

    def read_resources(self, api, resources=None):
        self.api = api
        resources = resources or []
        length = self.read_list_begin()
        for i in range(length):
            resource = self.read_resource(api)
            resources.append(resource)
        self.read_list_end()
        return resources
    
    def read_resource(self, api, resource=None):
        self.api = api
        working_resource, fields_length = self.read_resource_begin()
        resource = resource or working_resource
        for j in range(fields_length):
            field = self.read_field_begin()
            if isinstance(field, ForeignKey):
                value = self.read_dynamic()
                if isinstance(value, dict):
                    value = self.read_resource(api)
                    setattr(resource, field.name, value)
                elif isinstance(value, basestring) and value.startswith("/"):
                    pass
                else:
                    value = self.read_dynamic()
                    setattr(resource, field.attname, value)
                self.read_field_end(field)

            elif isinstance(field, RelatedField):
                value = self.read_dynamic()
                if isinstance(value, basestring) and value.startswith("/"):
                    pass
                else:
                    value = self.read_resources(api)
                    setattr(resource, field.name, value)
                self.read_field_end(field)
            else:
                if isinstance(field, BooleanField):
                    value = self.read_boolean()
                    value = field.validate(value)
                elif isinstance(field, DateField):
                    value = self.read_date()
                    value = field.validate(value)
                elif isinstance(field, DateTimeField):
                    value = self.read_datetime()
                    value = field.validate(value)
                elif isinstance(field, DictField):
                    value = {}
                    length = self.read_dict_begin()
                    for i in range(length):
                        value.update(self.read_dynamic())
                    self.read_dict_end()
                elif isinstance(field, FloatField):
                    value = self.read_float()
                    value = field.validate(value)
                elif isinstance(field, IntegerField):
                    value = self.read_integer()
                    value = field.validate(value)
                elif isinstance(field, ListField):
                    value = []
                    length = self.read_list_begin()
                    for i in range(length):
                        value.append(self.read_dynamic())
                    self.read_list_end()
                elif isinstance(field, StringField):
                    value = self.read_string()
                    value = field.validate(value)
                elif isinstance(field, TimestampField):
                    value = self.read_timestamp()
                else:
                    raise RuntimeError("unsupoorted field")

                setattr(resource, field.attname, value)
                self.read_field_end(field)

        self.read_resource_end(resource)
        return resource

    def write(self, api, resources):
        self.api = api
        if isinstance(resources, (list, tuple)):
            self.write_resources(api, resources)
        else:
            self.write_resource(api, resources)

    def write_resources(self, api, resources):
        self.api = api
        self.write_list_begin(len(resources))
        for resource in resources:
            self.write_resource(api, resource)
        self.write_list_end()

    def write_resource(self, api, resource):
        self.api = api
        self.write_resource_begin(resource)
        for field in resource.desc.fields:
            if field.hidden:
                continue

            self.write_field_begin(field, field.attname)

            if isinstance(field, BooleanField):
                self.write_boolean(getattr(resource, field.attname))
            elif isinstance(field, DateField):
                self.write_date(getattr(resource, field.attname))
            elif isinstance(field, DateTimeField):
                self.write_datetime(getattr(resource, field.attname))
            elif isinstance(field, DictField):
                values = getattr(resource, field.attname) or {}
                self.write_dict_begin(len(values))
                for key, value in values.items():
                    self.write_dynamic({key: value})
                self.write_dict_end()
            elif isinstance(field, ForeignKey):
                self.write_dynamic(getattr(resource, field.attname))
            elif isinstance(field, FloatField):
                self.write_float(getattr(resource, field.attname))
            elif isinstance(field, IntegerField):
                self.write_integer(getattr(resource, field.attname))
            elif isinstance(field, ListField):
                values = getattr(resource, field.attname) or []
                self.write_list_begin(len(values))
                for value in values:
                    self.write_dynamic(value)
                self.write_list_end()
            elif isinstance(field, StringField):
                self.write_string(getattr(resource, field.attname))
            elif isinstance(field, TimestampField):
                self.write_timestamp(getattr(resource, field.attname))
            else:
                raise RuntimeError("unsupported field")

            self.write_field_end(field)

        for field in resource.desc.related_fields:
            if field.hidden:
                continue
            related_descriptor = getattr(resource.__class__, field.name)
            if related_descriptor.is_loaded(resource):
                resources = getattr(resource, field.name)
                self.write_field_begin(field, field.name)
                if field.many:
                    self.write_resources(api, resources)
                else:
                    self.write_resource(api, resources)
                self.write_field_end(field)
            else:
                if isinstance(field, ForeignKey):
                    fk = getattr(resource, field.attname)
                    if fk is None:
                        link = None
                    else:
                        link = "%s/%s/%s" % \
                        (api.base_uri, field.relation.desc.resource_name, fk)
                else:
                    primary_key = resource.primary_key_value()
                    link = "%s/%s/%s/%s" % \
                    (api.base_uri, resource.desc.resource_name, primary_key, field.name)
                self.write_field_begin(field, field.name)
                self.write_string(link)
                self.write_field_end(field)

        self.write_resource_end(resource)


    def read_dict_begin(self):
        pass

    def read_dict_end(self):
        pass

    def read_list_begin(self):
        pass

    def read_list_end(self):
        pass

    def read_resource_begin(self):
        pass
        
    def read_resource_end(self, resource):
        pass

    def read_field_begin(self):
        pass

    def read_field_end(self, field):
        pass

    def read_dynamic(self):
        pass

    def read_boolean(self):
        pass

    def read_date(self):
        pass

    def read_datetime(self):
        pass

    def read_float(self):
        pass

    def read_integer(self):
        pass

    def read_string(self):
        pass

    def read_timestamp(self):
        pass

    def write_dict_begin(self, length):
        pass

    def write_dict_end(self):
        pass

    def write_list_begin(self, length):
        pass

    def write_list_end(self):
        pass

    def write_resource_end(self, resource):
        pass
    
    def write_field_begin(self, field, field_attname):
        pass

    def write_field_end(self, field):
        pass

    def write_dynamic(self, value):
        pass

    def write_boolean(self, value):
        pass

    def write_date(self, value):
        pass

    def write_datetime(self, value):
        pass

    def write_float(self, value):
        pass

    def write_integer(self, value):
        pass

    def write_string(self, value):
        pass
    
    def write_timestamp(self, value):
        pass
