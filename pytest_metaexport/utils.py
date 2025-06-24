import json
from datetime import datetime

import pandas as pd

from pytest_metaexport import PYTEST_METAEXPORT_CACHE
from pytest_metaexport.schema import MetaExportRun, TestRun
from pytest_metaexport.settings import settings


def extract_duration_by_datetime(runs: MetaExportRun) -> pd.DataFrame:
    """Returns a DataFrame with columns:
    - datetime: the run date and time
    - duration: the duration of the run in seconds
    - timestamp: the run date and time formatted as a string"""

    duration_by_datetime = {
        datetime.fromisoformat(run.run_date): run.duration_seconds
        for run in runs.runs
        if run.run_date
    }

    df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(list(duration_by_datetime.keys())),
            "duration": list(duration_by_datetime.values()),
        }
    )

    df["timestamp"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.sort_values("datetime")

    return df


def extract_status_by_datetime(runs: MetaExportRun) -> pd.DataFrame:
    """Returns a DataFrame with columns:
    - datetime: the run date and time
    - status: the test status (Passed, Failed, Skipped)
    - count: the number of tests with that status for that run"""

    df = pd.DataFrame(
        [
            {
                "datetime": pd.to_datetime(datetime.fromisoformat(run.run_date)),
                "status": status,
                "count": getattr(run, status.lower(), 0),
            }
            for run in runs.runs
            if run.run_date
            for status in ["Passed", "Failed", "Skipped"]
        ]
    )

    df["timestamp"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.sort_values("datetime")
    return df


def append_run_to_cache(run: TestRun) -> None:
    """Appends a TestRun to the cache."""

    runs = try_load()
    runs.runs.append(run)

    while len(runs.runs) > settings.max_cache_size:
        runs.runs.pop(0)

    with open(PYTEST_METAEXPORT_CACHE, "w") as f:
        data = runs.model_dump_json(indent=2)
        f.write(data)


def try_load() -> MetaExportRun:
    """Load the cache file, assuming it exists."""

    with open(PYTEST_METAEXPORT_CACHE, "r") as f:
        data = json.load(f)

    return MetaExportRun.model_validate(data)
