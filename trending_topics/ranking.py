"""Ranking helpers for trending topics."""

from __future__ import annotations

from typing import Iterable, List

from .models import TrendingTopic


def rank_topics(topics: Iterable[TrendingTopic], *, descending: bool = True) -> List[TrendingTopic]:
    """Return topics sorted by their traffic score.

    Parameters
    ----------
    topics:
        An iterable of :class:`~trending_topics.models.TrendingTopic` instances.
    descending:
        Whether to sort in descending order of traffic (default). If ``False``
        the topics are sorted from least to most popular.
    """

    return sorted(topics, key=lambda topic: topic.traffic, reverse=descending)
