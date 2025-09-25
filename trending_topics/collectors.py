"""Collectors that fetch hot topics from different providers."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

from .models import TrendingTopic

_LOGGER = logging.getLogger(__name__)


_TRAFFIC_UNIT_MAP = {
    "万": 10_000,
    "亿": 100_000_000,
}


def _parse_hot_value(raw_value: str) -> int:
    """Convert Baidu's hot index text into an integer.

    Baidu typically formats its hot index using Chinese units such as ``万``
    (ten thousand) and ``亿`` (hundred million). The function also copes with
    plain integer strings.
    """

    if not raw_value:
        return 0

    raw_value = raw_value.strip()

    # Extract numeric part (possibly containing decimal points).
    match = re.search(r"[\d.]+", raw_value)
    if not match:
        return 0

    number = float(match.group())
    unit = raw_value.replace(match.group(), "").strip()
    multiplier = _TRAFFIC_UNIT_MAP.get(unit, 1)
    traffic = int(number * multiplier)
    return max(traffic, 0)


@dataclass
class BaiduHotSearchCollector:
    """Collect trending topics from Baidu's realtime hot list."""

    session: Optional[requests.Session] = None
    timeout: float = 10.0

    URL: str = "https://top.baidu.com/board?tab=realtime"
    SOURCE: str = "baidu_realtime_hot"

    def _get_session(self) -> requests.Session:
        return self.session or requests.Session()

    def fetch(self, *, limit: Optional[int] = None) -> List[TrendingTopic]:
        """Fetch realtime hot topics from Baidu.

        Parameters
        ----------
        limit:
            Optional maximum number of topics to return. If ``None`` all
            available topics are returned.
        """

        session = self._get_session()
        response = session.get(self.URL, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        items: Iterable[Tag] = soup.select("div.category-wrap_iQLoo")

        topics: List[TrendingTopic] = []
        for idx, item in enumerate(items, start=1):
            title_el = item.select_one("div.c-single-text-ellipsis")
            if title_el is None:
                _LOGGER.debug("Skipping topic %s without a title", idx)
                continue

            hot_el = item.select_one("div.hot-index_1Bl1a")
            description_el = item.select_one("div.hot-desc_1m_jR")
            link_el = item.select_one("a.title_dIF3B")

            title = title_el.get_text(strip=True)
            traffic = _parse_hot_value(hot_el.get_text(strip=True)) if hot_el else 0
            description = description_el.get_text(strip=True) if description_el else None
            if description:
                description = re.sub(r"查看(更多|全部)>?", "", description).strip()
            url = link_el["href"] if link_el and link_el.has_attr("href") else None

            topics.append(
                TrendingTopic(
                    title=title,
                    url=url,
                    source=self.SOURCE,
                    traffic=traffic,
                    description=description,
                )
            )

            if limit is not None and len(topics) >= limit:
                break

        return topics


__all__ = ["BaiduHotSearchCollector"]
