# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest  # noqa


class TestBlok:
    def test_import_file(self, registry_testblok):
        registry_testblok.upgrade(install=("test-io-blok1", "test-io-blok2"))
        assert registry_testblok.Exemple.query().count() == 6
