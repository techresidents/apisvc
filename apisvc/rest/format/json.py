from __future__ import absolute_import

import json

from trpycore.timezone import tz
from rest.format.base import Formatter

class DictContext(object):
    def __init__(self, json_data=None, parent_context=None):
        self.parent_context = parent_context
        self.position = 0
        self.json_data = json_data
    def read(self):
        key = self.json_data.keys()[self.position]
        value = self.json_data[key]
        self.position +=1
        return {key, value}
    def write(self, data):
        key, value = data.items()[0]
        self.json_data[key] = value

class ListContext(object):
    def __init__(self, json_data=None, parent_context=None):
        self.parent_context = parent_context
        self.position = 0
        self.json_data = json_data
    def read(self):
        result = self.json_data[self.position]
        self.position +=1
        return result
    def write(self, data):
        self.json_data.append(data)

class ResourceContext(object):
    def __init__(self, resource, json_data=None, parent_context=None):
        self.resource = resource
        self.json_data = json_data
        self.parent_context = parent_context
        self.position = 0
    def read(self):
        keys = self.json_data.keys()
        key = keys[self.position]
        value = self.json_data[key]
        self.position += 1
        result = {key: value}
        return result
    def write(self, v):
        key, value = v.items()[0]
        self.json_data[key] = value

class FieldContext(object):
    def __init__(self, parent_context, json_data, field, field_attname):
        self.parent_context = parent_context
        self.json_data = json_data
        self.field = field
        self.field_attname = field_attname
        self.resource = parent_context.resource
    def read(self):
        value = self.json_data[self.field_attname]
        return self.field.validate(value)
    def write(self, value):
        self.json_data[self.field_attname] = value

class JsonFormatter(Formatter):
    
    def __init__(self, buffer):
        self.buffer = buffer
        self.context_stack = []

    def read_dict_begin(self):
        if self.context_stack:
            parent_context = self.context_stack[-1]
            context = DictContext(
                parent_context=parent_context,
                json_data=parent_context.read())
        else:
            context = DictContext(json_data=json.loads(self.buffer.read()))
            
        self.context_stack.append(context)
        return len(context.json_data)

    def read_dict_end(self):
        self.context_stack.pop()
    
    def read_list_begin(self):
        if self.context_stack:
            parent_context = self.context_stack[-1]
            context = ListContext(
                parent_context=parent_context,
                json_data=parent_context.read())
        else:
            context = ListContext(json_data=json.loads(self.buffer.read()))
            
        self.context_stack.append(context)
        return len(context.json_data)

    def read_list_end(self):
        self.context_stack.pop()

    def read_resource_begin(self):
        if self.context_stack:
            parent_context = self.context_stack[-1]
            json_data = parent_context.read()
        else:
            parent_context = None
            json_data = json.loads(self.buffer.read())
        
        meta = json_data.pop("meta")
        resource_class = self.api.get_resource_class(meta["resource_name"])
        resource = resource_class()

        context = ResourceContext(
                resource=resource,
                json_data=json_data,
                parent_context=parent_context)

        self.context_stack.append(context)
        return resource, len(json_data.keys())
        
    def read_resource_end(self, resource):
        self.context_stack.pop()

    def read_field_begin(self):
        resource_context = self.context_stack[-1]
        resource = resource_context.resource
        json_data = resource_context.read()
        try:
            field_attname = json_data.keys()[0]
            field = resource.desc.fields_by_name[field_attname]
        except KeyError:
            field = resource.desc.related_fields_by_name[field_attname]

        context = FieldContext(resource_context, json_data, field, field_attname)
        self.context_stack.append(context)
        return field

    def read_field_end(self, field):
        self.context_stack.pop()

    def read_dynamic(self):
        context = self.context_stack[-1]
        return context.read()

    def read_boolean(self):
        context = self.context_stack[-1]
        return context.read()

    def read_date(self):
        context = self.context_stack[-1]
        return context.read()

    def read_datetime(self):
        context = self.context_stack[-1]
        timestamp = context.read()
        return tz.timestamp_to_utc(timestamp)

    def read_float(self):
        context = self.context_stack[-1]
        return context.read()

    def read_integer(self):
        context = self.context_stack[-1]
        return context.read()

    def read_string(self):
        context = self.context_stack[-1]
        return context.read()

    def read_timestamp(self):
        context = self.context_stack[-1]
        return context.read()

    def write_dict_begin(self, length):
        json_data = {}
        if self.context_stack:
            parent_context = self.context_stack[-1]
            parent_context.write(json_data)
        else:
            parent_context = None

        context = DictContext(
                parent_context=parent_context,
                json_data=json_data)
        self.context_stack.append(context)

    def write_dict_end(self):
        context = self.context_stack.pop()
        if not self.context_stack:
            self.buffer.write(json.dumps(context.json_data))

    def write_list_begin(self, length):
        json_data = []
        if self.context_stack:
            parent_context = self.context_stack[-1]
            parent_context.write(json_data)
        else:
            parent_context = None

        context = ListContext(
                parent_context=parent_context,
                json_data=json_data)
        self.context_stack.append(context)

    def write_list_end(self):
        context = self.context_stack.pop()
        if not self.context_stack:
            self.buffer.write(json.dumps(context.json_data))

    def write_resource_begin(self, resource):
        json_data = {"meta": {
            "resource_name": resource.desc.resource_name,
            "resource_uri:": self.api.get_resource_uri(resource),
            }
        }

        if self.context_stack:
            parent_context = self.context_stack[-1]
            parent_context.write(json_data)
        else:
            parent_context = None

        context = ResourceContext(
                resource=resource,
                json_data=json_data,
                parent_context=parent_context)
        self.context_stack.append(context)

    def write_resource_end(self, resource):
        context = self.context_stack.pop()
        if not self.context_stack:
            self.buffer.write(json.dumps(context.json_data))
    
    def write_field_begin(self, field, field_attname):
        if self.context_stack:
            parent_context = self.context_stack[-1]
            json_data = parent_context.json_data
        else:
            parent_context = None
            json_data = {}

        context = FieldContext(
                parent_context=parent_context,
                json_data=json_data,
                field=field,
                field_attname=field_attname)
        self.context_stack.append(context)

    def write_field_end(self, field):
        self.context_stack.pop()

    def write_dynamic(self, value):
        context = self.context_stack[-1]
        context.write(value)

    def write_boolean(self, value):
        context = self.context_stack[-1]
        context.write(value)

    def write_date(self, value):
        context = self.context_stack[-1]
        context.write(str(value))

    def write_datetime(self, value):
        context = self.context_stack[-1]
        timestamp = tz.utc_to_timestamp(value)
        context.write(timestamp)

    def write_float(self, value):
        context = self.context_stack[-1]
        context.write(value)

    def write_integer(self, value):
        context = self.context_stack[-1]
        context.write(value)

    def write_string(self, value):
        context = self.context_stack[-1]
        context.write(value)

    def write_timestamp(self, value):
        context = self.context_stack[-1]
        context.write(value)
