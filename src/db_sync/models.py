from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TableSync:
    """Defines a table to synchronize from SQL Server to SQLite.

    Attributes:
        name: Name of the destination table in SQLite.
        query: SQL query to execute against SQL Server. Can include JOINs,
               WHERE clauses, etc. The result columns become the SQLite schema.
    """

    name: str
    query: str
