from rest.exceptions import InvalidQuery
from rest.fields import BooleanField, ListField, StructField

class Operation(object):
    def __init__(self, name, target_field, operands):
        self.name = name
        self.target_field = target_field
        self.unparsed_operands = operands
        self.parsed_operands = self.parse_operands(operands)
        self.operands = self.validate_operands(self.parsed_operands)

    def parse_operands(self, operands):
        return self._to_list(operands)

    def validate_operands(self, operands):
        return map(self.target_field.validate, operands)

    def map_operands(self, function, validated=True):
        operands = self.operands if validated else self.parsed_operands
        return map(function, operands)

    def _to_list(self, x):
        if isinstance(x, (list, tuple)):
            return x
        else:
            return [x]
    
    def __eq__(self, other):
        return other is not None and \
               self.name == other.name and \
               self.target_field is other.target_field and \
               self.operands == other.operands

    def __hash__(self):
        return hash((self.name, self.target_field, self.operands))
        

class MultiOperandOperation(Operation):
    def __init__(self, name, target_field, operands, delimiter=","):
        self.delimiter = delimiter
        super(MultiOperandOperation, self).__init__(
                name=name,
                target_field=target_field,
                operands=operands)

    def parse_operands(self, operands):
        results = []
        if isinstance(operands, (list, tuple)):
            for op in operands:
                results.append(op)
        elif isinstance(operands, basestring):
            for op in operands.split(self.delimiter):
                results.append(op)
        else:
            return self._to_list(operands)
        return results

class Equal(Operation):
    def __init__(self, target_field, operands):
        super(Equal, self).__init__("eq", target_field, operands)

class GreaterThan(Operation):
    def __init__(self, target_field, operands):
        super(GreaterThan, self).__init__("gt", target_field, operands)

class GreaterThanEqual(Operation):
    def __init__(self, target_field, operands):
        super(GreaterThanEqual, self).__init__("gte", target_field, operands)

class LessThan(Operation):
    def __init__(self, target_field, operands):
        super(LessThan, self).__init__("lt", target_field, operands)

class LessThanEqual(Operation):
    def __init__(self, target_field, operands):
        super(LessThanEqual, self).__init__("lte", target_field, operands)

class Contains(MultiOperandOperation):
    def __init__(self, target_field, operands):
        super(Contains, self).__init__("contains", target_field, operands)

class Exact(Operation):
    def __init__(self, target_field, operands):
        super(Exact, self).__init__("exact", target_field, operands)

class IgnoreCaseExact(Operation):
    def __init__(self, target_field, operands):
        super(IgnoreCaseExact, self).__init__("iexact", target_field, operands)

class In(MultiOperandOperation):
    def __init__(self, target_field, operands):
        super(In, self).__init__("in", target_field, operands)

class Startswith(Operation):
    def __init__(self, target_field, operands):
        super(Startswith, self).__init__("startswith", target_field, operands)

class IgnoreCaseStartswith(Operation):
    def __init__(self, target_field, operands):
        super(IgnoreCaseStartswith, self).__init__("istartswith", target_field, operands)

class Endswith(Operation):
    def __init__(self, target_field, operands):
        super(Endswith, self).__init__("endswith", target_field, operands)

class IgnoreCaseEndswith(Operation):
    def __init__(self, target_field, operands):
        super(IgnoreCaseEndswith, self).__init__("iendswith", target_field, operands)

class Range(MultiOperandOperation):
    def __init__(self, target_field, operands):
        super(Range, self).__init__("range", target_field, operands, delimiter=':')

class Ranges(MultiOperandOperation):
    def __init__(self, target_field, operands):
        super(Ranges, self).__init__("ranges", target_field, operands)

    def parse_operands(self, operands):
        results = []
        if isinstance(operands, list):
            for start, end in operands:
                results.append((start, end))
        elif isinstance(operands, basestring):
            for r in operands.split(self.delimiter):
                start, end = r.split(':')
                results.append((start, end))
        elif isinstance(operands, tuple):
            start, end = operands
            results.append((start, end))
        return results

    def validate_operands(self, operands):
        results = []
        for start, end in operands:
            start = self.target_field.validate(start)
            end = self.target_field.validate(end)
            results.append((start, end))
        return results

    def map_operands(self, function, validated=True):
        results = []
        operands = self.operands if validated else self.parsed_operands
        for start, end in operands:
            start = function(start)
            end = function(end)
            results.append((start, end))
        return results

class IsNull(Operation):
    def __init__(self, target_field, operands):
        super(IsNull, self).__init__("isnull", target_field, operands)

    def parse_operands(self, operands):
        return self._to_list(BooleanField().validate(operands))



OPERATIONS = {
    "eq": Equal,
    "gt": GreaterThan,
    "gte": GreaterThanEqual,
    "lt": LessThan,
    "lte": LessThanEqual,
    "contains": Contains,
    "exact": Exact,
    "iexact": IgnoreCaseExact,
    "in": In,
    "startswith": Startswith,
    "istartswith": IgnoreCaseStartswith,
    "endswith": Endswith,
    "iendswith": IgnoreCaseEndswith,
    "range": Range,
    "ranges": Ranges,
    "isnull": IsNull,
}

class Filter(object):
    def __init__(self, path_fields, operation):
        self.path_fields = path_fields
        self.operation = operation

    def name(self):
        path = "__".join([f.name for f in self.path_fields])
        operation = "%s__%s" % (self.operation.target_field.attname, self.operation.name)
        if path:
            result = "%s__%s" % (path, operation)
        else:
            result = operation
        return result

    def __eq__(self, other):
        return other is not None and \
               self.path_fields == other.path_fields and \
               self.operation == other.operation
    
    def __hash__(self):
        return hash((self.path_fields, self.operation))

    @staticmethod
    def parse(resource_class, **kwargs):
        results = []

        for arg, value in kwargs.items():
            current = resource_class
            parts = arg.split("__")

            path_fields = []
            target_field = None
            operation_class = None

            if parts[-1] in OPERATIONS:
                operation_name = parts[-1]
                operation_class = OPERATIONS[operation_name]
                parts = parts[:-1]
            else:
                operation_class = Equal
            
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
                            raise InvalidQuery("invalid filter '%s'" % arg)
                        target_field = field
                elif part in current.desc.related_fields_by_name:
                    field = current.desc.related_fields_by_name[part]
                    if field.relation is resource_class:
                        target_field = field
                    else:
                        path_fields.append(field)
                        current = field.relation
                else:
                    raise InvalidQuery("invalid filter '%s'" % arg)
            
            primary_key = getattr(current.desc, "primary_key", None)
            target_field = target_field or current.desc.fields_by_name[primary_key]
            operation = operation_class(target_field, value)

            filter = Filter(
                    path_fields=path_fields,
                    operation=operation)

            results.append(filter)

        return results
