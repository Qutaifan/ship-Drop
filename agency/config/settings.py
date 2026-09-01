"""Centralized Configuration Settings for Project: Dropship | Framework: Hermes."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    # Storage & Database
    ROOT_DIR: Path = ROOT
    DATA_DIR: Path = ROOT / "data"
    DATABASE_PATH: Path = ROOT / "data" / "dropship.db"
    SCHEMAS_DIR: Path = ROOT / "schemas"

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
