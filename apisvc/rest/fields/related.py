from trpycore.encode.basic import basic_encode, basic_decode
from rest.exceptions import ValidationError
from rest.fields.base import Field

class RelatedField(Field):
    def __init__(self, many=False, self_referential=False,  **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = self.NO_DEFAULT
        super(RelatedField, self).__init__(**kwargs)
        self.many = many
        self.self_referential = self_referential
    
class RelatedDescriptor(object):
    def __init__(self, field):
        self.field = field
        self.cache_name = self.field.get_cache_name()
    
    def is_loaded(self, instance):
        return hasattr(instance, self.cache_name)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        try:
            return getattr(instance, self.cache_name)
        except AttributeError:
            manager = instance.desc.manager
            value =  manager.get_relation(self.field, instance)
            setattr(instance, self.cache_name, value)
            return value

    def __set__(self, instance, value):
        if value is None:
            raise ValidationError("related descriptor cannot be null")
        setattr(instance, self.cache_name, value)

class ReverseForeignKey(RelatedField):
    def __init__(self, relation, backref=None, reverse=None, **kwargs):
        super(ReverseForeignKey, self).__init__(many=True, **kwargs)
        self.relation = relation
        self.backref = backref
        self.reverse = reverse

    def contribute_to_class(self, container_class, name):
        super(ReverseForeignKey, self).contribute_to_class(container_class, name)
        setattr(container_class, name, RelatedDescriptor(self))

class ForeignKey(RelatedField):
    def __init__(self, relation, backref=None, reverse=None, attname=None, **kwargs):
        self._attname = attname
        super(ForeignKey, self).__init__(many=False, default=None, **kwargs)
        self.relation = relation
        self.backref = backref
        self.reverse = reverse

    def get_attname(self):
        return self._attname if self._attname else "%s_id" % self.name

    def contribute_to_class(self, container_class, name):
        super(ForeignKey, self).contribute_to_class(container_class, name)
        if self.relation == "self":
            self.relation = container_class
            self.self_referential = True

        setattr(container_class, name, RelatedDescriptor(self))

        if self.backref is not None:
            hidden = self.backref.endswith("+")
            self.reverse = ReverseForeignKey(
                    relation=container_class,
                    backref=None,
                    reverse=self,
                    self_referential=self.self_referential,
                    hidden=hidden)
            self.reverse.contribute_to_class(self.relation, self.backref)

class EncodedForeignKey(ForeignKey):
    def to_python(self, value):
        result = value
        if isinstance(value, int):
            result = basic_encode(value)
        elif not isinstance(value, basestring):
            result = str(value)
        return result

    def to_model(self, value):
        result = value
        if isinstance(value, basestring):
            result = basic_decode(value)
        return result

class OneToOne(RelatedField):
    def __init__(self, relation, backref=None, reverse=None, attname=None, **kwargs):
        self._attname = attname
        super(OneToOne, self).__init__(many=False, default=None, **kwargs)
        self.relation = relation
        self.backref = backref
        self.reverse = reverse

    def get_attname(self):
        return self._attname if self._attname else "%s_id" % self.name

    def contribute_to_class(self, container_class, name):
        super(OneToOne, self).contribute_to_class(container_class, name)
        if self.relation == "self":
            self.relation = container_class
            self.self_referential = True

        setattr(container_class, name, RelatedDescriptor(self))

        if self.backref is not None:
            hidden = self.backref.endswith("+")
            self.reverse = OneToOne(
                    relation=container_class,
                    backref=None,
                    reverse=self,
                    self_referential=self.self_referential,
                    hidden=hidden)
            self.reverse.contribute_to_class(self.relation, self.backref)

class EncodedOneToOne(OneToOne):
    def to_python(self, value):
        result = value
        if isinstance(value, int):
            result = basic_encode(value)
        elif not isinstance(value, basestring):
            result = str(value)
        return result

    def to_model(self, value):
        result = value
        if isinstance(value, basestring):
            result = basic_decode(value)
        return result


class ManyToMany(RelatedField):
    def __init__(self, relation, backref=None, reverse=None, through=None, backref_through=None, **kwargs):
        super(ManyToMany, self).__init__(many=True, **kwargs)
        self.relation = relation
        self.backref = backref
        self.reverse = reverse
        self.through = through
        self.backref_through=backref_through
    
    def contribute_to_class(self, container_class, name):
        super(ManyToMany, self).contribute_to_class(container_class, name)
        setattr(container_class, name, RelatedDescriptor(self))

        if self.backref is not None:
            hidden = self.backref.endswith("+")
            self.reverse = ManyToMany(
                    relation=container_class,
                    backref=None,
                    reverse=self,
                    through=self.backref_through or self.through,
                    hidden=hidden)
            self.reverse.contribute_to_class(self.relation, self.backref)
