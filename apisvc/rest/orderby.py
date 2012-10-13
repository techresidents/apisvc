class OrderBy(object):
    def __init__(self, related_fields, target_field):
        self.related_fields = related_fields
        self.target_field = target_field
    
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
        
            for part in parts:
                if part in current.desc.fields_by_name:
                    field = current.desc.fields_by_name[part]
                    target_field = field
        
                    #target field should be the last part
                    if parts[-1] != part:
                        raise RuntimeError("invalid filter '%s'" % arg)
        
                elif part in current.desc.related_fields_by_name:
                    field = current.desc.related_fields_by_name[part]
                    related_fields.append(field)
                    current = field.relation
                else:
                    raise RuntimeError("invalid filter '%s'" % arg)
        
            primary_key = current.desc.primary_key
            target_field = target_field or current.desc.fields_by_name[primary_key]
            results.append(OrderBy(related_fields, target_field))
        return results
