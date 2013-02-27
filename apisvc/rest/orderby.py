from rest.exceptions import InvalidQuery

DIRECTIONS = {
    "ASC": "ASC",
    "DESC": "DSC",
}

class OrderBy(object):
    def __init__(self, related_fields, target_field, direction):
        self.related_fields = related_fields
        self.target_field = target_field
        self.direction = direction
    
    def name(self):
        relations = "__".join([f.name for f in self.related_fields])
        target = self.target_field.attname
        if relations:
            result = "%s__%s" % (relations, target)
        else:
            result = target
        return result

    @staticmethod
    def parse(resource_class, **kwargs):
        results = []
        for arg, value in kwargs.items():
            current = resource_class
            parts = arg.split("__")
        
            related_fields = []
            target_field = None

            if parts[-1].upper() in DIRECTIONS:
                direction = parts[-1].upper()
                parts = parts[:-1]
            else:
                direction = DIRECTIONS["ASC"]
        
            for part in parts:
                if part in current.desc.fields_by_name:
                    field = current.desc.fields_by_name[part]
                    target_field = field
        
                    #target field should be the last part
                    if parts[-1] != part:
                        raise InvalidQuery("invalid order_by '%s'" % arg)
        
                elif part in current.desc.related_fields_by_name:
                    field = current.desc.related_fields_by_name[part]
                    related_fields.append(field)
                    current = field.relation
                else:
                    raise InvalidQuery("invalid order_by '%s'" % arg)
        
            primary_key = current.desc.primary_key
            target_field = target_field or current.desc.fields_by_name[primary_key]
            results.append(OrderBy(related_fields, target_field, direction))
        return results
