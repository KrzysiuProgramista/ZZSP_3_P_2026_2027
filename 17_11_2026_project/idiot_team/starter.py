"""CityPulse Challenge — starter code.

Work in a notebook or complete the functions below. Keep the original CSV files unchanged.
"""
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def load_data(data_dir=DATA_DIR):
    """Load the four source datasets and parse timestamp columns."""
    traffic = pd.read_csv(data_dir / "traffic.csv", parse_dates=["timestamp"])
    sensors = pd.read_csv(data_dir / "sensors.csv")
    weather = pd.read_csv(data_dir / "weather.csv", parse_dates=["timestamp"])
    incidents = pd.read_csv(data_dir / "incidents.csv", parse_dates=["timestamp"])
    return traffic, sensors, weather, incidents


def integrate_data(traffic, sensors, weather, incidents):
    """Return an integrated traffic table and a dictionary of merge reports.

    TODO:
    - Print/store row counts before and after every merge.
    - Use validate= to protect expected key relationships.
    - Keep traffic rows with left joins.
    - Add an indicator for weather and incident matches.
    - Do not hide unknown sensor IDs in the incidents table.
    """
    raise NotImplementedError


def traffic_hotspots(integrated):
    """Return tidy DataFrames with district and road rankings. TODO."""
    raise NotImplementedError


def time_series_report(integrated):
    """Return daily and hourly trends, rolling averages and period changes. TODO."""
    raise NotImplementedError


def investigate_mystery(integrated):
    """Compare 12 Nov 2026 with a fair baseline; check roads, weather and incidents. TODO."""
    raise NotImplementedError


def city_dashboard(traffic, sensors, weather, incidents):
    """Return a dict of tidy DataFrames for the final briefing. TODO."""
    raise NotImplementedError


if __name__ == "__main__":
    frames = load_data()
    print("Loaded row counts:", [len(frame) for frame in frames])
    print("Complete the TODOs, then build your CityPulse investigation.")
