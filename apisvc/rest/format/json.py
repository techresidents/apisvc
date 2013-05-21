from __future__ import absolute_import
import datetime
import json

from trpycore.timezone import tz
from rest.format.base import Formatter
from rest.fields import Field

class DictContext(object):
    def __init__(self, json_data=None, parent_context=None):
        self.parent_context = parent_context
        self.position = 0
        self.key = None
        self.json_data = json_data
    def read(self):
        result = None
        if self.key is None:
            self.key = self.json_data.keys()[self.position]
            result = self.key
        else:
            result = self.json_data[self.key]
            self.key = None
            self.position += 1
        return result
    def write(self, data):
        if self.key is None:
            self.key = data
        else:
            self.json_data[self.key] = data
            self.key = None

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

class StructContext(object):
    def __init__(self, json_data=None, parent_context=None):
        self.json_data = json_data
        self.parent_context = parent_context
        self.position = 0
    def read(self):
        if self.json_data is None:
            return None
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
    def __init__(self, parent_context, json_data, field_attname):
        self.parent_context = parent_context
        self.json_data = json_data
        self.field_attname = field_attname
    def read(self):
        value = self.json_data[self.field_attname]
        return value
    def write(self, value):
        self.json_data[self.field_attname] = value

class JsonFormatter(Formatter):
    def __init__(self, buffer, api=None):
        super(JsonFormatter, self).__init__(buffer, api)
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

    def read_struct_begin(self):
        if self.context_stack:
            parent_context = self.context_stack[-1]
            json_data = parent_context.read()
        else:
            parent_context = None
            json_data = json.loads(self.buffer.read())

        context = StructContext(
                json_data=json_data,
                parent_context=parent_context)

        self.context_stack.append(context)
        
    def read_struct_end(self):
        self.context_stack.pop()

    def read_field_begin(self):
        try:
            if self.context_stack:
                parent_context = self.context_stack[-1]
                json_data = parent_context.read()
            else:
                parent_context = None
                json_data = json.loads(self.buffer.read())
            
            #if no fields return Field.STOP.
            #this can happen for nullable structs
            if json_data is None:
                return Field.STOP

            field_attname = json_data.keys()[0]
            context = FieldContext(parent_context, json_data, field_attname)
            self.context_stack.append(context)
            return field_attname
        except IndexError:
            return Field.STOP


    def read_field_end(self):
        self.context_stack.pop()

    def read_dynamic(self):
        context = self.context_stack[-1]
        return context.read()

    def read_boolean(self):
        context = self.context_stack[-1]
        return context.read()

    def read_date(self):
        value = None
        context = self.context_stack[-1]
        isodate = context.read()
        if isodate:
            value = datetime.datetime.strptime(isodate, '%Y-%m-%d').date()
        return value

    def read_datetime(self):
        value = None
        context = self.context_stack[-1]
        timestamp = context.read()
        if timestamp:
            value = tz.timestamp_to_utc(timestamp)
        return value

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

    def write_dict_key(self, key):
        context = self.context_stack[-1]
        context.write_key(key)

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

    def write_struct_begin(self):
        json_data = {}

        if self.context_stack:
            parent_context = self.context_stack[-1]
            parent_context.write(json_data)
        else:
            parent_context = None

        context = StructContext(
                json_data=json_data,
                parent_context=parent_context)
        self.context_stack.append(context)

    def write_struct_end(self):
        context = self.context_stack.pop()
        if not self.context_stack:
            self.buffer.write(json.dumps(context.json_data))

    def write_field_begin(self, field_attname, field):
        if self.context_stack:
            parent_context = self.context_stack[-1]
            json_data = parent_context.json_data
        else:
            parent_context = None
            json_data = {}

        context = FieldContext(
                parent_context=parent_context,
                json_data=json_data,
                field_attname=field_attname)
        self.context_stack.append(context)

    def write_field_stop(self):
        pass

    def write_field_end(self):
        self.context_stack.pop()
    
    def write_dynamic(self, value):
        context = self.context_stack[-1]
        context.write(value)

    def write_boolean(self, value):
        context = self.context_stack[-1]
        context.write(value)

    def write_date(self, value):
        context = self.context_stack[-1]
        if value:
            value = value.isoformat()
        context.write(value.isoformat())

    def write_datetime(self, value):
        context = self.context_stack[-1]
        if value:
            value = tz.utc_to_timestamp(value)
        context.write(value)

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
