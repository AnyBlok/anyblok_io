# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from anyblok.release import version


class AnyBlokIOXML(Blok):
    """XML Importer / Exporter behaviour

    .. warning::

        Importer and Exporter are not implemented yet

    """

    version = version
    author = "Suzanne Jean-Sébastien"

    required = [
        "anyblok-io",
    ]

    @classmethod
    def import_declaration_module(cls):
        from . import exporter  # noqa
        from . import importer  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import importer

        reload(importer)
        from . import exporter

        reload(exporter)
