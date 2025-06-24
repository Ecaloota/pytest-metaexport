from collections import defaultdict
from datetime import datetime
from typing import Any

import pytest

from pytest_metaexport.report import generate_report
from pytest_metaexport.schema import TestRun
from pytest_metaexport.utils import (
    append_run_to_cache,
)

test_metadata: dict[Any, Any] = defaultdict(dict)
test_state: dict[str, int] = {"passed": 0, "failed": 0, "skipped": 0}
tagged_tests: dict[str, list[str]] = defaultdict(list)


def is_collection_only(session: "pytest.Session", exitstatus: int) -> bool:
    """
    Check if pytest is running in collection-only mode.
    """
    # check if pytest is running in collection-only mode
    collect_flags = ["collectonly", "collect_only", "co", "dry_run"]
    for option in collect_flags:
        if getattr(session.config.option, option, False):
            return True

    # skip generation if tests were collected but not run
    if getattr(session, "testscollected", 0) > 0 and test_state["failed"] == 0:
        return True

    # skip generation if certain exit status indicate collection-only mode
    collection_exit_codes = [5]
    if exitstatus in collection_exit_codes:
        return True

    return False


def pytest_addoption(parser):
    parser.addoption(
        "--metaexport-pdf",
        action="store",
        help="Path to output PDF metadata report",
        default="metaexport_report.pdf",
    )


def pytest_sessionstart(session):
    session._test_suite_start_time = datetime.now()


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        meta = {}
        # Support function-level decorators
        if hasattr(item.function, "_custom_meta"):
            meta.update(item.function._custom_meta)

        test_metadata[item.nodeid].update(meta)
        test_metadata[item.nodeid]["nodeid"] = item.nodeid
        test_metadata[item.nodeid].setdefault("title", item.name)


def pytest_runtest_logreport(report):
    if report.when == "call":
        test_metadata[report.nodeid]["status"] = report.outcome.capitalize()
        test_metadata[report.nodeid]["duration"] = report.duration
        test_state[report.outcome] += 1
    elif report.when == "setup" and report.outcome == "skipped":
        test_metadata[report.nodeid]["status"] = report.outcome.capitalize()
        test_metadata[report.nodeid]["duration"] = 0
        test_state[report.outcome] += 1


def pytest_sessionfinish(session, exitstatus):
    """Hook that runs at the end of the test session"""

    if is_collection_only(session, exitstatus):
        return

    # outpath = session.config.getoption("--metaexport-json")
    total_collected = getattr(session, "testscollected", 0)

    run = TestRun(
        run_date=datetime.now().isoformat(),
        duration_seconds=(
            datetime.now() - session._test_suite_start_time
        ).total_seconds(),
        collected=total_collected,
        passed=test_state["passed"],
        skipped=test_state["skipped"],
        failed=test_state["failed"],
        tests=list(test_metadata.values()),
    )

    append_run_to_cache(run)
    generate_report(test_state, session.config.getoption("--metaexport-pdf"))
