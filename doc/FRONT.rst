.. This file is a part of the AnyBlok project
..
..    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. AnyBlok documentation master file, created by
   sphinx-quickstart on Mon Feb 24 10:12:33 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. contents::

Front Matter
============

Information about the AnyBlok project.

Project Homepage
----------------

AnyBlok is hosted on `github <http://github.com>`_ - the main project
page is at http://github.com/AnyBlok/anyblok_io. Source code is tracked here
using `GIT <https://git-scm.com>`_.

Releases and project status are available on Pypi at
http://pypi.python.org/pypi/anyblok_io.

The most recent published version of this documentation should be at
https://anyblok-io.readthedocs.io/en/latest/.

Installation
------------

Install released versions of AnyBlok from the Python package index with
`pip <http://pypi.python.org/pypi/pip>`_ or a similar tool::

    pip install anyblok_io


Running Tests
-------------

.. .. seealso:: the :ref:`section about testing of AnyBlok applications
..              <basedoc_tests>`.


To run framework tests with ``pytest`` and ``PostgreSQL``::

    pip install pytest pytest-cov
    ANYBLOK_DATABASE_DRIVER=postgresql ANYBLOK_DATABASE_NAME=anyblok_test pytest anyblok_io/tests

To run bloks tests with ``pytest`` and ``PostgreSQL``::


    pip install pytest pytest-cov
    ANYBLOK_DATABASE_DRIVER=postgresql ANYBLOK_DATABASE_NAME=anyblok_test anyblok_createdb --install-all-bloks
    ANYBLOK_DATABASE_DRIVER=postgresql ANYBLOK_DATABASE_NAME=anyblok_test pytest anyblok_io/tests


AnyBlok is tested continuously using Github actions

Contributing (hackers needed!)
------------------------------

Anyblok is at a very early stage, feel free to fork, talk with core dev, and spread the word!

Author
------

Jean-Sébastien Suzanne

Contributors
------------

* Jean-Sébastien Suzanne

Bugs
----

Bugs and feature enhancements to AnyBlok should be reported on the `Issue
tracker <https://github.com/AnyBlok/anyblok_io/issues>`_.
