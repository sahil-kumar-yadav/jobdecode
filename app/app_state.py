from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any


@dataclass
class StatsCache:
    payload: dict[str, Any] | None = None
    version: int = 0


cache = StatsCache()
lock = Lock()

