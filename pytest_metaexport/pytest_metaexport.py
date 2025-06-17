import datetime
import json
from collections import defaultdict
from typing import Any

test_metadata: dict[Any, Any] = defaultdict(dict)
test_state: dict[str, int] = {"passed": 0, "failed": 0, "skipped": 0}


def pytest_addoption(parser):
    parser.addoption(
        "--metaexport-json",
        action="store",
        help="Path to output JSON metadata report",
    )


def pytest_sessionstart(session):
    session._test_suite_start_time = datetime.datetime.now()


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
        test_metadata[report.nodeid]["status"] = report.outcome
        test_metadata[report.nodeid]["duration"] = report.duration
        test_state[report.outcome] += 1
    elif report.when == "setup" and report.outcome == "skipped":
        test_metadata[report.nodeid]["status"] = report.outcome
        test_metadata[report.nodeid]["duration"] = 0
        test_state[report.outcome] += 1


def pytest_sessionfinish(session, exitstatus):
    """Hook that runs at the end of the test session"""

    # check if pytest is running in collection-only mode
    collect_flags = ["collectonly", "collect_only", "co", "dry_run"]
    for option in collect_flags:
        if getattr(session.config.option, option, False):
            return

    # skip generation if tests were collected but not run
    # total_ex = getattr(session, "testsfailed", 0)
    total_collected = getattr(session, "testscollected", 0)
    if total_collected > 0 and test_state["failed"] == 0:
        return

    # skip generation if certain exit status indicate collection-only mode
    collection_exit_codes = [5]
    if exitstatus in collection_exit_codes:
        return

    output = {
        "run_date": datetime.datetime.now().isoformat(),
        "duration_seconds": (
            datetime.datetime.now() - session._test_suite_start_time
        ).total_seconds(),
        "collected": total_collected,
        "passed": test_state["passed"],
        "skipped": test_state["skipped"],
        "failed": test_state["failed"],
        "tests": list(test_metadata.values()),
    }

    # TODO change this to append mode and append to the json
    # if it exists, under some higher key like "runs", so we can
    # track runs over time, and store this info in an auto-generated cache file
    # then, the user only specifies the name of the final PDF output
    outpath = session.config.getoption("--metaexport-json")
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
