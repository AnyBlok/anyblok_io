# This file is a part of the AnyBlok project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2021 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import os

from setuptools import find_packages, setup

version = "1.2.0"

requires = [
    "anyblok>=1.2.0",
    "lxml",
]

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst"), "r", encoding="utf-8") as readme:
    README = readme.read()

with open(
    os.path.join(here, "doc", "CHANGES.rst"), "r", encoding="utf-8"
) as change:
    CHANGE = change.read()

with open(
    os.path.join(here, "doc", "FRONT.rst"), "r", encoding="utf-8"
) as front:
    FRONT = front.read()

setup(
    name="anyblok_io",
    version=version,
    author="Jean-Sébastien Suzanne",
    author_email="js.suzanne@gmail.com",
    description="Add importer / exporter to AnyBlok",
    license="MPL2",
    long_description=README + "\n" + FRONT + "\n" + CHANGE,
    url="http://docs.anyblok.org/%s" % version,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=requires,
    tests_require=requires + ["pytest", "pytest-cov"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
    ],
    entry_points={
        "bloks": [
            "anyblok-io=anyblok_io.bloks.io:AnyBlokIO",
            "anyblok-io-csv=anyblok_io.bloks.io_csv:AnyBlokIOCSV",
            "anyblok-io-xml=anyblok_io.bloks.io_xml:AnyBlokIOXML",
        ],
        "test_bloks": [
            "test-io-blok1=anyblok_io.test_bloks.test_blok1:TestBlok",
            "test-io-blok2=anyblok_io.test_bloks.test_blok2:TestBlok",
            "test-io-blok3=anyblok_io.test_bloks.test_blok3:TestBlok",
            "test-io-blok4=anyblok_io.test_bloks.test_blok4:TestBlok",
        ],
    },
    extras_require={},
)
