"""Time-series chart builders."""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd
import plotly.graph_objects as go


def build_time_series_figure(wide_df: pd.DataFrame, metrics: Iterable[str]) -> Optional[go.Figure]:
    """Build a multi-line time-series chart for selected metrics."""
    selected = [metric for metric in metrics if metric in wide_df.columns]
    if not selected or "timestamp" not in wide_df.columns:
        return None

    fig = go.Figure()
    for metric in selected:
        series = wide_df[["timestamp", metric]].dropna(subset=[metric])
        if series.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=series["timestamp"],
                y=series[metric],
                mode="lines",
                name=metric,
            )
        )

    if len(fig.data) == 0:
        return None

    fig.update_layout(
        height=360,
        margin={"l": 0, "r": 0, "t": 20, "b": 0},
        xaxis_title="Time",
        yaxis_title="Value",
    )
    return fig
