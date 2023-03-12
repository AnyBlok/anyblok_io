# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest


@pytest.mark.usefixtures("rollback_registry")
class TestExportXML:
    @pytest.fixture(autouse=True)
    def transact(self, rollback_registry):
        self.registry = rollback_registry

    def create_exporter(self, Model, **kwargs):
        Exporter = self.registry.IO.Exporter.XML
        return Exporter.insert(model=Model, **kwargs)

    def test_export_anyblok_core(self):
        Blok = self.registry.System.Blok
        fields = [{"name": "name", "mode": "external_id"}, {"name": "state"}]
        exporter = self.create_exporter(Blok, fields=fields)
        blok = Blok.from_primary_keys(name="anyblok-core")
        with pytest.raises(NotImplementedError):
            exporter.run([blok])
