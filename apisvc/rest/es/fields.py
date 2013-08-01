from tres.query import CustomScoreQuery, MatchAllQuery, MatchQuery,\
        MultiMatchQuery

from rest import fields

class QueryField(fields.StringField):
    def __init__(self, **kwargs):
        super(QueryField, self).__init__(**kwargs)
    
    def build_query(self, q):
        pass

class MatchQueryField(QueryField):
    def __init__(self, es_field, **kwargs):
        super(MatchQueryField, self).__init__(**kwargs)
        self.es_field = es_field
    
    def build_query(self, query):
        q = None
        for f in query.filters:
            op = f.operation
            if op.target_field.name == self.name and op.name == 'eq':
                q = op.operands[0]
        if q:
            return MatchQuery(q, self.es_field)
        else:
            return None

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

class CustomScoreMultiMatchQueryField(QueryField):
    def __init__(self, es_score_field, es_fields, **kwargs):
        super(CustomScoreMultiMatchQueryField, self).__init__(**kwargs)
        self.es_fields = es_fields
        self.es_score_field = es_score_field

    
    def build_query(self, query):
        q = None
        for f in query.filters:
            op = f.operation
            if op.target_field.name == self.name and op.name == 'eq':
                q = op.operands[0]
        if q:
            return CustomScoreQuery(
                    MultiMatchQuery(q, self.es_fields),
                    "_score * doc['%s'].value" % self.es_score_field)
        else:
            return CustomScoreQuery(MatchAllQuery(),
                    "_score * doc['%s'].value" % self.es_score_field)
