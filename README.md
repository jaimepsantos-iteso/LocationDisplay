# LocationDisplay

Streamlit app to inspect Teleplot-style device logs in the format:

Live app: https://locationdisplay.streamlit.app/

`HH:MM:SS.mmm >metric:value`

Example:

`11:43:51.902 >latitude:20.706118`

## Features

- Upload and process `.log` or `.txt` files
- OpenStreetMap path view from latitude/longitude
- Left-panel dataset and variable statistics
- Basic time-series charts for selected metrics
- Parser diagnostics for malformed lines

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Streamlit UI composition and flow
- `src/parser.py`: Teleplot-like log parser
- `src/schema.py`: Metric constants and naming
- `src/stats.py`: Summary statistics helpers
- `src/map_view.py`: OpenStreetMap figure helpers
- `src/charts.py`: Time-series chart helpers
- `tests/test_parser.py`: Parser tests
- `data/samples/sample_gnss.log`: Sample input file

## Notes

- Phase 1 supports file upload only.
- Future phases can add serial and MQTT ingestion.
