import pandas as pd

from src.map_view import build_track_map_figure


def test_map_latest_marker_uses_last_point_not_view_center():
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

    latest_trace = fig.data[1]
    assert latest_trace.name == "Latest"
    assert abs(float(latest_trace.lat[0]) - 21.0) < 1e-9
    assert abs(float(latest_trace.lon[0]) + 104.0) < 1e-9


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