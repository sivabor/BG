from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class AppConfig:
    """Central configuration for calculations and visual thresholds."""

    calculation_date: date = date.today()
    low_available_limit_threshold: float = 0.10
    warning_available_limit_threshold: float = 0.20
    expires_soon_days: int = 30
    default_total_limit: float = 0.0
    default_reserved_limit: float = 0.0


CONFIG = AppConfig()
