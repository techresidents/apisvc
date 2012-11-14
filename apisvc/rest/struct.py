from rest.fields.related import RelatedField

class StructDescription(object):
    def __init__(self, **kwargs):
        self.abstract = False
        self.struct_class = None
        self.fields = []
        self.fields_by_name = {}
        self.related_fields = []
        self.related_fields_by_name = {}
        self.model_class = None

        self.update(**kwargs)

    def update(self, **kwargs):
        for name, value in kwargs.items():
            if value:
                setattr(self, name, value)

    def contribute_to_class(self, struct_class, name):
        self.struct_class = struct_class
        setattr(struct_class, name, self)

    def add_field(self, field):
        if isinstance(field, RelatedField):
            self.related_fields.append(field)
            self.related_fields_by_name[field.name] = field
        else:
            self.fields.append(field)
            self.fields_by_name[field.attname] = field


class StructMeta(type):
    def __new__(cls, name, bases, attributes):

        #parent classes derived from StructMeta
        parents = [base for base in bases if isinstance(base, StructMeta)]
        
        #create new class
        module = attributes.pop("__module__")
        new_class = super(StructMeta, cls).__new__(
                cls,
                name,
                bases,
                {"__module__": module})
        
        #Get 'Meta' class from parent, but only use it if no 'Meta'
        #class is provided by this class.
        meta = getattr(new_class, "Meta", None)
        
        #If 'Meta' class is provided in attributes, use this in
        #place of any parent 'Meta' class. In the future it may
        #be better to change this to attempt to merge
        #'Meta' class attributes.
        attr_meta = attributes.get("Meta", {})
        if attr_meta:
            meta = attr_meta

        #create struct description
        desc_kwargs = {}
        desc_kwargs["Meta"] = meta
        desc_kwargs["abstract"] = getattr(meta, "abstract", False)
        desc_kwargs["model_class"] = getattr(meta, "model_class", None)
        new_class.add_to_class("desc", StructDescription())
        
        #Add class attributes to new class
        for name, value in attributes.items():
            new_class.add_to_class(name, value)

        #Add parent fields to new class.
        #Note that currently we do not add any other
        #parent attributes.
        for parent in parents:
            if parent.desc.abstract:
                for field in parent.desc.fields:
                    new_class.desc.add_field(field)
        
        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, "contribute_to_class"):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Struct(object):
    __metaclass__ = StructMeta

    def __init__(self, **kwargs):
        for field in self.desc.fields:
            if field.attname in kwargs:
                value = kwargs.pop(field.attname)
                setattr(self, field.attname, value)
            elif field.name in kwargs:
                value = kwargs.pop(field.name)
                setattr(self, field.name, value)
            else:
                if field.has_default():
                    setattr(self, field.attname, field.get_default())
        
        if kwargs:
            raise TypeError("'%s' is an invalid argument" % kwargs.keys()[0])
