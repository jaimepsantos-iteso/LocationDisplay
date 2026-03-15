"""Shared schema and constants for parsing and visualization."""

EXPECTED_METRICS = [
    "latitude",
    "longitude",
    "altitude",
    "speed",
    "heading",
    "satellites",
    "hdop",
    "fix_mode",
    "gnss_time_raw",
]

LATITUDE_KEYS = ("latitude", "lat")
LONGITUDE_KEYS = ("longitude", "lon", "lng")

REQUIRED_MAP_KEYS = ("latitude", "longitude")
