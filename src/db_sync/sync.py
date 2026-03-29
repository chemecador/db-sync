from __future__ import annotations

import logging
import time

from db_sync.config import SyncConfig
from db_sync.models import TableSync
from db_sync.reader import SqlServerReader
from db_sync.writer import SqliteWriter

logger = logging.getLogger(__name__)


class SyncOrchestrator:
    """Orchestrates the synchronization from SQL Server to SQLite."""

    def __init__(self, config: SyncConfig) -> None:
        self._config = config

    def run(self, tables: list[TableSync]) -> None:
        start = time.monotonic()
        config = self._config

        # Ensure output directory exists
        config.sqlite_output_dir.mkdir(parents=True, exist_ok=True)
        output_path = config.sqlite_output_path

        # Remove existing database (fresh sync each time)
        if output_path.exists():
            output_path.unlink()
            logger.info("Removed existing database: %s", output_path)

        with SqlServerReader(config) as reader, SqliteWriter(output_path) as writer:
            total_rows = 0
            for table in tables:
                try:
                    logger.info("Syncing table '%s'...", table.name)
                    columns, rows = reader.read_table(table.query)
                    writer.create_table(table.name, columns)
                    count = writer.insert_rows(table.name, columns, rows)
                    total_rows += count
                except Exception:
                    logger.exception("Failed to sync table '%s'. Skipping.", table.name)

        elapsed = time.monotonic() - start
        logger.info(
            "Sync complete: %d table(s), %d total rows in %.1fs.",
            len(tables), total_rows, elapsed,
        )
