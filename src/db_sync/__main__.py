from __future__ import annotations

import logging
import sys
from urllib import error, request

from db_sync.config import SyncConfig
from db_sync.runtime_paths import app_base_dir
from db_sync.sync import SyncOrchestrator
from db_sync.tables import TABLES


def get_public_ip(timeout: float = 3.0) -> str | None:
    providers = (
        "https://api.ipify.org",
        "https://checkip.amazonaws.com/",
    )

    for provider in providers:
        try:
            with request.urlopen(provider, timeout=timeout) as response:
                ip_address = response.read().decode("utf-8").strip()
                if ip_address:
                    return ip_address
        except (error.URLError, TimeoutError, ValueError):
            continue

    return None


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

    public_ip = get_public_ip()
    if public_ip:
        logger.info("Public IP detected for this process: %s", public_ip)
    else:
        logger.warning("Could not determine the public IP for this process.")

    logger.info("Starting sync for client '%s'...", config.client_code)
    orchestrator = SyncOrchestrator(config)

    try:
        orchestrator.run(TABLES)
    except Exception:
        logger.critical("Sync failed with unexpected error.", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
