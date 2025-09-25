"""Utilities for collecting and ranking trending topics from the web."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models import TrendingTopic
from .ranking import rank_topics

__all__ = ["TrendingTopic", "rank_topics", "HotTopicsApp", "run"]

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .app import HotTopicsApp, run


def __getattr__(name: str) -> Any:  # pragma: no cover - import hook
    if name in {"HotTopicsApp", "run"}:
        from .app import HotTopicsApp, run  # type: ignore

        globals()["HotTopicsApp"] = HotTopicsApp
        globals()["run"] = run
        return globals()[name]
    raise AttributeError(f"module 'trending_topics' has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover - trivial
    return sorted(__all__)
