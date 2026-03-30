from __future__ import annotations

import logging
import sys

from db_sync.config import SyncConfig
from db_sync.runtime_paths import app_base_dir
from db_sync.sync import SyncOrchestrator
from db_sync.tables import TABLES


def main() -> None:
    log_dir = app_base_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "log.txt"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, mode="w", encoding="utf-8"),
        ],
    )
    logger = logging.getLogger("db_sync")

    try:
        config = SyncConfig.from_env()
    except ValueError as e:
        logger.critical("Configuration error: %s", e)
        sys.exit(1)

    logger.info("Starting sync for client '%s'...", config.client_code)
    orchestrator = SyncOrchestrator(config)

    try:
        orchestrator.run(TABLES)
    except Exception:
        logger.critical("Sync failed with unexpected error.", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
