# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest

from anyblok_io.blok import BlokImporterException


class TestBlok:
    @pytest.fixture(autouse=True)
    def transact(self, request, registry_testblok):
        transaction = registry_testblok.begin_nested()
        request.addfinalizer(transaction.rollback)
        return

    def test_import_file_csv_ok(self, registry_testblok):
        registry_testblok.upgrade(install=("test-io-blok1",))
        assert registry_testblok.Exemple.query().count() == 3

    def test_import_file_xml_ok(self, registry_testblok):
        registry_testblok.upgrade(install=("test-io-blok2",))
        assert registry_testblok.Exemple.query().count() == 3


class TestBlok2:
    def test_import_file_csv_ko(self, registry_testblok):
        with pytest.raises(BlokImporterException):
            registry_testblok.upgrade(install=("test-io-blok3",))


class TestBlok3:
    def test_import_file_xml_ko(self, registry_testblok):
        with pytest.raises(BlokImporterException):
            registry_testblok.upgrade(install=("test-io-blok4",))
