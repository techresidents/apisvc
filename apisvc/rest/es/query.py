from tres_gevent.query import BoolQuery, FilteredQuery, MatchAllQuery
from tres_gevent.search import Search
from tres_gevent.filter import BoolFilter, RangeFilter, TermFilter, TermsFilter
from tres_gevent.facet import Facets
from tres_gevent.sort import Sort

from rest.es.fields import QueryField
from rest.query import Query

ES_OPERATIONS = {
    "eq": lambda f, v: TermFilter(f, v),
    "in": lambda f, *v: TermsFilter(f, v),
    "lt": lambda f, v: RangeFilter(f, end=v, include_end=False),
    "gt": lambda f, v: RangeFilter(f, start=v, include_start=False),
    "lte": lambda f, v: RangeFilter(f, end=v),
    "gte": lambda f, v: RangeFilter(f, start=v),
    "range": lambda f, *v: RangeFilter(f, *v),
    "ranges": lambda f, *v: BoolFilter(should=[RangeFilter(f,s,e) for s,e in v])
}

class ElasticSearchQuery(Query):
    def __init__(self, 
            resource_class,
            es_index_name,
            es_doc_name,
            es_client_pool):
        super(ElasticSearchQuery, self).__init__(resource_class)
        
        self.es_index_name = es_index_name
        self.es_doc_name = es_doc_name
        self.es_client_pool = es_client_pool
        self.query_fields = {}

        for field in self.resource_class.desc.fields:
            if isinstance(field, QueryField):
                self.query_fields[field.name] = field

    def _build_search(self):
        search = Search()
        search.query = self._build_query()
        search = self._apply_filters(search)
        search = self._apply_order_bys(search)
        search = self._apply_slices(search)
        search = self._apply_facets(search)
        return search

    def _build_query(self):
        es_queries = []
        for field in self.query_fields.values():
            es_query = field.build_query(self)
            if es_query is not None:
                es_queries.append(es_query)
        
        if len(es_queries) == 0:
            query = MatchAllQuery()
        elif len(es_queries) == 1:
            query = es_queries[0]
        else:
            query = BoolQuery(must=es_queries)
        
        return query

    def _apply_filters(self, search):
        es_filters = []
        for filter in self.filters:
            target_field = filter.operation.target_field
            if not isinstance(target_field, QueryField):
                path = [f.model_attname for f in filter.path_fields]
                path.append(target_field.model_attname)

                es_field = ".".join(path)
                if target_field.options.get("filter_ext"):
                    es_field += target_field.options.get("filter_ext")
                operands = filter.operation.map_operands(
                        filter.operation.target_field.validate_for_model)
                es_filter = ES_OPERATIONS[filter.operation.name](es_field, *operands)
                es_filters.append(es_filter)
        
        f = None
        if len(es_filters) == 1:
            f = es_filters[0]
        elif len(es_filters) > 1:
            f = BoolFilter(must=es_filters)
        
        if f is not None:
            search.query = FilteredQuery(search.query, f)
        
        return search
    
    def _apply_order_bys(self, search):
        es_sort = Sort()
        for order_by in self.order_bys:
            target_field = order_by.target_field
            if not isinstance(target_field, QueryField):
                # Convert path__target to path.target.raw
                path = [f.model_attname for f in order_by.path_fields]
                path.append(target_field.model_attname)
                es_field = ".".join(path)
                if target_field.options.get("sort_ext"):
                    es_field += target_field.options.get("sort_ext")
                    es_sort.add(es_field, order_by.direction)
        if es_sort.length():
            search.sort = es_sort
        return search
    
    def _apply_slices(self, search):
        search.start = self.slices[0]
        search.size = self.slices[1] - self.slices[0]
        return search

    def _apply_facets(self, search):
        es_facets = {}
        facets = self.resource_class.desc.facets
        for facet in facets:
            es_facet = facet.build_es_facet(self)
            es_facets[facet.name] = es_facet
        
        if len(es_facets):
            search.facets = Facets(es_facets)

        return search

    def all(self):
        resources = self.resource_class.Collection()
        search = self._build_search()
        with self.es_client_pool.get() as client:
            index = client.get_index(self.es_index_name, self.es_doc_name)
            search_result = index.search(search)
        
        for hit in search_result.hits:
            resource = self.model_to_resource(hit.source,
                    excludes=self.query_fields.keys())
            resources.append(resource)
        resources.total_count = search_result.hits_total
        
        for name, es_facet in search_result.facets.items():
            facet = self.resource_class.desc.facets_by_name[name]
            resources.facets.append(facet.build_facet_struct(self, search_result))
        
        self._apply_with_relations(resources)
        return resources
