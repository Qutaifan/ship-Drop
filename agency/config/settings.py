"""Centralized Configuration Settings for Project: Dropship | Framework: Hermes."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]


def _env_path(name: str, default: Path) -> Path:
    """Path override from the environment, falling back to the repo layout.

    Exists so a test run can be pointed at a scratch directory. Without it every
    Store() writes into the working tree, and running the suite dirties tracked
    files — including data/audit/audit_log.jsonl, which is a governance record.
    Unset in normal operation, so production paths are unchanged.
    """
    value = os.getenv(name)
    return Path(value).expanduser().resolve() if value else default


# Module-level so importers resolve the same directories the Settings dataclass
# does; its field defaults are bound once at class-definition time.
DATA_DIR = _env_path("DROPSHIP_DATA_DIR", ROOT / "data")
CONFIG_DIR = ROOT / "config"

# config/ mixes committed configuration (markets/, feature_flags.json) with this
# one file, which is mutable runtime state. It gets its own override so a test run
# can redirect the state without also redirecting the config it needs to read.
WINDOWS_FILE = _env_path("DROPSHIP_WINDOWS_FILE", CONFIG_DIR / "autonomous_windows.json")


@dataclass(frozen=True)
class Settings:
    # Storage & Database
    ROOT_DIR: Path = ROOT
    DATA_DIR: Path = DATA_DIR
    DATABASE_PATH: Path = DATA_DIR / "dropship.db"
    SCHEMAS_DIR: Path = ROOT / "schemas"
    CONFIG_DIR: Path = CONFIG_DIR
    WINDOWS_FILE: Path = WINDOWS_FILE

    # Governance & Execution Limits
    POLICY_LEVEL: str = os.getenv("DROPSHIP_POLICY_LEVEL", "STRICT_FOUNDER_APPROVAL")
    DRY_RUN: bool = os.getenv("DROPSHIP_DRY_RUN", "true").lower() in ("true", "1", "yes")
    MAX_BUDGET: float = float(os.getenv("DROPSHIP_MAX_BUDGET", "350.00"))
    MAX_POSITION_SIZE: float = float(os.getenv("DROPSHIP_MAX_POSITION_SIZE", "500.00"))
    FOUNDER_NAME: str = "Ahmad"

    # External APIs (Optional / Securely referenced from env)
    CJ_API_KEY: Optional[str] = os.getenv("CJ_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    META_ACCESS_TOKEN: Optional[str] = os.getenv("META_ACCESS_TOKEN")

    # Economic & Benchmarking Parameters
    MEDIAN_CPA_USD: float = 12.00
    MEDIAN_CPA_EUR: float = 21.48
    MIN_NET_MARGIN_USD: float = 15.00
    MIN_NET_MARGIN_EUR: float = 15.00
    EU_MIN_PRICE: float = 62.00
    EU_MAX_PRICE: float = 93.00
    US_MIN_PRICE: float = 20.00
    US_MAX_PRICE: float = 99.00
    TARGET_COGS_MULTIPLE: float = 3.00
    MIN_COGS_MULTIPLE: float = 2.00

    def ensure_directories(self) -> None:
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)


_SETTINGS: Optional[Settings] = None


def get_settings() -> Settings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = Settings()
        _SETTINGS.ensure_directories()
    return _SETTINGS
