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
    if track.empty:
        return None

    last_row = track.iloc[-1]
    center_lat = float(last_row[lat_col])
    center_lon = float(last_row[lon_col])

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
            lat=[center_lat],
            lon=[center_lon],
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

    fig.update_layout(
        mapbox={
            "style": "open-street-map",
            "zoom": 15,
            "center": {"lat": center_lat, "lon": center_lon},
        },
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        legend={"orientation": "h", "y": 1.02, "x": 0},
        height=420,
    )
    return fig
