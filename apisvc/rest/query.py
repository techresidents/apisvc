from rest.collection import ResourceCollection
from rest.filter import Filter
from rest.option import Option
from rest.orderby import OrderBy
from rest.utils.attribute import xgetattr, xsetattr
from rest.withrel import WithRelation

class Query(object):
    def __init__(self, resource_class, transaction_factory=None):
        self.resource_class = resource_class
        self.transaction_factory = transaction_factory
        self.options = Option.default_options(resource_class)
        self.filters = []
        self.slices = None
        self.order_bys = []
        self.with_relations = []
    
    def parse(self, **kwargs):
        if "order_by" in kwargs:
            order_bys = kwargs.pop("order_by").split(",")
            self.order_by(*order_bys)
        if "slice" in kwargs:
            slice_args = kwargs.pop("slice").split(",")
            slice_args = [int(s) for s in slice_args]
            self.slice(*slice_args)
        if "with" in kwargs:
            with_relations = kwargs.pop("with").split(",")
            self.with_relation(*with_relations)
        
        option_kwargs = {}
        for option in self.resource_class.desc.options:
            if option.name in kwargs:
                option_kwargs[option.name] = kwargs.pop(option.name)
        self.option(**option_kwargs)

        self.filter(**kwargs)
    
    def empty(self):
        if self.filters \
            or self.slices \
            or self.order_bys \
            or self.with_relations:
                return False
        else:
            return True

    def model_to_resource(self, model, resource=None, excludes=None):
        excludes = excludes or []
        kwargs = {}
        for field in self.resource_class.desc.fields:
            if field.attname in excludes:
                continue 

            value = xgetattr(model, field.model_attname, None)
            kwargs[field.attname] = field.validate(value)
        
        if resource:
            for arg, value in kwargs.items():
                setattr(resource, arg, value)
        else:
            resource = self.resource_class(**kwargs)

        return resource

    def resource_to_model(self,
            resource,
            model=None,
            include_primary_key=False,
            include_readonly=False,
            include_hidden=False,
            excludes=None):
        excludes = excludes or []
        kwargs = {}
        nested_kwargs = []
        
        for field in self.resource_class.desc.fields:
            if (field.primary_key and not include_primary_key) or \
               (field.readonly and not include_readonly) or \
               (field.hidden and not include_hidden) or \
               (field.attname in excludes):
                continue
            
            if "." in field.model_attname:    
                value = getattr(resource, field.attname)
                nested_kwargs[field.model_attname] = field.validate_for_model(value)
            else:
                value = getattr(resource, field.attname)
                kwargs[field.model_attname] = field.validate_for_model(value)
        
        if model:
            for arg, value in kwargs.items():
                setattr(model, arg, value)
        else:
            model = self.resource_class.desc.model_class(**kwargs)
        
        for arg, value in nested_kwargs:
            xsetattr(model, arg, value)
        
        return model

    def option(self, **kwargs):
        options = Option.parse(self.resource_class, **kwargs)
        for name, value in options.items():
            self.options[name] = value
        return self

    def filter(self, **kwargs):
        filters = Filter.parse(self.resource_class, **kwargs)
        self.filters.extend(filters)
        return self
    
    def slice(self, start, stop):
        self.slices = (start, stop)
        return self

    def order_by(self, *args):
        kwargs = {}
        for arg in args:
            kwargs[arg] = None
        order_bys = OrderBy.parse(self.resource_class, **kwargs)
        self.order_bys.extend(order_bys)
        return self
    
    def with_relation(self, *args):
        kwargs = {}
        for arg in args:
            kwargs[arg] = None
        with_relations = WithRelation.parse(self.resource_class, **kwargs)
        self.with_relations.extend(with_relations)
        return self

    def get(self, id):
        pass

    def one(self):
        pass

    def all(self):
        pass

    def create(self, **kwargs):
        pass

    def update(self, **kwargs):
        pass

    def delete(self):
        pass

    def bulk_create(self, resources):
        pass

    def bulk_update(self, resources):
        pass

    def bulk_delete(self, resources):
        pass

    def _apply_with_relations(self, resources):
        for with_relation in self.with_relations:
            current = resources
            for related_field in with_relation.related_fields:
                if isinstance(current, ResourceCollection):
                    new_current = ResourceCollection()
                    for obj in current:
                        result = getattr(obj, related_field.name)
                        if isinstance(result, ResourceCollection):
                            new_current.extend(result)
                        else:
                            new_current.append(result)
                    current = new_current
                else:
                    current = getattr(current, related_field.name)
