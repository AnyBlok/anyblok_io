# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from logging import getLogger
from os.path import join
from datetime import datetime
from anyblok.blok import BlokManager

logger = getLogger(__name__)


class BlokImporter:

    def import_file_csv(self, model, *file_path, **kwargs):
        if not self.registry.System.Blok.is_installed('anyblok-io-csv'):
            raise Exception('anyblok-io-csv is not installed in the project')

        Importer = self.registry.IO.Importer.CSV
        return self.import_file(Importer, model, *file_path, **kwargs)

    def import_file_xml(self, model, *file_path, **kwargs):
        if not self.registry.System.Blok.is_installed('anyblok-io-xml'):
            raise Exception('anyblok-io-xml is not installed in the project')

        Importer = self.registry.IO.Importer.XML
        return self.import_file(Importer, model, *file_path, **kwargs)

    def import_file(self, Importer, model, *file_path, **kwargs):
        """ Import data file

        :param importer_name: Name of the importer (need installation of the
                              Blok which have the importer)
        :param model: Model of the data to import
        :param \*file_path: relative path of the path in this Blok
        :param \*\*kwargs: Option for the importer
        :rtype: return dict of result
        """
        blok_path = BlokManager.getPath(self.name)
        _file = join(blok_path, *file_path)
        logger.info("import %r file: %r", Importer, _file)
        file_to_import = None
        with open(_file, 'rb') as fp:
            file_to_import = fp.read()

        importer = Importer.insert(
            model=model, file_to_import=file_to_import, **kwargs)
        started_at = datetime.now()
        res = importer.run(self.name)
        stoped_at = datetime.now()
        dt = stoped_at - started_at
        logger.info("Create %d entries, Update %d entries (%d.%d sec)",
                    len(res['created_entries']), len(res['updated_entries']),
                    dt.seconds, dt.microseconds)
        if 'error_found' in res and res['error_found']:
            for error in res['error_found']:
                logger.error(error)
        else:
            importer.delete()

        return res
