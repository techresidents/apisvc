from rest.fields import BooleanField

class Operation(object):
    def __init__(self, name, target_field, operands):
        self.name = name
        self.target_field = target_field
        self.operands = self.parse_operands(operands)
    
    def parse_operands(self, operands):
        return self._to_list(self.target_field.validate(operands))

    def _to_list(self, x):
        if isinstance(x, (list, tuple)):
            return x
        else:
            return[x]

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
                results.append(self.target_field.validate(op))
        elif isinstance(operands, basestring):
            for op in operands.split(self.delimiter):
                results.append(self.target_field.validate(op))
        else:
            return self._to_list(self.target_field.validate(operands))
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
        super(LessThanEqual, self).__init__("lte", operands)

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
        super(Range, self).__init__("range", target_field, operands)

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
    "isnull": IsNull,
}

class Filter(object):
    def __init__(self, related_fields, operation):
        self.related_fields = related_fields
        self.operation = operation

    def name(self):
        relations = "__".join([f.name for f in self.related_fields])
        operation = "%s__%s" % (self.operation.target_field.attname, self.operation.name)
        if relations:
            result = "%s__%s" % (relations, operation)
        else:
            result = operation
        return result

    @staticmethod
    def parse(resource_class, **kwargs):
        results = []

        for arg, value in kwargs.items():
            current = resource_class
            parts = arg.split("__")

            related_fields = []
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
                    target_field = field

                    #target field should be the last part
                    if parts[-1] != part:
                        raise RuntimeError("invalid filter '%s'" % arg)

                elif part in current.desc.related_fields_by_name:
                    field = current.desc.related_fields_by_name[part]
                    if field.relation is resource_class:
                        target_field = field
                    else:
                        related_fields.append(field)
                        current = field.relation
                else:
                    raise RuntimeError("invalid filter '%s'" % arg)
            
            primary_key = current.desc.primary_key
            target_field = target_field or current.desc.fields_by_name[primary_key]
            operation = operation_class(target_field, value)

            filter = Filter(
                    related_fields=related_fields,
                    operation=operation)

            results.append(filter)

        return results
