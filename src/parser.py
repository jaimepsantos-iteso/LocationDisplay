"""Parsing utilities for Teleplot-like log lines."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import List

import pandas as pd

LINE_PATTERN = re.compile(
    r"^\s*(?P<ts>\d{2}:\d{2}:\d{2}\.\d{3})\s*>\s*(?P<metric>[A-Za-z0-9_]+)\s*:\s*(?P<value>.+?)\s*$"
)


@dataclass
class ParseResult:
    long_df: pd.DataFrame
    wide_df: pd.DataFrame
    total_lines: int
    parsed_lines: int
    invalid_lines: List[int]


def parse_log_text(log_text: str, source_filename: str | None = None) -> ParseResult:
    """Parse log text into long and wide dataframes.

    If *source_filename* contains a date pattern like YYYY-MM-DD or YYYYMMDD,
    that date is used as the day component for parsed timestamps.
    """
    records = []
    invalid_lines: List[int] = []

    lines = log_text.splitlines()
    total_lines = len(lines)

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        match = LINE_PATTERN.match(line)
        if not match:
            invalid_lines.append(line_number)
            continue

        timestamp_text = match.group("ts")
        metric = match.group("metric")
        value_raw = match.group("value").strip()

        value_num = pd.to_numeric(value_raw, errors="coerce")
        records.append(
            {
                "line_number": line_number,
                "timestamp_text": timestamp_text,
                "metric": metric,
                "value_raw": value_raw,
                "value_num": value_num,
            }
        )

    long_df = pd.DataFrame.from_records(records)
    if long_df.empty:
        return ParseResult(
            long_df=pd.DataFrame(
                columns=[
                    "line_number",
                    "timestamp_text",
                    "timestamp",
                    "metric",
                    "value_raw",
                    "value_num",
                ]
            ),
            wide_df=pd.DataFrame(columns=["timestamp"]),
            total_lines=total_lines,
            parsed_lines=0,
            invalid_lines=invalid_lines,
        )

    # Use filename date when available, otherwise fall back to today's date.
    day = None
    date_match = re.search(r"(\d{4})-?(\d{2})-?(\d{2})", source_filename or "")
    if date_match:
        try:
            day = pd.Timestamp(f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}").normalize()
        except Exception:
            pass

    if day is None:
        day = pd.Timestamp.today().normalize()

    long_df["timestamp"] = day + pd.to_timedelta(long_df["timestamp_text"], errors="coerce")

    wide_df = (
        long_df.pivot_table(index="timestamp", columns="metric", values="value_num", aggfunc="last")
        .sort_index()
        .reset_index()
    )
    wide_df.columns.name = None

    return ParseResult(
        long_df=long_df,
        wide_df=wide_df,
        total_lines=total_lines,
        parsed_lines=len(long_df),
        invalid_lines=invalid_lines,
    )
