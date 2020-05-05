# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from json import dumps


@pytest.mark.usefixtures('rollback_registry')
class TestImporterFormater:

    @pytest.fixture(autouse=True)
    def transact(self, rollback_registry):
        self.registry = rollback_registry

    def get_value(self, value, ctype, external_id=False, model=None):
        return self.registry.IO.Importer().str2value(value, ctype,
                                                     external_id=external_id,
                                                     model=model)

    def test_datetime(self):
        from datetime import datetime
        value = self.get_value("2015-05-01 17:52:01", "DateTime")
        assert isinstance(value, datetime)
        assert value.year == 2015
        assert value.month == 5
        assert value.day == 1

    def test_decimal(self):
        from decimal import Decimal
        value = self.get_value("1.5", "Decimal")
        assert isinstance(value, Decimal)
        assert value == Decimal("1.5")

    def test_float(self):
        value = self.get_value("1.5", "Float")
        assert isinstance(value, float)
        assert value == 1.5

    def test_json(self):
        value = self.get_value(dumps({'id': 1}), "Json")
        assert isinstance(value, dict)
        assert value == {'id': 1}

    def test_time(self):
        from datetime import time
        value = self.get_value("17:52:01", "Time")
        assert isinstance(value, time)
        assert value.hour == 17

    def test_big_interger(self):
        value = self.get_value("17", "BigInteger")
        assert isinstance(value, int)
        assert value == 17

    def test_boolean(self):
        for v in ('1', 'true', 'True'):
            value = self.get_value(v, "Boolean")
            assert isinstance(value, bool)
            assert value is True

        for v in ('0', 'false', 'False'):
            value = self.get_value(v, "Boolean")
            assert isinstance(value, bool)
            assert value is False

    def test_date(self):
        from datetime import date
        value = self.get_value("2015-05-01", "Date")
        assert isinstance(value, date)
        assert value.year == 2015
        assert value.month == 5
        assert value.day == 1

    def test_interger(self):
        value = self.get_value("10", "Integer")
        assert isinstance(value, int)
        assert value == 10

    def test_interval(self):
        from datetime import timedelta
        value = self.get_value("10", "Interval")
        assert isinstance(value, timedelta)
        assert value.seconds == 10

    def test_large_binary(self):
        from os import urandom
        blob = urandom(100)
        value = self.get_value(blob, "Large_Binary")
        assert isinstance(value, bytes)
        assert value == blob

    def test_selection(self):
        value = self.get_value("selection", "Selection")
        assert isinstance(value, str)
        assert value == "selection"

    def test_string(self):
        value = self.get_value("selection", "String")
        assert isinstance(value, str)
        assert value == "selection"

    def test_text(self):
        value = self.get_value("selection", "Text")
        assert isinstance(value, str)
        assert value == "selection"

    def test_many2many(self):
        pks = dict(name='Model.System.Model')
        model = self.registry.System.Model.from_primary_keys(**pks)
        value = self.get_value(
            dumps([pks]), "Many2Many", model="Model.System.Model")
        assert value == [model]

    def test_many2many_multi_value(self):
        pks1 = dict(name='Model.System.Model')
        pks2 = dict(name='Model.System.Column')
        model1 = self.registry.System.Model.from_primary_keys(**pks1)
        model2 = self.registry.System.Model.from_primary_keys(**pks2)
        value = self.get_value(
            dumps([pks1, pks2]), "Many2Many", model="Model.System.Model")
        assert value == [model1, model2]

    def test_many2many_external_ids(self):
        key = 'formater_mapping'
        model = self.registry.System.Model.from_primary_keys(
            name='Model.System.Model')
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(dumps([key]), "Many2Many",
                               external_id=True, model="Model.System.Model")
        assert value == [model]

    def test_many2many_multi_value_external_ids(self):
        key1 = 'formater_mapping1'
        key2 = 'formater_mapping2'
        model1 = self.registry.System.Model.from_primary_keys(
            name='Model.System.Model')
        model2 = self.registry.System.Model.from_primary_keys(
            name='Model.System.Column')
        self.registry.IO.Mapping.set(key1, model1)
        self.registry.IO.Mapping.set(key2, model2)
        value = self.get_value(dumps([key1, key2]), "Many2Many",
                               external_id=True, model="Model.System.Model")
        assert value == [model1, model2]

    def test_one2many(self):
        pks = dict(name='Model.System.Model')
        model = self.registry.System.Model.from_primary_keys(**pks)
        value = self.get_value(
            dumps([pks]), "One2Many", model="Model.System.Model")
        assert value == [model]

    def test_one2many_multi_value(self):
        pks1 = dict(name='Model.System.Model')
        pks2 = dict(name='Model.System.Column')
        model1 = self.registry.System.Model.from_primary_keys(**pks1)
        model2 = self.registry.System.Model.from_primary_keys(**pks2)
        value = self.get_value(
            dumps([pks1, pks2]), "One2Many", model="Model.System.Model")
        assert value == [model1, model2]

    def test_one2many_external_ids(self):
        key = 'formater_mapping'
        model = self.registry.System.Model.from_primary_keys(
            name='Model.System.Model')
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(dumps([key]), "One2Many", external_id=True,
                               model="Model.System.Model")
        assert value == [model]

    def test_one2many_external_ids_is_none_1(self):
        value = self.get_value(dumps(None), "One2Many", external_id=True,
                               model="Model.System.Model")
        assert value == []

    def test_one2many_external_ids_is_none_2(self):
        value = self.get_value(dumps([]), "One2Many", external_id=True,
                               model="Model.System.Model")
        assert value == []

    def test_one2many_multi_value_external_ids(self):
        key1 = 'formater_mapping1'
        key2 = 'formater_mapping2'
        model1 = self.registry.System.Model.from_primary_keys(
            name='Model.System.Model')
        model2 = self.registry.System.Model.from_primary_keys(
            name='Model.System.Column')
        self.registry.IO.Mapping.set(key1, model1)
        self.registry.IO.Mapping.set(key2, model2)
        value = self.get_value(dumps([key1, key2]), "One2Many",
                               external_id=True, model="Model.System.Model")
        assert value == [model1, model2]

    def test_many2one(self):
        pks = dict(name='Model.System.Model')
        model = self.registry.System.Model.from_primary_keys(**pks)
        value = self.get_value(
            dumps(pks), "Many2One", model="Model.System.Model")
        assert value == model

    def test_many2one_external_ids(self):
        key = 'formater_mapping'
        model = self.registry.System.Model.from_primary_keys(
            name='Model.System.Model')
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(key, "Many2One", external_id=True,
                               model="Model.System.Model")
        assert value == model

    def test_many2one_external_ids_with_none_value(self):
        value = self.get_value(None, "Many2One", external_id=True,
                               model="Model.System.Model")
        assert value is None

    def test_one2one(self):
        pks = dict(name='Model.System.Model')
        model = self.registry.System.Model.from_primary_keys(**pks)
        value = self.get_value(
            dumps(pks), "One2One", model="Model.System.Model")
        assert value == model

    def test_one2one_external_ids(self):
        key = 'formater_mapping'
        model = self.registry.System.Model.from_primary_keys(
            name='Model.System.Model')
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(key, "One2One", external_id=True,
                               model="Model.System.Model")
        assert value == model
