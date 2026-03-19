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

LATITUDE_KEYS = ("latitude", "lat", "GNSS_Latitude")
LONGITUDE_KEYS = ("longitude", "lon", "lng", "GNSS_Longitude")

REQUIRED_MAP_KEYS = ("latitude", "longitude")
