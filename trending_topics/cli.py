"""Command line interface for the trending topic collector."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Iterable, Sequence

from .collectors import BaiduHotSearchCollector
from .models import TrendingTopic
from .ranking import rank_topics


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch and rank hot topics from Baidu.")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of topics to display (default: 20).",
    )
    parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="Output format (default: table).",
    )
    return parser


def _format_table(topics: Sequence[TrendingTopic]) -> str:
    headers = ["排名", "话题", "热度", "来源", "链接"]
    rows = []
    for index, topic in enumerate(topics, start=1):
        rows.append(
            [
                str(index),
                topic.title,
                str(topic.traffic),
                topic.source,
                topic.url or "",
            ]
        )

    widths = [len(header) for header in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    def format_row(row: Iterable[str]) -> str:
        return " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row))

    lines = [format_row(headers), "-+-".join("-" * width for width in widths)]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    collector = BaiduHotSearchCollector()
    topics = rank_topics(collector.fetch(limit=args.limit))

    if args.format == "json":
        payload = [asdict(topic) for topic in topics]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(_format_table(topics))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
