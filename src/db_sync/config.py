from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class SyncConfig:
    """Configuration for the database synchronization."""

    sqlserver_host: str
    sqlserver_database: str
    sqlserver_user: str
    sqlserver_password: str
    sqlite_output_dir: Path
    client_code: str

    @property
    def sqlite_output_path(self) -> Path:
        return self.sqlite_output_dir / f"{self.client_code}.db"

    @classmethod
    def from_env(cls, env_path: str | Path | None = None) -> SyncConfig:
        load_dotenv(env_path)

        required = [
            "SQLSERVER_HOST",
            "SQLSERVER_DATABASE",
            "SQLSERVER_USER",
            "SQLSERVER_PASSWORD",
            "SQLITE_OUTPUT_DIR",
            "CLIENT_CODE",
        ]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return cls(
            sqlserver_host=os.environ["SQLSERVER_HOST"],
            sqlserver_database=os.environ["SQLSERVER_DATABASE"],
            sqlserver_user=os.environ["SQLSERVER_USER"],
            sqlserver_password=os.environ["SQLSERVER_PASSWORD"],
            sqlite_output_dir=Path(os.environ["SQLITE_OUTPUT_DIR"]),
            client_code=os.environ["CLIENT_CODE"],
        )
