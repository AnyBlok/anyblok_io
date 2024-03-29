# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from json import dumps

import pytest


@pytest.mark.usefixtures("rollback_registry")
class TestExporterFormater:
    @pytest.fixture(autouse=True)
    def transact(self, rollback_registry):
        self.registry = rollback_registry

    def get_value(self, value, ctype, external_id=False, model=None):
        return self.registry.IO.Exporter().value2str(
            value, ctype, external_id=external_id, model=model
        )

    def test_datetime(self):
        from datetime import datetime

        dt = datetime(2015, 5, 1, 17, 52, 1)
        value = self.get_value(dt, "DateTime")
        assert value == "2015-05-01 17:52:01"

    def test_decimal(self):
        from decimal import Decimal

        value = self.get_value(Decimal("1.5"), "Decimal")
        assert value == "1.5"

    def test_float(self):
        value = self.get_value(1.5, "Float")
        assert value == "1.5"

    def test_json(self):
        value = self.get_value({"id": 1}, "Json")
        assert value == dumps({"id": 1})

    def test_time(self):
        from datetime import time

        t = time(17, 52, 1)
        value = self.get_value(t, "Time")
        assert value == "17:52:01"

    def test_big_interger(self):
        value = self.get_value(17, "BigInteger")
        assert value == "17"

    def test_boolean(self):
        value = self.get_value(True, "Boolean")
        assert value == "1"
        value = self.get_value(False, "Boolean")
        assert value == "0"

    def test_date(self):
        from datetime import date

        d = date(2015, 5, 1)
        value = self.get_value(d, "Date")
        assert value == "2015-05-01"

    def test_interger(self):
        value = self.get_value(10, "Integer")
        assert value == "10"

    def test_interval(self):
        from datetime import timedelta

        td = timedelta(seconds=10)
        value = self.get_value(td, "Interval")
        assert value == "10"

    def test_selection(self):
        value = self.get_value("selection", "Selection")
        assert value == "selection"

    def test_string(self):
        value = self.get_value("selection", "String")
        assert value == "selection"

    def test_text(self):
        value = self.get_value("selection", "Text")
        assert value == "selection"

    def test_many2many(self):
        pks = dict(name="Model.System.Model")
        model = self.registry.System.Model.from_primary_keys(**pks)
        value = self.get_value([model], "Many2Many", model="Model.System.Model")
        assert value == dumps([pks])

    def test_many2many_multi_value(self):
        pks1 = dict(name="Model.System.Model")
        pks2 = dict(name="Model.System.Column")
        model1 = self.registry.System.Model.from_primary_keys(**pks1)
        model2 = self.registry.System.Model.from_primary_keys(**pks2)
        value = self.get_value(
            [model1, model2], "Many2Many", model="Model.System.Model"
        )
        assert value == dumps([pks1, pks2])

    def test_many2many_external_ids(self):
        key = "formater_mapping"
        model = self.registry.System.Model.from_primary_keys(
            name="Model.System.Model"
        )
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(
            ([model]), "Many2Many", external_id=True, model="Model.System.Model"
        )
        assert value == dumps([key])

    def test_many2many_multi_value_external_ids(self):
        key1 = "formater_mapping1"
        key2 = "formater_mapping2"
        model1 = self.registry.System.Model.from_primary_keys(
            name="Model.System.Model"
        )
        model2 = self.registry.System.Model.from_primary_keys(
            name="Model.System.Column"
        )
        self.registry.IO.Mapping.set(key1, model1)
        self.registry.IO.Mapping.set(key2, model2)
        value = self.get_value(
            [model1, model2],
            "Many2Many",
            external_id=True,
            model="Model.System.Model",
        )
        assert value == dumps([key1, key2])

    def test_one2many(self):
        pks = dict(name="Model.System.Model")
        model = self.registry.System.Model.from_primary_keys(**pks)
        value = self.get_value([model], "One2Many", model="Model.System.Model")
        assert value == dumps([pks])

    def test_one2many_multi_value(self):
        pks1 = dict(name="Model.System.Model")
        pks2 = dict(name="Model.System.Column")
        model1 = self.registry.System.Model.from_primary_keys(**pks1)
        model2 = self.registry.System.Model.from_primary_keys(**pks2)
        value = self.get_value(
            [model1, model2], "One2Many", model="Model.System.Model"
        )
        assert value == dumps([pks1, pks2])

    def test_one2many_external_ids(self):
        key = "formater_mapping"
        model = self.registry.System.Model.from_primary_keys(
            name="Model.System.Model"
        )
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(
            [model], "One2Many", external_id=True, model="Model.System.Model"
        )
        assert value == dumps([key])

    def test_one2many_multi_value_external_ids(self):
        key1 = "formater_mapping1"
        key2 = "formater_mapping2"
        model1 = self.registry.System.Model.from_primary_keys(
            name="Model.System.Model"
        )
        model2 = self.registry.System.Model.from_primary_keys(
            name="Model.System.Column"
        )
        self.registry.IO.Mapping.set(key1, model1)
        self.registry.IO.Mapping.set(key2, model2)
        value = self.get_value(
            [model1, model2],
            "One2Many",
            external_id=True,
            model="Model.System.Model",
        )
        assert value == dumps([key1, key2])

    def test_many2one(self):
        pks = dict(name="Model.System.Model")
        model = self.registry.System.Model.from_primary_keys(**pks)
        value = self.get_value(model, "Many2One", model="Model.System.Model")
        assert value == dumps(pks)

    def test_many2one_external_ids(self):
        key = "formater_mapping"
        model = self.registry.System.Model.from_primary_keys(
            name="Model.System.Model"
        )
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(
            model, "Many2One", external_id=True, model="Model.System.Model"
        )
        assert value == key

    def test_one2one(self):
        pks = dict(name="Model.System.Model")
        model = self.registry.System.Model.from_primary_keys(**pks)
        value = self.get_value(model, "One2One", model="Model.System.Model")
        assert value == dumps(pks)

    def test_one2one_external_ids(self):
        key = "formater_mapping"
        model = self.registry.System.Model.from_primary_keys(
            name="Model.System.Model"
        )
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(
            model, "One2One", external_id=True, model="Model.System.Model"
        )
        assert value == key

    def test_external_id(self):
        key = "formater_mapping"
        model = self.registry.System.Model.from_primary_keys(
            name="Model.System.Model"
        )
        self.registry.IO.Mapping.set(key, model)
        value = self.get_value(
            model.name, "String", external_id=True, model="Model.System.Model"
        )
        assert value == key

    def test_external_id_without_existing_mapping(self):
        model = self.registry.System.Model.from_primary_keys(
            name="Model.System.Model"
        )
        value = self.get_value(
            model.name, "String", external_id=True, model="Model.System.Model"
        )
        assert value
