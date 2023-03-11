# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid1

import pytest
from sqlalchemy import text

from ..exceptions import IOMappingSetException

try:
    import colour

    has_colour = True
except Exception:
    has_colour = False


try:
    import furl  # noqa

    has_furl = True
except Exception:
    has_furl = False


try:
    import phonenumbers  # noqa

    has_phonenumbers = True
    from sqlalchemy_utils import PhoneNumber as PN
except Exception:
    has_phonenumbers = False


try:
    import pycountry  # noqa

    has_pycountry = True
except Exception:
    has_pycountry = False


@pytest.mark.usefixtures("rollback_registry")
class TestIOMapping:
    @pytest.fixture(autouse=True)
    def transact(self, rollback_registry):
        self.registry = rollback_registry
        self.Mapping = self.registry.IO.Mapping
        self.Model = self.registry.System.Model
        self.Column = self.registry.System.Column
        self.Field = self.registry.System.Field
        self.Blok = self.registry.System.Blok

    def test_set_primary_key(self):
        model = self.Model.query().first()
        res = self.Mapping.set_primary_keys(
            model.__registry_name__, "test_set_pk", dict(name=model.name)
        )
        query = self.Mapping.query()
        query = query.filter(self.Mapping.key == "test_set_pk")
        assert query.count(), 1
        mapping = query.first()
        assert mapping == res
        assert mapping.model == model.__registry_name__
        assert mapping.primary_key == dict(name=model.name)

    def test_set_primary_keys(self):
        column = self.Column.query().first()
        res = self.Mapping.set_primary_keys(
            column.__registry_name__,
            "test_set_pks",
            dict(model=column.model, name=column.name),
        )
        query = self.Mapping.query()
        query = query.filter(self.Mapping.key == "test_set_pks")
        assert query.count() == 1
        mapping = query.first()
        assert mapping == res
        assert mapping.model == column.__registry_name__
        assert mapping.primary_key == dict(model=column.model, name=column.name)

    def test_set(self):
        column = self.Column.query().first()
        res = self.Mapping.set("test_set", column)
        query = self.Mapping.query()
        query = query.filter(self.Mapping.key == "test_set")
        assert query.count() == 1
        mapping = query.first()
        assert mapping == res
        assert mapping.model == column.__registry_name__
        assert mapping.primary_key == dict(model=column.model, name=column.name)

    def test_get_primary_key(self):
        model = self.Model.query().first()
        self.Mapping.set_primary_keys(
            model.__registry_name__, "test_get_pk", dict(name=model.name)
        )
        mapping = self.Mapping.get_mapping_primary_keys(
            model.__registry_name__, "test_get_pk"
        )
        assert mapping == dict(name=model.name)

    def test_get_primary_keys(self):
        column = self.Column.query().first()
        self.Mapping.set_primary_keys(
            column.__registry_name__,
            "test_get_pks",
            dict(model=column.model, name=column.name),
        )
        mapping = self.Mapping.get_mapping_primary_keys(
            column.__registry_name__, "test_get_pks"
        )
        assert mapping == dict(model=column.model, name=column.name)

    def test_get(self):
        column = self.Column.query().first()
        self.Mapping.set("test_get", column)
        mapping = self.Mapping.get(column.__registry_name__, "test_get")
        assert mapping == column

    def test_delete(self):
        column = self.Column.query().first()
        self.Mapping.set("test_delete", column)
        mapping = self.Mapping.get(column.__registry_name__, "test_delete")
        assert mapping == column
        self.Mapping.delete(column.__registry_name__, "test_delete")
        mapping = self.Mapping.get(column.__registry_name__, "test_delete")
        assert mapping is None

    def test_multi_delete(self):
        columns = {
            "test_%s" % m.code: m for m in self.Column.query().limit(5).all()
        }
        model = self.Column.__registry_name__

        # create all
        for key, instance in columns.items():
            self.Mapping.set(key, instance)

        # check all
        for key, instance in columns.items():
            mapping = self.Mapping.get(model, key)
            assert mapping == instance

        # delete all
        self.Mapping.multi_delete(model, *columns.keys())

        # check all
        for key, instance in columns.items():
            mapping = self.Mapping.get(model, key)
            assert mapping != instance
            assert mapping is None

    def test_multi_set_the_same_key_with_raise(self):
        column = self.Column.query().first()
        self.Mapping.set("test_set", column)
        with pytest.raises(IOMappingSetException):
            self.Mapping.set("test_set", column)

    def test_multi_set_the_same_key_without_raise(self):
        column = self.Column.query().first()
        self.Mapping.set("test_set", column)
        self.Mapping.set("test_set", column, raiseifexist=False)

    def test_clean_all(self):
        blok = self.Blok.insert(name="Test", version="0.0.0")
        self.Mapping.set("test", blok)
        self.registry.execute(text("DELETE FROM system_blok WHERE name='Test'"))
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        removed = self.Mapping.clean()
        assert removed == 1
        assert not (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )

    def test_clean_by_bloknames(self):
        self.Blok.insert(name="Test", version="0.0.0")
        blok = self.Blok.insert(name="Test2", version="0.0.0")
        self.Mapping.set("test", blok, blokname="Test")
        self.registry.execute(
            text("DELETE FROM system_blok WHERE name='Test2'")
        )
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        removed = self.Mapping.clean(bloknames=["wrong"])
        assert removed == 0
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        removed = self.Mapping.clean(bloknames=["Test"])
        assert removed == 1
        assert not (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )

    def test_clean_by_blokname(self):
        self.Blok.insert(name="Test", version="0.0.0")
        blok = self.Blok.insert(name="Test2", version="0.0.0")
        self.Mapping.set("test", blok, blokname="Test")
        self.registry.execute(
            text("DELETE FROM system_blok WHERE name='Test2'")
        )
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        self.Mapping.clean(bloknames="Test")
        assert not (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )

    def test_clean_by_models_1(self):
        blok = self.Blok.insert(name="Test", version="0.0.0")
        self.Mapping.set("test", blok)
        self.registry.execute(text("DELETE FROM system_blok WHERE name='Test'"))
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        self.Mapping.clean(models=["Model.System.Column"])
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        self.Mapping.clean(models=["Model.System.Blok"])
        assert not (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )

    def test_clean_by_models_2(self):
        blok = self.Blok.insert(name="Test", version="0.0.0")
        self.Mapping.set("test", blok)
        self.registry.execute(text("DELETE FROM system_blok WHERE name='Test'"))
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        self.Mapping.clean(models=[self.Column])
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        self.Mapping.clean(models=[self.Blok])
        assert not (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )

    def test_clean_by_model(self):
        blok = self.Blok.insert(name="Test", version="0.0.0")
        self.Mapping.set("test", blok)
        self.registry.execute(text("DELETE FROM system_blok WHERE name='Test'"))
        assert (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )
        self.Mapping.clean(models=self.Blok)
        assert not (
            self.Mapping.query()
            .filter_by(key="test", model="Model.System.Blok")
            .count()
        )

    def test_detect_key_from_model_and_primary_key(self):
        Mapping = self.registry.IO.Mapping
        Blok = self.registry.System.Blok

        values = []
        for i, blok in enumerate(Blok.query().all()):
            values.append(
                dict(
                    key="key_%d" % i,
                    model=Blok.__registry_name__,
                    primary_key=blok.to_primary_keys(),
                )
            )

        Mapping.multi_insert(*values)
        mapping = Mapping.get_from_model_and_primary_keys(
            Blok.__registry_name__, blok.to_primary_keys()
        )
        entry = Mapping.get(blok.__registry_name__, mapping.key)
        assert entry == blok

    def test_delete_for_blokname(self):
        self.Blok.insert(name="Test", version="0.0.0")
        assert not (self.Mapping.query().filter_by(blokname="Test").count())
        for column in self.Column.query().limit(10).all():
            self.Mapping.set("test_" + column.code, column, blokname="Test")
        assert self.Mapping.query().filter_by(blokname="Test").count()

        removed = self.Mapping.delete_for_blokname("Test")
        assert removed == 10
        assert not (self.Mapping.query().filter_by(blokname="Test").count())

    def test_delete_for_blokname_filter_by_model_1(self):
        self.Blok.insert(name="Test", version="0.0.0")
        nb_column = self.Column.query().count()
        assert not (self.Mapping.query().filter_by(blokname="Test").count())
        for field in self.Field.query().all():
            self.Mapping.set("test_" + field.code, field, blokname="Test")

        assert (
            self.Mapping.query().filter_by(blokname="Test").count()
            == self.Field.query().count()
        )
        removed = self.Mapping.delete_for_blokname(
            "Test", ["Model.System.Column"]
        )
        assert removed == nb_column

    def test_delete_for_blokname_filter_by_model_2(self):
        nb_column = self.Column.query().count()
        self.Blok.insert(name="Test", version="0.0.0")
        assert not (self.Mapping.query().filter_by(blokname="Test").count())
        for field in self.Field.query().all():
            self.Mapping.set("test_" + field.code, field, blokname="Test")

        assert (
            self.Mapping.query().filter_by(blokname="Test").count()
            == self.Field.query().count()
        )
        removed = self.Mapping.delete_for_blokname(
            "Test", [self.registry.System.Column]
        )
        assert removed == nb_column

    def test_delete_for_blokname_filter_by_model_3(self):
        nb_column = self.Column.query().count()
        self.Blok.insert(name="Test", version="0.0.0")
        assert not (self.Mapping.query().filter_by(blokname="Test").count())
        for field in self.Field.query().all():
            self.Mapping.set("test_" + field.code, field, blokname="Test")

        assert (
            self.Mapping.query().filter_by(blokname="Test").count()
            == self.Field.query().count()
        )
        removed = self.Mapping.delete_for_blokname(
            "Test", self.registry.System.Column
        )
        assert removed == nb_column

    def test_convert_primary_key_uuid(self):
        uuid = uuid1()
        assert self.Mapping.convert_primary_key(uuid) == str(uuid)

    def test_convert_primary_key_date(self):
        today = date.today()
        assert self.Mapping.convert_primary_key(today) == today.isoformat()

    def test_convert_primary_key_datetime(self):
        now = datetime.now()
        assert self.Mapping.convert_primary_key(now) == now.isoformat()

    def test_convert_primary_key_decimal(self):
        assert self.Mapping.convert_primary_key(Decimal("1")) == "1"

    @pytest.mark.skipif(not has_furl, reason="furl is not installed")
    def test_convert_primary_key_furl(self):
        url = "http://doc.anyblok.org"
        assert self.Mapping.convert_primary_key(furl.furl(url)) == url

    @pytest.mark.skipif(
        not has_phonenumbers, reason="phonenumbers is not installed"
    )
    def test_convert_primary_key_phonenumber(self):
        phone = PN("+120012301", None)
        assert self.Mapping.convert_primary_key(phone) == "+1 20012301"

    @pytest.mark.skipif(not has_pycountry, reason="pycountry is not installed")
    def test_convert_primary_key_country(self):
        country = pycountry.countries.get(alpha_2="FR")
        assert self.Mapping.convert_primary_key(country) == "FRA"

    @pytest.mark.skipif(not has_colour, reason="colour is not installed")
    def test_convert_primary_key_color(self):
        color = "#f5f5f5"
        assert self.Mapping.convert_primary_key(colour.Color(color)) == color
