# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from os import urandom

import pytest
from lxml import etree

from ..exceptions import XMLImporterException


@pytest.mark.usefixtures("rollback_registry")
class TestImportXML:
    @pytest.fixture(autouse=True)
    def transact(self, rollback_registry):
        self.registry = rollback_registry

    def create_importer(self, file_to_import=None, **kwargs):
        XML = self.registry.IO.Importer.XML
        if "model" not in kwargs:
            kwargs["model"] = "Model.IO.Importer"

        if file_to_import is None:
            file_to_import = urandom(100000)
        return XML.insert(file_to_import=file_to_import, **kwargs)

    def create_XML_importer(self, blokname=None, **kwargs):
        XML = self.registry.IO.Importer.XML
        return XML(self.create_importer(**kwargs), blokname=blokname)

    def test_commit_if_error_found(self):
        importer = self.create_XML_importer()
        importer.error_found.append("Mock error")
        assert importer.commit() is False

    def test_commit(self):
        importer = self.create_XML_importer()
        assert importer.commit() is True

    def test_raise_now(self):
        importer = self.create_XML_importer()
        msg = "test"
        with pytest.raises(XMLImporterException):
            importer._raise(msg, on_error="raise")

        assert msg in importer.error_found

    def test_raise_at_the_end(self):
        importer = self.create_XML_importer()
        msg = "test"
        importer._raise(msg)
        assert msg in importer.error_found

    def test_raise_ignore(self):
        importer = self.create_XML_importer()
        msg = "test"
        importer._raise(msg, on_error="ignore")
        assert msg in importer.error_found

    def test_find_entry(self):
        importer = self.create_XML_importer()
        assert importer.find_entry() is None

    def test_find_entry_params(self):
        importer = self.create_XML_importer()
        model = "Model.System.Model"
        param = "test_param"
        importer.params[(model, param)] = importer
        assert importer.find_entry(model=model, param=param) == importer

    def test_find_entry_external_id(self):
        importer = self.create_XML_importer()
        param = "test_param"
        self.registry.IO.Mapping.set(param, importer.importer)
        assert (
            importer.find_entry(
                model=importer.importer.__registry_name__, external_id=param
            )
            == importer.importer
        )

    def test_check_entry_before_import(self):
        importer = self.create_XML_importer()
        record = etree.Element("record")
        assert importer.check_entry_before_import(record, importer) == (
            False,
            importer,
        )
        assert importer.error_found == []

    def test_check_entry_before_import_if_exist_pass(self):
        importer = self.create_XML_importer()
        record = etree.Element("record")
        assert importer.check_entry_before_import(
            record, importer, if_exist="pass"
        ) == (True, importer)
        assert importer.error_found == []

    def test_check_entry_before_import_if_exist_raise(self):
        importer = self.create_XML_importer()
        record = etree.Element("record")
        assert importer.check_entry_before_import(
            record, importer, if_exist="raise"
        ) == (True, None)
        assert len(importer.error_found) == 1

    def test_check_entry_before_import_if_does_not_exist_pass(self):
        importer = self.create_XML_importer()
        record = etree.Element("record")
        assert importer.check_entry_before_import(
            record, None, if_does_not_exist="pass"
        ) == (True, None)
        assert len(importer.error_found) == 0

    def test_check_entry_before_import_if_does_not_exist_raise(self):
        importer = self.create_XML_importer()
        record = etree.Element("record")
        assert importer.check_entry_before_import(
            record, None, if_does_not_exist="raise"
        ) == (True, None)
        assert len(importer.error_found) == 1

    def test_import_entry_if_exist_continue(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        assert (
            importer.import_entry(
                importer, None, model=model, if_exist="continue"
            )
            == importer
        )
        assert len(importer.created_entries) == 0
        assert len(importer.updated_entries) == 0
        assert len(importer.error_found) == 0

    def test_import_entry_if_exist_create(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        values = {
            "model": model,
            "mode": model + ".XML",
            "file_to_import": urandom(100000),
        }
        assert (
            importer.import_entry(
                importer, values, model=model, if_exist="create"
            )
            != importer
        )
        assert len(importer.created_entries) == 1
        assert len(importer.updated_entries) == 0
        assert len(importer.error_found) == 0

    def test_import_entry_if_exist_update(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        values = {
            "model": model,
            "mode": model + ".XML",
            "file_to_import": urandom(100000),
        }
        assert (
            importer.import_entry(importer.importer, values, model=model)
            == importer.importer
        )
        assert len(importer.created_entries) == 0
        assert len(importer.updated_entries) == 1
        assert len(importer.error_found) == 0

    def test_import_entry_if_does_not_exist_create(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        values = {
            "model": model,
            "mode": model + ".XML",
            "file_to_import": urandom(100000),
        }
        importer.import_entry(None, values, model=model, if_exist="create")
        assert len(importer.created_entries) == 1
        assert len(importer.updated_entries) == 0
        assert len(importer.error_found) == 0

    def test_import_entry_external_id(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        importer.import_entry(
            importer.importer,
            None,
            model=model,
            if_exist="continue",
            external_id="test_import",
        )
        assert (
            self.registry.IO.Mapping.get(model, "test_import")
            == importer.importer
        )

    def test_import_entry_external_id_with_blokname(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        importer.import_entry(
            importer.importer,
            None,
            model=model,
            if_exist="continue",
            external_id="test_import",
        )
        mapping = self.registry.IO.Mapping.get(model, "test_import")
        mapping.blokname = "Test"

    def test_import_entry_mapper(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        importer.import_entry(
            importer,
            None,
            model=model,
            if_exist="continue",
            param="test_import",
        )
        assert importer.params[(model, "test_import")] == importer

    def test_import_entry_mapper_exist(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        importer.params[(model, "test_import")] = importer
        importer.import_entry(
            importer,
            None,
            model=model,
            if_exist="continue",
            param="test_import",
        )
        assert importer.params[(model, "test_import")] == importer

    def test_import_entry_mapper_exist_and_not_the_same(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        importer.params[(model, "test_import")] = importer.importer
        importer.import_entry(
            importer,
            None,
            model=model,
            if_exist="continue",
            param="test_import",
        )
        assert len(importer.error_found) == 1

    def test_import_multi_value(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        record1 = etree.Element("field")
        record1.set("model", model)
        field = etree.SubElement(record1, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record1, "field")
        field.set("name", "mode")
        field.text = model + ".XML"
        record2 = etree.Element("field")
        record2.set("model", model)
        field = etree.SubElement(record2, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record2, "field")
        field.set("name", "mode")
        field.text = model + ".XML"

        res = importer.import_multi_values([record1, record2], model)
        assert len(res) == 2
        assert len(importer.error_found) == 0
        assert len(importer.created_entries) == 2

    def test_import_value(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        record = etree.Element("field")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"

        res = importer.import_value(record, "Integer", model)
        assert isinstance(res, int)
        assert len(importer.error_found) == 0
        assert len(importer.created_entries) == 1

    def test_import_value_relation_ship(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        record = etree.Element("field")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"

        res = importer.import_value(record, "Many2One", model)
        assert isinstance(res.id, int)
        assert len(importer.error_found) == 0
        assert len(importer.created_entries) == 1

    def test_import_field(self):
        importer = self.create_XML_importer()
        field = etree.Element("field")
        field.set("name", "model")
        field.text = "Model.IO.Importer"
        assert (
            importer.import_field(self.registry.IO.Importer, field, "String")
            == field.text
        )

    def test_import_field_external_id(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        _model = self.registry.System.Model.query().get(model)
        self.registry.IO.Mapping.set("test_import", _model)
        field = etree.Element("field")
        field.set("name", "model")
        field.set("external_id", "test_import")
        assert (
            importer.import_field(
                self.registry.IO.Importer,
                field,
                "String",
                model="Model.System.Model",
            )
            == model
        )
        assert len(importer.error_found) == 0

    def test_import_field_external_id_without_model(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        _model = self.registry.System.Model.query().get(model)
        self.registry.IO.Mapping.set("test_import", _model)
        field = etree.Element("field")
        field.set("name", "model")
        field.set("external_id", "test_import")
        assert (
            importer.import_field(self.registry.IO.Importer, field, "String")
            is None
        )
        assert len(importer.error_found) == 1

    def test_import_field_params(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        importer.params[(model, "test_import")] = importer
        field = etree.Element("field")
        field.set("name", "model")
        field.set("param", "test_import")
        assert (
            importer.import_field(
                self.registry.IO.Importer, field, "String", model=model
            )
            == importer
        )
        assert len(importer.error_found) == 0

    def test_import_field_inexisting_params(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        importer.params[(model, "test_import")] = model
        field = etree.Element("field")
        field.set("name", "model")
        field.set("param", "test_import")
        field.text = "Model.IO.Importer"
        assert (
            importer.import_field(
                self.registry.IO.Importer, field, "String", model=model
            )
            == field.text
        )
        assert len(importer.error_found) == 0
        assert importer.params[(model, "test_import")] == field.text

    def test_import_field_params_without_model(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Importer"
        importer.params[(model, "test_import")] = importer
        field = etree.Element("field")
        field.set("name", "model")
        field.set("param", "test_import")
        assert (
            importer.import_field(self.registry.IO.Importer, field, "String")
            is None
        )
        assert len(importer.error_found) == 1

    def test_import_record_without_model(self):
        importer = self.create_XML_importer()
        record = etree.Element("record")
        assert importer.import_record(record) is None
        assert len(importer.error_found) == 1

    def test_import_record_with_wrong_node(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        record = etree.Element("record")
        record.set("model", model)
        etree.SubElement(record, "badnode")
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"

        importer.import_record(record)
        assert len(importer.error_found) == 1

    def test_import_record_field_without_name(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        record = etree.Element("record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"

        importer.import_record(record)
        assert len(importer.error_found) == 1

    def test_import_record(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        record = etree.Element("record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"

        importer.import_record(record)
        assert len(importer.error_found) == 0
        assert len(importer.created_entries) == 1

    def test_import_records(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        records = etree.Element("records")
        record = etree.SubElement(records, "record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"

        importer.import_records(records)
        assert len(importer.error_found) == 0
        assert len(importer.created_entries) == 1

    def test_import_records_with_bad_node(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        records = etree.Element("records")
        etree.SubElement(records, "badnode")
        record = etree.SubElement(records, "record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"

        importer.import_records(records)
        assert len(importer.error_found) == 1
        assert len(importer.created_entries) == 1

    def test_import_records_with_commit(self):
        importer = self.create_XML_importer()
        model = "Model.IO.Exporter"
        records = etree.Element("records")
        record = etree.SubElement(records, "record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"
        etree.SubElement(records, "commit")

        importer.import_records(records)
        assert len(importer.error_found) == 0
        assert len(importer.created_entries) == 1

    def test_run_raise(self):
        model = "Model.IO.Exporter"
        records = etree.Element("records")
        records.set("on_error", "raise")
        record = etree.SubElement(records, "record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"
        file_to_import = etree.tostring(records)
        importer = self.create_XML_importer(file_to_import=file_to_import)
        with pytest.raises(XMLImporterException):
            importer.run()

        assert len(importer.error_found) == 1

    def test_run_raise_ignore(self):
        model = "Model.IO.Exporter"
        records = etree.Element("records")
        records.set("on_error", "ignore")
        record = etree.SubElement(records, "record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"
        file_to_import = etree.tostring(records)
        importer = self.create_XML_importer(file_to_import=file_to_import)
        res = importer.run()
        assert len(res["error_found"]) == 1

    def test_run(self):
        model = "Model.IO.Exporter"
        records = etree.Element("records")
        record = etree.SubElement(records, "record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"
        file_to_import = etree.tostring(records)
        importer = self.create_XML_importer(file_to_import=file_to_import)
        res = importer.run()
        assert len(res["error_found"]) == 0
        assert len(res["created_entries"]) == 1
        assert len(res["updated_entries"]) == 0

    def test_run_bad_root_name(self):
        model = "Model.IO.Exporter"
        records = etree.Element("badrootname")
        records.set("on_error", "ignore")
        record = etree.SubElement(records, "record")
        record.set("model", model)
        field = etree.SubElement(record, "field")
        field.set("name", "model")
        field.text = model
        field = etree.SubElement(record, "field")
        field.set("name", "mode")
        field.text = model + ".XML"
        file_to_import = etree.tostring(records)
        importer = self.create_XML_importer(file_to_import=file_to_import)
        res = importer.run()
        assert len(res["error_found"]) == 1
        assert len(res["created_entries"]) == 0
        assert len(res["updated_entries"]) == 0
