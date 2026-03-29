from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, NamedTuple

import pymssql

from db_sync.config import SyncConfig

# Allow connections to SQL Servers with older TLS versions
_OPENSSL_CONF = Path(__file__).resolve().parent.parent.parent / "openssl.cnf"
if _OPENSSL_CONF.exists() and "OPENSSL_CONF" not in os.environ:
    os.environ["OPENSSL_CONF"] = str(_OPENSSL_CONF)

logger = logging.getLogger(__name__)


class Column(NamedTuple):
    name: str
    type_code: type


class SqlServerReader:
    """Reads data from SQL Server using pymssql."""

    def __init__(self, config: SyncConfig) -> None:
        self._config = config
        self._conn: pymssql.Connection | None = None

    def connect(self) -> None:
        logger.info("Connecting to SQL Server...")
        self._conn = pymssql.connect(
            server=self._config.sqlserver_host,
            user=self._config.sqlserver_user,
            password=self._config.sqlserver_password,
            database=self._config.sqlserver_database,
            login_timeout=30,
            tds_version="7.3",
            conn_properties="",
            encryption="off",
        )
        logger.info("Connected to SQL Server.")

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("SQL Server connection closed.")

    def read_table(self, query: str) -> tuple[list[Column], list[tuple[Any, ...]]]:
        """Execute a query and return (columns, rows).

        The columns list contains Column namedtuples with name and type_code
        extracted from cursor.description.
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        cursor = self._conn.cursor()
        cursor.execute(query)

        columns = [
            Column(name=desc[0], type_code=desc[1])
            for desc in cursor.description
        ]
        rows = cursor.fetchall()
        cursor.close()

        return columns, rows

    def __enter__(self) -> SqlServerReader:
        self.connect()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
