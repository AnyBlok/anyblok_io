# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from csv import DictReader

import pytest

from ..exceptions import CSVExporterException


@pytest.mark.usefixtures("rollback_registry")
class TestExportCSV:
    @pytest.fixture(autouse=True)
    def transact(self, rollback_registry):
        self.registry = rollback_registry

    def create_exporter(self, Model, **kwargs):
        Exporter = self.registry.IO.Exporter.CSV
        return Exporter.insert(model=Model, **kwargs)

    def test_create_exporter_by_registry_name(self):
        exporter = self.create_exporter("Model.IO.Exporter")
        assert exporter.model == "Model.IO.Exporter"

    def test_create_exporter_by_model(self):
        exporter = self.create_exporter(self.registry.IO.Exporter)
        assert exporter.model == "Model.IO.Exporter"

    def test_create_exporter_with_field(self):
        fields = [{"name": "model"}]
        exporter = self.create_exporter(
            self.registry.IO.Exporter, fields=fields
        )
        assert exporter.model == "Model.IO.Exporter"
        assert len(exporter.fields_to_export) == 1
        assert exporter.fields_to_export[0].name == "model"

    def test_create_exporter_with_two_fields(self):
        fields = [{"name": "model"}, {"name": "csv_delimiter"}]
        exporter = self.create_exporter(
            self.registry.IO.Exporter, fields=fields
        )
        assert exporter.model == "Model.IO.Exporter"
        assert len(exporter.fields_to_export) == 2

    def test_get_header_from_fields_any(self):
        fields = [{"name": "id"}]
        exporter = self.create_exporter(
            self.registry.IO.Exporter, fields=fields
        )
        res = exporter.get_model(exporter.mode)(exporter).get_header()
        assert len(res) == 1
        assert res[0] == "id"

    def test_get_header_from_fields_external_id(self):
        fields = [{"name": "id", "mode": "external_id"}]
        exporter = self.create_exporter(
            self.registry.IO.Exporter, fields=fields
        )
        res = exporter.get_model(exporter.mode)(exporter).get_header()
        assert len(res) == 1
        assert res[0] == "id/EXTERNAL_ID"

    def test_format_field_with_mapping_any(self):
        Exporter = self.registry.IO.Exporter
        fields = [{"name": "id"}]
        exporter = self.create_exporter(Exporter, fields=fields)
        res = exporter.fields_to_export[0].value2str(exporter, exporter)
        assert res == str(exporter.id)

    def test_format_field_with_mapping_external_id(self):
        Exporter = self.registry.IO.Exporter
        fields = [{"name": "id", "mode": "external_id"}]
        exporter = self.create_exporter(Exporter, fields=fields)
        key = Exporter.get_external_id(exporter.model)
        key = key.split("_")
        key = "_".join([key[0], str(int(key[1]) + 1)])
        res = exporter.fields_to_export[0].value2str(exporter, exporter)
        assert res == key

    def test_format_field_with_forbidden_mapping_external_id(self):
        Exporter = self.registry.IO.Exporter
        fields = [{"name": "id.other", "mode": "external_id"}]
        exporter = self.create_exporter(Exporter, fields=fields)
        with pytest.raises(CSVExporterException):
            exporter.fields_to_export[0].value2str(exporter, exporter)

    def test_format_browsed_field_with_mapping_any(self):
        Exporter = self.registry.IO.Exporter
        fields = [{"name": "model.is_sql_model"}]
        exporter = self.create_exporter(Exporter, fields=fields)
        res = exporter.fields_to_export[0].value2str(exporter, exporter)
        assert res == "1"

    def test_format_browsed_field_pks_without_mapping_key(self):
        Exporter = self.registry.IO.Exporter
        fields = [{"name": "model.name"}]
        exporter = self.create_exporter(Exporter, fields=fields)
        res = exporter.fields_to_export[0].value2str(exporter, exporter)
        assert res == "Model.IO.Exporter"

    def test_format_browsed_field_with_mapping_key(self):
        Exporter = self.registry.IO.Exporter
        fields = [{"name": "model.name", "mode": "external_id"}]
        exporter = self.create_exporter(Exporter, fields=fields)
        model = self.registry.System.Model.from_primary_keys(
            name=Exporter.__registry_name__
        )
        key = self.registry.IO.Exporter.get_key_mapping(model)
        res = exporter.fields_to_export[0].value2str(exporter, exporter)
        assert res == key

    def test_format_browsed_field_with_mapping_Many2One(self):
        Field = self.registry.IO.Exporter.Field
        fields = [{"name": "exporter.id", "mode": "external_id"}]
        exporter = self.create_exporter(Field, fields=fields)
        key = self.registry.IO.Exporter.get_key_mapping(exporter)
        res = exporter.fields_to_export[0].value2str(
            exporter, exporter.fields_to_export[0])
        assert res == key

    def test_export_anyblok_core(self):
        Blok = self.registry.System.Blok
        fields = [{"name": "name", "mode": "external_id"}, {"name": "state"}]
        exporter = self.create_exporter(Blok, fields=fields)
        blok = Blok.from_primary_keys(name="anyblok-core")
        key = self.registry.IO.Exporter.get_key_mapping(blok)
        csvfile = exporter.run([blok])
        reader = DictReader(
            csvfile,
            delimiter=exporter.csv_delimiter,
            quotechar=exporter.csv_quotechar,
        )
        rows = [x for x in reader]
        csvfile.close()
        assert len(rows) == 1
        assert rows[0]["name/EXTERNAL_ID"] == key
        assert rows[0]["state"] == "installed"

    def test_export_all_bloks(self):
        Blok = self.registry.System.Blok
        fields = [
            {"name": "name"},
            {"name": "state"},
            {"name": "version"},
            {"name": "installed_version"},
            {"name": "order"},
        ]
        exporter = self.create_exporter(Blok, fields=fields)
        bloks = Blok.query().all()
        exporter.run(bloks)

    def test_export_anyblok_core_wrong_field(self):
        Blok = self.registry.System.Blok
        fields = [{"name": "name", "mode": "external_id"}, {"name": "wrong"}]
        exporter = self.create_exporter(Blok, fields=fields)
        blok = Blok.from_primary_keys(name="anyblok-core")
        with pytest.raises(CSVExporterException):
            exporter.run([blok])
