from tres.query import MultiMatchQuery

from rest import fields

class QueryField(fields.StringField):
    def __init__(self, **kwargs):
        super(QueryField, self).__init__(**kwargs)
    
    def build_query(self, q):
        pass

class MultiMatchQueryField(QueryField):
    def __init__(self, es_fields, **kwargs):
        super(MultiMatchQueryField, self).__init__(**kwargs)
        self.es_fields = es_fields
    
    def build_query(self, query):
        q = None
        for f in query.filters:
            op = f.operation
            if op.target_field.name == self.name and op.name == 'eq':
                q = op.operands[0]
        if q:
            return MultiMatchQuery(q, self.es_fields)
        else:
            return None
