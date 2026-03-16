from __future__ import annotations

import pandas as pd
import streamlit as st

from src.charts import build_time_series_figure
from src.map_view import build_track_map_figure
from src.parser import parse_log_text
from src.schema import EXPECTED_METRICS
from src.stats import compute_dataset_stats, compute_metric_table


st.set_page_config(page_title="Location Display", page_icon="📍", layout="wide")
st.title("📍 Location Display")
st.caption("Upload Teleplot-like logs and inspect map + metrics.")

uploaded_file = st.file_uploader("Choose a log file", type=["log", "txt"])

if uploaded_file is None:
    st.info("Upload a `.log` or `.txt` file to begin.")
    with st.expander("Expected line format"):
        st.code("11:43:51.902 >latitude:20.706118")
    st.stop()

raw_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
result = parse_log_text(raw_text, source_filename=uploaded_file.name)

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
        st.dataframe(metric_table, width="stretch", hide_index=True)

with right_col:
    # Resolve any previously selected time-series point so the map can show it.
    highlight_ts = None
    chart_state_keys = [
        key
        for key in st.session_state.keys()
        if key == "ts_chart_combined" or key.startswith("ts_chart_")
    ]
    for state_key in chart_state_keys:
        ts_state = st.session_state.get(state_key)
        if ts_state is None:
            continue
        pts = getattr(getattr(ts_state, "selection", None), "points", None) or []
        if not pts:
            continue
        raw_x = pts[0].get("x")
        if not raw_x:
            continue
        try:
            highlight_ts = pd.Timestamp(raw_x)
            break
        except Exception:
            continue

    st.subheader("OpenStreetMap Track")
    map_figure = build_track_map_figure(result.wide_df, highlight_ts=highlight_ts)
    if map_figure is None:
        st.warning("No valid latitude/longitude data found for map rendering.")
    else:
        st.plotly_chart(map_figure, width="stretch")

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
    combine_metrics = st.checkbox(
        "Show all selected metrics in one chart",
        value=True,
    )

    if selected_metrics:
        if combine_metrics:
            ts_figure = build_time_series_figure(result.wide_df, selected_metrics)
            if ts_figure is None:
                st.warning("Selected metrics do not have plottable points.")
            else:
                st.plotly_chart(
                    ts_figure,
                    width="stretch",
                    on_select="rerun",
                    key="ts_chart_combined",
                )
        else:
            for metric in selected_metrics:
                metric_figure = build_time_series_figure(result.wide_df, [metric])
                if metric_figure is None:
                    continue
                metric_figure.update_layout(yaxis_title=metric, title=metric)
                st.plotly_chart(
                    metric_figure,
                    width="stretch",
                    on_select="rerun",
                    key=f"ts_chart_{metric}",
                )
    else:
        st.info("Select one or more metrics to draw charts.")
