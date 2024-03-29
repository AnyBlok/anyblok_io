# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.

from ..io.exceptions import ExporterException, ImporterException


class XMLImporterException(ImporterException):
    """Simple exception for XML importer"""


class XMLExporterException(ExporterException):
    """Simple exception for XML exporter"""
