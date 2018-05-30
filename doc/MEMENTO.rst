.. This file is a part of the AnyBlok project
..
..    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

MEMENTO
=======

Blok
----

The **BlokImporter** give some behaviour to help to import file from the blok::

    from anyblok.blok import Blok
    from anyblok_io.blok import BlokImporter

    class MyBlok(BlokImporter, Blok):

        required = ['anyblok-io-csv', 'anyblok-io-xml']

        def upload(self, latest_version=None):
            self.import_file_csv(Model, *file_path, **ImporterOptions)  # need anyblok-io-csv
            self.import_file_xml(Model, *file_path, **ImporterOptions)  # need anyblok-io-xml
