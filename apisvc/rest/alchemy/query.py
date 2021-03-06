import inspect

from sqlalchemy import asc, desc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from rest.exceptions import InvalidQuery, ResourceNotFound
from rest.fields import ManyToMany
from rest.query import Query
from rest.resource import Resource

DB_OPERATIONS = {
    "eq": lambda c, v: c == v,
    "gt": lambda c, v: c > v,
    "gte": lambda c, v: c >= v,
    "lt": lambda c, v: c < v,
    "lte": lambda c, v: c <= v,
    "contains": lambda c, *v: c.contains(*v),
    "exact": lambda c, v: c == v,
    "iexact": lambda c, v: c.ilike(v),
    "in": lambda c, *v: c.in_(v),
    "startswith": lambda c, v: c.startswith(v),
    "istartswith": lambda c, v: c.ilike(v.replace('%', '%%') + '%'),
    "endswith": lambda c, v: c.endswith(v),
    "iendswith": lambda c, v: c.ilike('%' + v.replace('%', '%%')),
    "range": lambda c, *v: c.between(*v),
    "ranges": lambda c, *v: or_(*[c.between(s,e) for s,e in v]),
    "isnull": lambda c, v: c == None if v else c != None,
}

class AlchemyQuery(Query):
    def __init__(self, resource_class, transaction_factory):
        super(AlchemyQuery, self).__init__(
                resource_class=resource_class,
                transaction_factory=transaction_factory)

    def _build_query(self, db_session, is_count=False):
        query = db_session.query(self.resource_class.desc.model_class)
        try:
            #Set optional alchemy query options if provided.
            #This is typically a joinedload or something of
            #of this sort serving as an optimization.
            query = query.options(*self.resource_class.Meta.alchemy_query_options)
        except AttributeError:
            pass
        query = self._apply_filters(query)

        if not is_count:
            query = self._apply_order_bys(query)
            query = self._apply_slices(query)
        return query

    def _build_count_query(self, db_session):
        return self._build_query(db_session, is_count=True)

    def _apply_filters(self, query):
        for filter in self.filters:
            query = self._apply_joins(filter.path_fields, filter.operation.target_field, query)
            model = filter.operation.target_field.model_class
            model_field = getattr(model, filter.operation.target_field.model_attname.rsplit(".", 1)[-1])
            operands = filter.operation.map_operands(
                    filter.operation.target_field.validate_for_model)
            db_op = DB_OPERATIONS[filter.operation.name](model_field, *operands)
            query = query.filter(db_op)
        return query
    
    def _apply_order_bys(self, query):
        if self.order_bys:
            order_bys = []
            for order_by in self.order_bys:
                field = order_by.target_field
                query = self._apply_joins(order_by.path_fields, field, query)
                o = getattr(field.model_class, field.model_attname.rsplit(".")[-1])
                if order_by.direction == 'DESC':
                    order_bys.append(desc(o))
                else:
                    order_bys.append(asc(o))
                query = query.order_by(*order_bys)
        return query
    
    def _apply_slices(self, query):
        limit = self.resource_class.desc.allowed_limit
        if self.slices is not None:
            start, stop = self.slices
            if (stop-start) > limit:
                raise InvalidQuery("max limit exceeded")
        else:
            self.slices = (0, limit)
        query = query.slice(*self.slices)
        return query

    def _apply_joins(self, related_fields, target_field, query):
        current = self.resource_class

        joins = []
        for related_field in related_fields:
            if related_field.relation is self.resource_class:
                continue
            if isinstance(related_field, ManyToMany):
                m2m_joins = []
                if related_field.through: 
                    if isinstance(related_field.through, (list, tuple)):
                        m2m_joins.extend(related_field.through)
                    else:
                        if inspect.isclass(related_field.through) \
                                and issubclass(related_field.through, Resource):
                            m2m_joins.append(related_field.through.desc.model_class)
                        else:
                            m2m_joins.append(related_field.through)
                        m2m_joins.append(related_field.relation.desc.model_class)
                else:
                    model_name = related_field.model_name.strip("+")
                    #join through model_name attribute if present,
                    #otherwise add join through model class.
                    if hasattr(current.desc.model_class, model_name):
                        joins.append(model_name)
                    else:
                        joins.append(related_field.relation.desc.model_class)
                joins.extend(self._to_list(m2m_joins))
            else:
                model_name = related_field.model_name.strip("+")
                #join through model_name attribute if present,
                #otherwise add join through model class.
                if hasattr(current.desc.model_class, model_name):
                    joins.append(model_name)
                else:
                    if related_field.through:
                        if isinstance(related_field.through, (list, tuple)):
                            joins.extend(related_field.through)
                        else:
                            if inspect.isclass(related_field.through) \
                                    and issubclass(related_field.through, Resource):
                                joins.append(related_field.through.desc.model_class)
                            else:
                                joins.append(related_field.through)
                    joins.append(related_field.relation.desc.model_class)

            current = related_field.relation
        
        if target_field and target_field.model_class is not current.desc.model_class:
            joins.extend(self._to_list(target_field.model_class))
        
        #Aliasing allows us to not worry about duplicate joins.
        #This is not as efficient, but more robust.
        query = query.join(*joins, aliased=True)
        return query

    def _to_list(self, x):
        if isinstance(x, (list, tuple)):
            return x
        else:
            return[x]

    def get(self, id):
        with self.transaction_factory() as db_session:
            query = self._build_query(db_session)
            try:
                model = query.get(id)
            except NoResultFound:
                raise ResourceNotFound()
            result = self.model_to_resource(model)
            self._apply_with_relations(result)
            return result

    def one(self):
        with self.transaction_factory() as db_session:
            query = self._build_query(db_session)
            try:
                model = query.one()
            except NoResultFound:
                raise ResourceNotFound()
            result = self.model_to_resource(model)
            self._apply_with_relations(result)
            return result

    def all(self):
        with self.transaction_factory() as db_session:
            results = self.resource_class.Collection()

            query = self._build_query(db_session)
            for model in query.all():
                results.append(self.model_to_resource(model))
            self._apply_with_relations(results)
            
            results.total_count = self._build_count_query(db_session).count()
            
            return results

    def create(self, **kwargs):
        if not self.empty():
            raise InvalidQuery("create query must be empty")

        resource = kwargs.pop("resource", None)
        if resource is None:
            resource = self.resource_class(**kwargs)
        
        try:
            with self.transaction_factory() as db_session:
                model = self.resource_to_model(resource)
                db_session.add(model)
                db_session.flush()
                return self.model_to_resource(model, resource)
        except IntegrityError as error:
            raise InvalidQuery("invalid create query: %s" % str(error))

    def update(self, **kwargs):
        resource = kwargs.pop("resource", None)
        if resource is None:
            resource = self.resource_class(**kwargs)
        try:
            with self.transaction_factory() as db_session:
                query = self._build_query(db_session)
                model = query.one()
                self.resource_to_model(resource, model)
                return self.model_to_resource(model, resource)
        except IntegrityError as error:
            raise InvalidQuery("invalid update query: %s" % str(error))

    def delete(self):
        with self.transaction_factory() as db_session:
            query = self._build_query(db_session)
            model = query.one()
            db_session.delete(model)

    def bulk_create(self, resources):
        if not self.empty():
            raise InvalidQuery("create query must be empty")
        
        try:
            with self.transaction_factory() as db_session:
                models = []
                for resource in resources:
                    model = self.resource_to_model(resource)
                    db_session.add(model)
                    models.append(model)
                db_session.flush()

                for model,resource in zip(models, resources):
                    self.model_to_resource(model, resource)

                return resources
        except IntegrityError as error:
            raise InvalidQuery("invalid bulk create query: %s" % str(error))

    def bulk_update(self, resources):
        primary_keys = [r.primary_key_value() for r in resources]

        try:
            with self.transaction_factory() as db_session:
                query = self._build_query(db_session)
                model_pk_name = self.resource_class.desc.primary_key_field.model_attname
                model_pk = getattr(self.resource_class.desc.model_class, model_pk_name)
                query = query.filter(model_pk.in_(primary_keys))
                models = query.all()
                if len(models) != len(resources):
                    raise InvalidQuery("resources provided does not match filter results")

                model_map = {}
                for model in models:
                    model_map[getattr(model, model_pk_name)] = model
                
                for resource in resources:
                    model = model_map[getattr(resource, model_pk_name)]
                    self.resource_to_model(resource, model)
                db_session.flush()

                for resource in resources:
                    model = model_map[getattr(resource, model_pk_name)]
                    self.model_to_resource(model, resource)
                return resources
        except IntegrityError as error:
            raise InvalidQuery("invalid bulk update query: %s" % str(error))

    def bulk_delete(self, resources):
        primary_keys = [r.primary_key_value() for r in resources]
        with self.transaction_factory() as db_session:
            query = self._build_query(db_session)
            model_pk_name = self.resource_class.desc.primary_key_field.model_attname
            model_pk = getattr(self.resource_class.desc.model_class, model_pk_name)
            count = query.filter(model_pk.in_(primary_keys)).count()
            if count != len(resources):
                raise InvalidQuery("resources provided does not match filter results")

            for resource in resources:
                model = self.resource_to_model(resource)
                db_session.delete(model)
