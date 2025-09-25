"""Data models used by the trending topic collector."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class TrendingTopic:
    """Represents a trending topic returned by an upstream provider.

    Attributes
    ----------
    title:
        The human readable title of the topic.
    url:
        A canonical URL that points to more information about the topic. Not all
        providers supply URLs. ``None`` denotes that no URL is available.
    source:
        Name of the upstream source, for example ``"google_trends"``.
    traffic:
        A normalised integer that indicates the relative interest for this
        topic. When the upstream source does not publish absolute numbers we
        convert the supplied qualitative labels (e.g. ``"100K+"``) into rough
        integers. Higher values mean higher interest.
    description:
        Optional free form text that describes the topic.
    """

    title: str
    url: Optional[str]
    source: str
    traffic: int
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if self.traffic < 0:
            raise ValueError("traffic must be a non-negative integer")
