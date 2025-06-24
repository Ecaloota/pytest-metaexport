import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, PackageLoader
from weasyprint import HTML  # type: ignore[import-untyped]

from pytest_metaexport.schema import MetaExportReport, MetaExportRun, Test
from pytest_metaexport.settings import settings
from pytest_metaexport.utils import try_load

tagged_tests: dict[str, list[Test]] = defaultdict(list)
tag_figs: dict[str, str] = defaultdict(str)


def runs_to_report(runs: MetaExportRun) -> MetaExportReport:
    """Convert MetaExportRun to MetaExportReport."""
    if not runs.runs:
        raise ValueError("No runs found in MetaExportRun.")

    # Derive summary counts from most recent run (mrr)
    most_recent_key = max([t.run_date for t in runs.runs])
    mrr = [x for x in runs.runs if x.run_date == most_recent_key][0]

    # handle tags organisation
    for test in mrr.tests:
        tags = test.tags if hasattr(test, "tags") else []  # type: ignore[attr-defined]
        if tags:
            for tag in tags:
                tagged_tests[tag].append(test)
                tag_figs[tag] = (
                    Path(os.path.join(settings.cache_dir, f"horizontal_{tag}.png"))
                    .resolve()
                    .as_uri()
                )
        else:
            tagged_tests["Untagged"].append(test)
            tag_figs["Untagged"] = (
                Path(os.path.join(settings.cache_dir, "horizontal_Untagged.png"))
                .resolve()
                .as_uri()
            )

    return MetaExportReport(
        run_date=datetime.now().date().isoformat(),
        total_collected=mrr.collected,
        total_passed=mrr.passed,
        total_failed=mrr.failed,
        total_skipped=mrr.skipped,
        summary_pie_chart_path=Path(os.path.join(settings.cache_dir, "donut.png"))
        .resolve()
        .as_uri(),
        duration_bar_chart_path=Path(os.path.join(settings.cache_dir, "duration.png"))
        .resolve()
        .as_uri(),
        status_line_chart_path=Path(os.path.join(settings.cache_dir, "stacked.png"))
        .resolve()
        .as_uri(),
        tests=[t for t in mrr.tests],
        tagged_tests=tagged_tests,
        tagged_figs=tag_figs,
    )


def report_to_pdf(report: MetaExportReport, loc: str) -> None:
    """Convert MetaExportReport to PDF using WeasyPrint."""

    # Setup Jinja2
    env = Environment(loader=PackageLoader("pytest_metaexport", "static"))
    template = env.get_template(os.path.basename(settings.template_path))

    # Render HTML
    css_path = Path(settings.css_path).resolve().as_uri()
    html_out = template.render(
        **report.model_dump(),
        css_path=css_path,
        project_title=settings.project_title,
    )

    # Write to PDF
    HTML(string=html_out).write_pdf(loc)


def generate_report(test_state: dict[str, int], loc: str) -> None:
    """Generate a report from the cached runs and save it as a PDF."""

    all_runs = try_load()
    report = runs_to_report(all_runs)

    if settings.generate_figures:
        from pytest_metaexport.figures import (
            plot_duration_bar_chart,
            plot_stacked_horizontal,
            plot_status_stacked_bar_chart,
            plot_test_summary_donut,
        )
        from pytest_metaexport.utils import (
            extract_duration_by_datetime,
            extract_status_by_datetime,
        )

        duration_df = extract_duration_by_datetime(all_runs)
        status_df = extract_status_by_datetime(all_runs)

        plot_duration_bar_chart(duration_df)
        plot_status_stacked_bar_chart(status_df)
        plot_test_summary_donut(**test_state)

        for tag in report.tagged_tests:
            status_counts = {
                status: sum(1 for x in report.tagged_tests[tag] if x.status == status)
                for status in ("Passed", "Failed", "Skipped")
            }
            plot_stacked_horizontal(status_counts, tag)

    report_to_pdf(report, loc)
