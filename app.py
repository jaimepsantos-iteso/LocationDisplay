from __future__ import annotations

import streamlit as st

from src.charts import build_time_series_figure
from src.map_view import build_track_map_figure
from src.parser import parse_log_text
from src.schema import EXPECTED_METRICS
from src.stats import compute_dataset_stats, compute_metric_table


st.set_page_config(page_title="LocationDisplay", layout="wide")
st.title("LocationDisplay")
st.caption("Upload Teleplot-like logs and inspect map + metrics.")

uploaded_file = st.file_uploader("Choose a log file", type=["log", "txt"])

if uploaded_file is None:
    st.info("Upload a `.log` or `.txt` file to begin.")
    with st.expander("Expected line format"):
        st.code("11:43:51.902 >latitude:20.706118")
    st.stop()

raw_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
result = parse_log_text(raw_text)

left_col, right_col = st.columns([1, 3], gap="large")

with left_col:
    st.subheader("Dataset Stats")
    dataset_stats = compute_dataset_stats(result.long_df, result.wide_df)
    st.metric("Parsed records", dataset_stats["records"])
    st.metric("Unique metrics", dataset_stats["metrics"])
    st.metric("Wide points", dataset_stats.get("points", 0))
    st.metric("Duration (s)", f"{dataset_stats['duration_s']:.3f}")

    if dataset_stats["start"] is not None and dataset_stats["end"] is not None:
        st.caption(f"Start: {dataset_stats['start']}")
        st.caption(f"End: {dataset_stats['end']}")

    st.subheader("Parser Diagnostics")
    st.write(f"Total lines: {result.total_lines}")
    st.write(f"Parsed lines: {result.parsed_lines}")
    st.write(f"Invalid lines: {len(result.invalid_lines)}")
    if result.invalid_lines:
        st.caption(f"Invalid line numbers (first 20): {result.invalid_lines[:20]}")

    st.subheader("Metric Statistics")
    metric_table = compute_metric_table(result.long_df)
    if metric_table.empty:
        st.warning("No numeric metrics found.")
    else:
        st.dataframe(metric_table, use_container_width=True, hide_index=True)

with right_col:
    st.subheader("OpenStreetMap Track")
    map_figure = build_track_map_figure(result.wide_df)
    if map_figure is None:
        st.warning("No valid latitude/longitude data found for map rendering.")
    else:
        st.plotly_chart(map_figure, use_container_width=True)

    st.subheader("Time-Series")
    available_metrics = [
        col for col in result.wide_df.columns if col != "timestamp" and result.wide_df[col].notna().any()
    ]
    default_metrics = [metric for metric in EXPECTED_METRICS if metric in available_metrics][:3]
    selected_metrics = st.multiselect(
        "Metrics to plot",
        options=available_metrics,
        default=default_metrics,
    )

    if selected_metrics:
        ts_figure = build_time_series_figure(result.wide_df, selected_metrics)
        if ts_figure is None:
            st.warning("Selected metrics do not have plottable points.")
        else:
            st.plotly_chart(ts_figure, use_container_width=True)
    else:
        st.info("Select one or more metrics to draw charts.")
