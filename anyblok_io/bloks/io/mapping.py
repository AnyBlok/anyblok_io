# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.declarations import Declarations, hybrid_method
from anyblok.column import String, Json
from .exceptions import IOMappingCheckException, IOMappingSetException
from logging import getLogger
logger = getLogger(__name__)


register = Declarations.register
Model = Declarations.Model


@register(Model.IO)
class Mapping:

    key = String(primary_key=True)
    model = String(primary_key=True,
                   foreign_key=Model.System.Model.use('name'))
    primary_key = Json(nullable=False)
    blokname = String(label="Blok name",
                      foreign_key=Model.System.Blok.use('name'))

    @hybrid_method
    def filter_by_model_and_key(self, model, key):
        """ SQLAlechemy hybrid method to filter by model and key

        :param model: model of the mapping
        :param key: external key of the mapping
        """
        return (self.model == model) & (self.key == key)

    @hybrid_method
    def filter_by_model_and_keys(self, model, *keys):
        """ SQLAlechemy hybrid method to filter by model and key

        :param model: model of the mapping
        :param key: external key of the mapping
        """
        return (self.model == model) & self.key.in_(keys)

    def remove_element(self, byquery=False):
        val = self.registry.get(self.model).from_primary_keys(
            **self.primary_key)
        logger.info("Remove entity for %r.%r: %r" % (
            self.model, self.key, val))
        val.delete(byquery=byquery, remove_mapping=False)

    @classmethod
    def multi_delete(cls, model, *keys, **kwargs):
        """ Delete all the keys for this model

        :param model: model of the mapping
        :param \*keys: list of the key
        :rtype: Boolean True if the mappings are removed
        """
        mapping_only = kwargs.get('mapping_only', True)
        byquery = kwargs.get('byquery', False)
        query = cls.query()
        query = query.filter(cls.filter_by_model_and_keys(model, *keys))
        count = query.count()
        if count:
            if not mapping_only:
                query.all().remove_element(byquery=byquery)

            query.delete(synchronize_session='fetch', remove_mapping=False)
            cls.registry.expire_all()
            return count

        return 0

    @classmethod
    def delete(cls, model, key, mapping_only=True, byquery=False):
        """ Delete the key for this model

        :param model: model of the mapping
        :param key: string of the key
        :rtype: Boolean True if the mapping is removed
        """
        query = cls.query()
        query = query.filter(cls.filter_by_model_and_key(model, key))
        count = query.count()
        if count:
            if not mapping_only:
                query.one().remove_element(byquery=byquery)

            query.delete(remove_mapping=False)
            return count

        return 0

    @classmethod
    def get_mapping_primary_keys(cls, model, key):
        """ return primary key for a model and an external key

        :param model: model of the mapping
        :param key: string of the key
        :rtype: dict primary key: value or None
        """
        query = cls.query()
        query = query.filter(cls.filter_by_model_and_key(model, key))
        if query.count():
            pks = query.first().primary_key
            cls.check_primary_keys(model, *pks.keys())
            return pks

        return None

    @classmethod
    def check_primary_keys(cls, model, *pks):
        """ check if the all the primary keys match with primary keys of the
        model

        :param model: model to check
        :param pks: list of the primary keys to check
        :exception: IOMappingCheckException
        """
        for pk in cls.get_model(model).get_primary_keys():
            if pk not in pks:
                raise IOMappingCheckException(
                    "No primary key %r found in %r for model %r" % (
                        pk, pks, model))

    @classmethod
    def set_primary_keys(cls, model, key, pks, raiseifexist=True,
                         blokname=None):
        """ Add or update a mmping with a model and a external key

        :param model: model to check
        :param key: string of the key
        :param pks: dict of the primary key to save
        :param raiseifexist: boolean (True by default), if True and the entry
            exist then an exception is raised
        :param blokname: name of the blok where come from the mapping
        :exception: IOMappingSetException
        """
        if cls.get_mapping_primary_keys(model, key):
            if raiseifexist:
                raise IOMappingSetException(
                    "One value found for model %r and key %r" % (model, key))
            cls.delete(model, key)

        if not pks:
            raise IOMappingSetException(
                "No value to save %r for model %r and key %r" % (
                    pks, model, key))

        cls.check_primary_keys(model, *pks.keys())
        vals = dict(model=model, key=key, primary_key=pks)
        if blokname is not None:
            vals['blokname'] = blokname

        return cls.insert(**vals)

    @classmethod
    def set(cls, key, instance, raiseifexist=True, blokname=None):
        """ Add or update a mmping with a model and a external key

        :param model: model to check
        :param key: string of the key
        :param instance: instance of the model to save
        :param raiseifexist: boolean (True by default), if True and the entry
            exist then an exception is raised
        :param blokname: name of the blok where come from the mapping
        :exception: IOMappingSetException
        """
        pks = instance.to_primary_keys()
        return cls.set_primary_keys(instance.__registry_name__, key, pks,
                                    blokname=blokname,
                                    raiseifexist=raiseifexist)

    @classmethod
    def get(cls, model, key):
        """ return instance of the model with this external key

        :param model: model of the mapping
        :param key: string of the key
        :rtype: instance of the model
        """
        pks = cls.get_mapping_primary_keys(model, key)
        if pks is None:
            return None

        return cls.get_model(model).from_primary_keys(**pks)

    @classmethod
    def get_from_model_and_primary_keys(cls, model, pks):
        query = cls.query().filter(cls.model == model)
        for mapping in query.all():
            if mapping.primary_key == pks:
                return mapping

        return None

    @classmethod
    def get_from_entry(cls, entry):
        return cls.get_from_model_and_primary_keys(
            entry.__registry_name__, entry.to_primary_keys())

    @classmethod
    def __get_models(cls, models):
        """Return models name

        if models is not: return all the existing model
        if models is a list of instance model, convert them

        :params models: list of model
        """
        if models is None:
            models = cls.registry.System.Model.query().all().name
        elif not isinstance(models, (list, tuple)):
            models = [models]

        return [m.__registry_name__ if hasattr(m, '__registry_name__') else m
                for m in models]

    @classmethod
    def clean(cls, bloknames=None, models=None):
        """Clean all mapping with removed object linked::

            Mapping.clean(bloknames=['My blok'])

        .. warning::

            For filter only the no blokname::

                Mapping.clean(bloknames=[None])

        :params bloknames: filter by blok, keep the order to remove the mapping
        :params models: filter by model, keep the order to remove the mapping
        """
        if bloknames is None:
            bloknames = cls.registry.System.Blok.query().all().name + [None]
        elif not isinstance(bloknames, (list, tuple)):
            bloknames = [bloknames]
        models = cls.__get_models(models)

        removed = 0
        for blokname in bloknames:
            for model in models:
                query = cls.query().filter_by(blokname=blokname, model=model)
                for key in query.all().key:
                    if cls.get(model, key) is None:
                        cls.delete(model, key)
                        removed += 1

        return removed

    @classmethod
    def delete_for_blokname(cls, blokname, models=None, byquery=False):
        """Clean all mapping with removed object linked::

            Mapping.clean('My blok')

        .. warning::

            For filter only the no blokname::

                Mapping.clean(None)

        :params blokname: filter by blok
        :params models: filter by model, keep the order to remove the mapping
        """
        models = cls.__get_models(models)

        removed = 0
        for model in models:
            query = cls.query().filter_by(blokname=blokname, model=model)
            for key in query.all().key:
                if cls.get(model, key):
                    cls.delete(model, key, mapping_only=False, byquery=byquery)
                    cls.registry.flush()
                    removed += 1

        return removed
