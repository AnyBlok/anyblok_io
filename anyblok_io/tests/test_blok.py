# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase


class TestBlokRequired(DBTestCase):

    blok_entry_points = ('bloks', 'test_bloks')

    def test_import_file_csv(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test-io-blok1',))
        self.assertEqual(registry.Exemple.query().count(), 3)

    def test_import_file_xml(self):
        registry = self.init_registry(None)
        registry.upgrade(install=('test-io-blok2',))
        self.assertEqual(registry.Exemple.query().count(), 3)
