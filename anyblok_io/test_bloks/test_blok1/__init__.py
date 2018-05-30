# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok_io.blok import BlokImporter


class TestBlok(BlokImporter, Blok):

    version = '1.0.0'
    required = ['anyblok-io-csv']

    @classmethod
    def import_declaration_module(cls):
        from . import test  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import test
        reload(test)

    def update(self, latest_version):
        self.import_file_csv('Model.Exemple', 'file.csv')
