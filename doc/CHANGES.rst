.. This file is a part of the AnyBlok project
..
..    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

CHANGELOG
=========

1.1.1
-----

* Fixed the size of the fields **model**, because they have a
  foreign key to the model  **Model.System.Model** on the field
  **name**. The next version of AnyBlok check that the size are the same

1.1.0 (2020-05-06)
------------------

* Removed **Python 3.4** capability
* Removed **Python 3.5** capability
* Refactored unittest, replaced nose by pytest
* Fixed #1 added hook to render primary key serializable


1.0.0 (2018-05-30)
------------------

* Cherry pick io bloks from AnyBlok distribution
