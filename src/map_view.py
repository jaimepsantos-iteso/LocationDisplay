"""OpenStreetMap rendering helpers."""

from __future__ import annotations

from typing import Optional, Tuple

import pandas as pd
import plotly.graph_objects as go

from .schema import LATITUDE_KEYS, LONGITUDE_KEYS

_HIGHLIGHT_COLOR = "#4FD346"  # green


def _find_coordinate_columns(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    lat_col = next((key for key in LATITUDE_KEYS if key in df.columns), None)
    lon_col = next((key for key in LONGITUDE_KEYS if key in df.columns), None)

    return lat_col, lon_col


def _normalize_coordinate_series(series: pd.Series, abs_limit: float) -> pd.Series:
    """Normalize E7 coordinates to decimal degrees for out-of-range values."""
    numeric = pd.to_numeric(series, errors="coerce")
    out_of_range = (numeric > abs_limit) | (numeric < -abs_limit)
    numeric.loc[out_of_range] = numeric.loc[out_of_range] / 1e7
    return numeric


def _zoom_for_span(span: float) -> int:
    """Estimate a map zoom level that keeps the whole path in view."""
    if span < 0.0005:
        return 18
    if span < 0.001:
        return 17
    if span < 0.002:
        return 16
    if span < 0.005:
        return 15
    if span < 0.01:
        return 14
    if span < 0.02:
        return 13
    if span < 0.05:
        return 12
    if span < 0.1:
        return 11
    if span < 0.2:
        return 10
    if span < 0.5:
        return 9
    if span < 1:
        return 8
    if span < 2:
        return 7
    if span < 5:
        return 6
    if span < 10:
        return 5
    if span < 20:
        return 4
    if span < 40:
        return 3
    return 2


def build_track_map_figure(
    wide_df: pd.DataFrame,
    highlight_ts: Optional[pd.Timestamp] = None,
) -> Optional[go.Figure]:
    """Build an OpenStreetMap track figure from wide GNSS data.

    If *highlight_ts* is given, the coordinate row nearest to that timestamp
    is marked with a green pin so it can be cross-referenced with the
    time-series chart.
    """
    lat_col, lon_col = _find_coordinate_columns(wide_df)
    if not lat_col or not lon_col:
        return None

    track = wide_df.dropna(subset=[lat_col, lon_col]).copy()
    track[lat_col] = _normalize_coordinate_series(track[lat_col], abs_limit=90)
    track[lon_col] = _normalize_coordinate_series(track[lon_col], abs_limit=180)
    track = track.dropna(subset=[lat_col, lon_col])
    if track.empty:
        return None

    last_row = track.iloc[-1]
    last_lat = float(last_row[lat_col])
    last_lon = float(last_row[lon_col])
    lat_min = float(track[lat_col].min())
    lat_max = float(track[lat_col].max())
    lon_min = float(track[lon_col].min())
    lon_max = float(track[lon_col].max())
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    zoom = _zoom_for_span(max(lat_max - lat_min, lon_max - lon_min))

    fig = go.Figure()
    fig.add_trace(
        go.Scattermapbox(
            lat=track[lat_col],
            lon=track[lon_col],
            mode="lines",
            line={"width": 4},
            name="Path",
        )
    )
    fig.add_trace(
        go.Scattermapbox(
            lat=[last_lat],
            lon=[last_lon],
            mode="markers",
            marker={"size": 12, "color": "red"},
            name="Latest",
        )
    )

    if highlight_ts is not None:
        idx = (track["timestamp"] - highlight_ts).abs().idxmin()
        row = track.loc[idx]
        fig.add_trace(
            go.Scattermapbox(
                lat=[float(row[lat_col])],
                lon=[float(row[lon_col])],
                mode="markers",
                marker={"size": 16, "color": _HIGHLIGHT_COLOR},
                name="Selected",
            )
        )
        center_lat = float(row[lat_col])
        center_lon = float(row[lon_col])
        zoom = 15

    fig.update_layout(
        mapbox={
            "style": "open-street-map",
            "zoom": zoom,
            "center": {"lat": center_lat, "lon": center_lon},
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        legend={"orientation": "h", "y": 1.02, "x": 0},
        height=420,
    )
    return fig
