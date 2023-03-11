# This file is a part of the AnyBlok project
#
#    Copyright (C) 2015 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#    Copyright (C) 2021 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from sqlalchemy import select


@Declarations.register(Declarations.Core)
class SqlBase:
    @classmethod
    def execute_sql_statement(cls, statement, *args, **kwargs):
        remove_mapping = kwargs.pop("remove_mapping", True)
        if remove_mapping:
            if str(statement).startswith("DELETE FROM "):
                Mapping = cls.anyblok.IO.Mapping
                mappings = []
                stmt = select(statement.table).where(*statement._where_criteria)
                entries = cls.execute_sql_statement(
                    stmt, remove_mapping=False
                ).scalars()

                for entry in entries:
                    mapping = Mapping.get_from_model_and_primary_keys(
                        entry.__registry_name__, entry.to_primary_keys()
                    )
                    if mapping and mapping not in mappings:
                        mappings.append(mapping)

                res = super(SqlBase, cls).execute_sql_statement(
                    statement, *args, **kwargs
                )

                for mapping in mappings:
                    Mapping.delete(mapping.model, mapping.key)

                return res

        return super(SqlBase, cls).execute_sql_statement(
            statement, *args, **kwargs
        )

    def delete(self, *args, **kwargs):
        """Inherit the Model.delete methods.::

            instance.delete(remove_mapping=True)

        :param remove_mapping: boolean, if check (default) the mapping is
            removed
        """
        remove_mapping = kwargs.pop("remove_mapping", True)
        if remove_mapping:
            Mapping = self.anyblok.IO.Mapping
            mapping = Mapping.get_from_model_and_primary_keys(
                self.__registry_name__, self.to_primary_keys()
            )

            res = super(SqlBase, self).delete(*args, **kwargs)
            if mapping:
                Mapping.delete(mapping.model, mapping.key)

            return res

        return super(SqlBase, self).delete(*args, **kwargs)
