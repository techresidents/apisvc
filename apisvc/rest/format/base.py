class Format:
    JSON = "JSON"

class Formatter(object):
    def __init__(self, buffer, api=None):
        self.buffer = buffer
        self.api = api

    def read_dict_begin(self):
        pass

    def read_dict_end(self):
        pass

    def read_list_begin(self):
        pass

    def read_list_end(self):
        pass

    def read_struct_begin(self):
        pass
        
    def read_struct_end(self, struct):
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

    def read_uri(self):
        return self.read_string()

    def write_dict_begin(self, length):
        pass

    def write_dict_end(self):
        pass

    def write_list_begin(self, length):
        pass

    def write_list_end(self):
        pass

    def write_struct_begin(self, struct):
        pass

    def write_struct_end(self, struct):
        pass
    
    def write_field_begin(self, field, field_attname):
        pass

    def write_field_stop(self):
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

    def write_uri(self, value):
        if self.api:
            if value and not value.startswith(self.api.base_uri):
                value = self.api.base_uri + value
        self.write_string(value)
