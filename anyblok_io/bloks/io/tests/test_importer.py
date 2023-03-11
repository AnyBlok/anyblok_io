# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest


@pytest.mark.usefixtures("rollback_registry")
class TestImporter:
    @pytest.fixture(autouse=True)
    def transact(self, rollback_registry):
        self.registry = rollback_registry

    def create_importer(self, **kwargs):
        Importer = self.registry.IO.Importer
        kwargs["model"] = "Model.IO.Importer"
        if "check_import" not in kwargs:
            kwargs["check_import"] = False

        if "commit_at_each_grouped" not in kwargs:
            kwargs["commit_at_each_grouped"] = True

        return Importer(**kwargs)

    def test_commit_if_check(self):
        importer = self.create_importer(check_import=True)
        assert importer.commit() is False

    def test_commit_if_not_commit_at_each_group(self):
        importer = self.create_importer(commit_at_each_grouped=False)
        assert importer.commit() is False

    def test_commit(self):
        importer = self.create_importer()
        assert importer.commit() is True
