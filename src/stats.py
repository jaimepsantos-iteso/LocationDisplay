"""Statistics helpers for the log viewer."""

from __future__ import annotations

from typing import Dict

import pandas as pd


def compute_dataset_stats(long_df: pd.DataFrame, wide_df: pd.DataFrame) -> Dict[str, object]:
    """Return global dataset stats used in the left panel."""
    if long_df.empty:
        return {
            "records": 0,
            "metrics": 0,
            "start": None,
            "end": None,
            "duration_s": 0.0,
        }

    start = long_df["timestamp"].min()
    end = long_df["timestamp"].max()
    duration_s = (end - start).total_seconds() if pd.notna(start) and pd.notna(end) else 0.0

    return {
        "records": int(len(long_df)),
        "metrics": int(long_df["metric"].nunique()),
        "start": start,
        "end": end,
        "duration_s": float(duration_s),
        "points": int(len(wide_df)),
    }


def compute_metric_table(long_df: pd.DataFrame) -> pd.DataFrame:
    """Return per-metric summary stats for numeric values."""
    if long_df.empty:
        return pd.DataFrame(columns=["metric", "count", "min", "max", "mean", "last"])

    numeric = long_df.dropna(subset=["value_num"])
    if numeric.empty:
        return pd.DataFrame(columns=["metric", "count", "min", "max", "mean", "last"])

    grouped = numeric.groupby("metric", as_index=False)["value_num"]
    summary = grouped.agg(count="count", min="min", max="max", mean="mean")

    last_values = (
        numeric.sort_values("timestamp")
        .groupby("metric", as_index=False)
        .tail(1)[["metric", "value_num"]]
        .rename(columns={"value_num": "last"})
    )

    result = summary.merge(last_values, on="metric", how="left")
    return result.sort_values("metric").reset_index(drop=True)
