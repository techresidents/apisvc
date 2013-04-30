from trpycore.timezone import tz
import tres.facet as esfacet

from rest.facet import Facet, FacetStruct, FacetItemStruct

class ESFacet(Facet):
    def __init__(self, title, field, es_field=None):
        self.title = title
        self.field = field
        self.es_field = es_field or field
    
    def build_es_facet(self, query):
        pass

    def build_facet_struct(self, query, search_result):
        pass


class TermsFacet(ESFacet):
    def __init__(self, title, field, es_field=None, size_option=None):
        super(TermsFacet, self).__init__(title, field, es_field)
        self.size_option = size_option
    
    def build_es_facet(self, query):
        size = 10
        if self.size_option and self.size_option in query.options:
            size = query.options[self.size_option]

        return esfacet.TermsFacet(self.es_field, size)

    def build_facet_struct(self, query, search_result):
        result = FacetStruct(name=self.name, title=self.title)
        es_facet = search_result.facets.get(self.name)
        filter_prefix = self.field + '__in'
        
        current_filters = []
        for f in query.filters:
            if f.name() == filter_prefix:
                current_filters = f.operation.operands
                break

        for term in es_facet.terms:
            name = term.get('term')
            count = term.get('count')
            if name in current_filters:
                on = True
                on_filter = self._filters_to_str(filter_prefix, current_filters)
                off_filter = self._filters_to_str(filter_prefix,
                        filter(lambda f: f != name, current_filters))
            else:
                on = False
                on_filter = self._filters_to_str(filter_prefix,
                        current_filters + [name])
                off_filter = self._filters_to_str(filter_prefix,
                        current_filters)
            
            item = FacetItemStruct(name=name, count=count,
                    on=on, on_filter=on_filter, off_filter=off_filter)
            result.items.append(item)

        return result

    def _filters_to_str(self, filter_prefix, filters):
        operands = ','.join(['%s' % f for f in filters])
        return '%s=%s' % (filter_prefix, operands)


class RangeFacet(ESFacet):
    class Range(object):
        def __init__(self, start=None, end=None,
                include_start=True, include_end=True, name=None):
            self.start = start
            self.end = end
            self.include_start = include_start
            self.include_end = include_end
            self.name = name

    def __init__(self, title, field, ranges=None, es_field=None):
        super(RangeFacet, self).__init__(title, field, es_field)
        self.es_field = es_field or field
        self.ranges = ranges or []

    def add(self, start=None, end=None,
            include_start=True, include_end=True, name=None):
        r = self.Range(start, end, include_start, include_end, name)
        self.ranges.append(r)
        return self
    
    def build_es_facet(self, query):
        result = esfacet.RangeFacet(self.es_field)
        for r in self.ranges:
            result.add_range(
                    start=r.start,
                    end=r.end,
                    include_start=r.include_start,
                    include_end=r.include_end,
                    name=r.name)
        return result

    def build_facet_struct(self, query, search_result):
        result = FacetStruct(name=self.name, title=self.title)
        es_facet = search_result.facets.get(self.name)
        filter_prefix = self.field + '__ranges'

        current_filters = []
        for f in query.filters:
            if f.name() == filter_prefix:
                current_filters = f.operation.parsed_operands
                break

        for search_range, result_range in zip(self.ranges, es_facet.ranges):
            start = search_range.start
            end = search_range.end
            name = search_range.name
            
            count = result_range.get('count')
            if name is None:
                if start is not None and end is not None:
                    name = '%s to %s' % (start, end)
                elif start is not None:
                    name = '%s+' % start
                else:
                    name ='<= %s' % end
            
            r_filter = (str(start), str(end))
            if r_filter in current_filters:
                on = True
                on_filter = self._filters_to_str(filter_prefix, current_filters)
                off_filter = self._filters_to_str(filter_prefix,
                        filter(lambda f: f != r_filter, current_filters))
            else:
                on = False
                on_filter = self._filters_to_str(filter_prefix,
                        current_filters + [r_filter])
                off_filter = self._filters_to_str(filter_prefix,
                        current_filters)

            item = FacetItemStruct(name=name, count=count,
                    on=on, on_filter=on_filter, off_filter=off_filter)
            result.items.append(item)
        return result

    def _filters_to_str(self, filter_prefix, filters):
        operands = ','.join(['%s:%s' % (s,e) for s,e in filters])
        return '%s=%s' % (filter_prefix, operands)


class DateRangeFacet(RangeFacet):
    def __init__(self, title, field, ranges=None, es_field=None):
        super(DateRangeFacet, self).__init__(title, field, ranges, es_field)

    def build_es_facet(self, query):
        result = esfacet.RangeFacet(self.es_field)
        for r in self.ranges:
            start = r.start
            end = r.end

            if isinstance(start, basestring):
                start = tz.iso_to_utc(start) or tz.now_to_utc(start)
            if isinstance(end, basestring):
                end = tz.iso_to_utc(end) or tz.now_to_utc(end)

            result.add_range(
                    start=start,
                    end=end,
                    include_start=r.include_start,
                    include_end=r.include_end,
                    name=r.name)
        return result
