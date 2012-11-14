from rest.exceptions import InvalidQuery

class WithRelation(object):
    def __init__(self, related_fields):
        self.related_fields = related_fields

    def name(self):
        relations = "__".join([f.name for f in self.related_fields])
        return relations

    @staticmethod
    def parse(resource_class, **kwargs):
        results = []
        for arg, value in kwargs.items():
            current = resource_class
            parts = arg.split("__")
        
            related_fields = []
        
            for part in parts:
                if part in current.desc.related_fields_by_name:
                    field = current.desc.related_fields_by_name[part]
                    related_fields.append(field)
                    current = field.relation
                else:
                    raise InvalidQuery("invalid with relation '%s'" % arg)
        
            results.append(WithRelation(related_fields))

        return results
