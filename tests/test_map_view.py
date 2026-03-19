import pandas as pd

from src.map_view import build_track_map_figure


def _trace_by_name(fig, trace_name: str):
    for trace in fig.data:
        if trace.name == trace_name:
            return trace
    raise AssertionError(f"Missing trace: {trace_name}")


def test_map_finish_marker_uses_last_point_not_view_center():
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime([
                "2026-03-15T10:00:00",
                "2026-03-15T10:00:01",
                "2026-03-15T10:00:02",
            ]),
            "latitude": [20.0, 20.5, 21.0],
            "longitude": [-103.0, -103.5, -104.0],
        }
    )

    fig = build_track_map_figure(df)
    assert fig is not None

    finish_trace = _trace_by_name(fig, "Finish")
    assert finish_trace.name == "Finish"
    assert abs(float(finish_trace.lat[0]) - 21.0) < 1e-9
    assert abs(float(finish_trace.lon[0]) + 104.0) < 1e-9


def test_map_start_marker_is_blue_and_uses_first_point():
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime([
                "2026-03-15T10:00:00",
                "2026-03-15T10:00:01",
                "2026-03-15T10:00:02",
            ]),
            "latitude": [20.0, 20.5, 21.0],
            "longitude": [-103.0, -103.5, -104.0],
        }
    )

    fig = build_track_map_figure(df)
    assert fig is not None

    start_trace = _trace_by_name(fig, "Start")
    assert abs(float(start_trace.lat[0]) - 20.0) < 1e-9
    assert abs(float(start_trace.lon[0]) + 103.0) < 1e-9
    assert start_trace.marker["color"] == "blue"


def test_map_default_center_uses_path_extent_midpoint():
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime([
                "2026-03-15T10:00:00",
                "2026-03-15T10:00:01",
            ]),
            "latitude": [10.0, 20.0],
            "longitude": [-120.0, -100.0],
        }
    )

    fig = build_track_map_figure(df)
    assert fig is not None

    center = fig.layout.mapbox.center
    assert abs(float(center["lat"]) - 15.0) < 1e-9
    assert abs(float(center["lon"]) + 110.0) < 1e-9


def test_map_default_zoom_is_slightly_tighter_than_span_zoom():
    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime([
                "2026-03-15T10:00:00",
                "2026-03-15T10:00:01",
            ]),
            "latitude": [20.0, 21.5],
            "longitude": [-103.0, -103.0],
        }
    )

    fig = build_track_map_figure(df)
    assert fig is not None

    # Span is 1.5 deg: base table gives 7, default bias should show at 8.
    assert int(fig.layout.mapbox.zoom) == 8