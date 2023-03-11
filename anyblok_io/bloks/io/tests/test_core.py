# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from sqlalchemy import func


@pytest.mark.usefixtures('rollback_registry')
class TestIOCore:

    @pytest.fixture(autouse=True)
    def transact(self, rollback_registry):
        self.registry = rollback_registry

    def checkExist(self):
        Mapping = self.registry.IO.Mapping
        assert Mapping.execute_sql_statement(
            Mapping.select_sql_statement(func.count()).where(
                Mapping.key == 'test', Mapping.model == 'Model.System.Blok')
        ).scalar()

    def checkUnExist(self):
        Mapping = self.registry.IO.Mapping
        assert not Mapping.execute_sql_statement(
            Mapping.select_sql_statement(func.count()).where(
                Mapping.key == 'test', Mapping.model == 'Model.System.Blok')
        ).scalar()

    def test_session_delete_obj_with_mapping(self):
        Mapping = self.registry.IO.Mapping
        Blok = self.registry.System.Blok
        blok = Blok.insert(name='Test', version='0.0.0')
        self.checkUnExist()
        Mapping.set('test', blok)
        self.checkExist()
        blok.delete()
        self.checkUnExist()

    def test_delete_statement_with_mapping(self):
        Mapping = self.registry.IO.Mapping
        Blok = self.registry.System.Blok
        blok = Blok.insert(name='Test', version='0.0.0')
        self.checkUnExist()
        Mapping.set('test', blok)
        self.checkExist()
        Blok.execute_sql_statement(
            Blok.delete_sql_statement().filter_by(name='Test')
        )
        self.checkUnExist()
