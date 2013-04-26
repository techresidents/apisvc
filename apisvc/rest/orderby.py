from rest.exceptions import InvalidQuery
from rest.fields import ListField, StructField

DIRECTIONS = {
    "ASC": "ASC",
    "DESC": "DSC",
}

class OrderBy(object):
    def __init__(self, path_fields, target_field, direction):
        self.path_fields = path_fields
        self.target_field = target_field
        self.direction = direction
    
    def name(self):
        path = "__".join([f.name for f in self.path_fields])
        target = self.target_field.attname
        if path:
            result = "%s__%s" % (path, target)
        else:
            result = target
        return result

    @staticmethod
    def parse(resource_class, **kwargs):
        results = []
        for arg, value in kwargs.items():
            current = resource_class
            parts = arg.split("__")
        
            path_fields = []
            target_field = None

            if parts[-1].upper() in DIRECTIONS:
                direction = parts[-1].upper()
                parts = parts[:-1]
            else:
                direction = DIRECTIONS["ASC"]
        
            for part in parts:
                if part in current.desc.fields_by_name:
                    field = current.desc.fields_by_name[part]
                    if isinstance(field, StructField):
                        current = field
                        path_fields.append(field)
                    elif isinstance(field, ListField) and \
                       isinstance(field.field, StructField):
                        current = field.field.struct_class
                        path_fields.append(field)
                    else:
                        #target field should be the last part
                        if parts[-1] != part:
                            raise InvalidQuery("invalid order_by '%s'" % arg)
                        target_field = field
                    target_field = field
        
                elif part in current.desc.related_fields_by_name:
                    field = current.desc.related_fields_by_name[part]
                    path_fields.append(field)
                    current = field.relation
                else:
                    raise InvalidQuery("invalid order_by '%s'" % arg)
        
            primary_key = current.desc.primary_key
            target_field = target_field or current.desc.fields_by_name[primary_key]
            results.append(OrderBy(path_fields, target_field, direction))
        return results
