from typing import Literal

from pydantic import BaseModel, ConfigDict

TestOutcome = Literal["Passed", "Failed", "Skipped"]


class Test(BaseModel):
    model_config = ConfigDict(extra="allow")

    nodeid: str
    title: str
    status: TestOutcome
    duration: float


class TestRun(BaseModel):
    run_date: str
    duration_seconds: float
    collected: int
    passed: int
    skipped: int
    failed: int
    tests: list[Test] = []


class MetaExportRun(BaseModel):
    runs: list[TestRun] = []


class MetaExportReport(BaseModel):
    run_date: str
    total_collected: int
    total_passed: int
    total_failed: int
    total_skipped: int

    summary_pie_chart_path: str
    duration_bar_chart_path: str
    status_line_chart_path: str

    tests: list[Test] = []
    tagged_tests: dict[str, list[Test]] = {}
    tagged_figs: dict[str, str] = {}
