from __future__ import annotations

import logging
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from db_sync.reader import Column

logger = logging.getLogger(__name__)

# Mapping from Python types (pyodbc type_code) to SQLite type affinity
_TYPE_MAP: dict[type, str] = {
    str: "TEXT",
    int: "INTEGER",
    float: "REAL",
    Decimal: "REAL",
    bool: "INTEGER",
    datetime: "TEXT",
    date: "TEXT",
    bytes: "BLOB",
    bytearray: "BLOB",
}


def _sqlite_type(type_code: type) -> str:
    return _TYPE_MAP.get(type_code, "TEXT")


class SqliteWriter:
    """Writes data to a SQLite database, creating tables dynamically."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        logger.info("Opened SQLite database: %s", self._db_path)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("SQLite connection closed.")

    def create_table(self, table_name: str, columns: list[Column]) -> None:
        """Create (or recreate) a table based on the source query columns."""
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        col_defs = ", ".join(
            f'"{col.name}" {_sqlite_type(col.type_code)}' for col in columns
        )
        self._conn.execute(f"DROP TABLE IF EXISTS \"{table_name}\"")
        create_sql = f'CREATE TABLE "{table_name}" ({col_defs})'
        self._conn.execute(create_sql)
        self._conn.commit()
        logger.info("Created table '%s' with %d columns.", table_name, len(columns))

    def insert_rows(
        self, table_name: str, columns: list[Column], rows: list[tuple],
    ) -> int:
        """Insert rows into the table. Returns the number of rows inserted."""
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        if not rows:
            logger.info("No rows to insert into '%s'.", table_name)
            return 0

        col_names = ", ".join(f'"{col.name}"' for col in columns)
        placeholders = ", ".join("?" for _ in columns)
        insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'

        # Convert pyodbc Row objects to plain tuples
        plain_rows = [tuple(row) for row in rows]

        try:
            self._conn.executemany(insert_sql, plain_rows)
            self._conn.commit()
            logger.info("Inserted %d rows into '%s'.", len(plain_rows), table_name)
            return len(plain_rows)
        except sqlite3.Error:
            logger.warning(
                "Batch insert failed for '%s'. Falling back to row-by-row.",
                table_name,
            )
            return self._insert_row_by_row(insert_sql, table_name, plain_rows)

    def _insert_row_by_row(
        self, insert_sql: str, table_name: str, rows: list[tuple],
    ) -> int:
        """Fallback: insert rows one by one, logging errors per row."""
        inserted = 0
        for i, row in enumerate(rows):
            try:
                self._conn.execute(insert_sql, row)
                inserted += 1
            except sqlite3.Error as e:
                logger.error(
                    "Error inserting row %d into '%s': %s", i, table_name, e,
                )
        self._conn.commit()
        logger.info(
            "Row-by-row insert into '%s': %d/%d succeeded.",
            table_name, inserted, len(rows),
        )
        return inserted

    def __enter__(self) -> SqliteWriter:
        self.connect()
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
