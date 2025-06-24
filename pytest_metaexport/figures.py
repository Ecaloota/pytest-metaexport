import os

import pandas as pd
import plotly.express as px  # type: ignore[import-untyped]
import plotly.graph_objects as go  # type: ignore[import-untyped]

from pytest_metaexport.settings import settings

LABELS = ["Passed", "Failed", "Skipped"]
COLOURMAP = {"Passed": "#008000", "Failed": "#FF0000", "Skipped": "#DAA520"}

DONUT_PATH = os.path.join(settings.cache_dir, "donut.png")
DURATION_PATH = os.path.join(settings.cache_dir, "duration.png")
STACKED_PATH = os.path.join(settings.cache_dir, "stacked.png")
HORIZ_PATH = os.path.join(settings.cache_dir, "horizontal.png")


def plot_test_summary_donut(
    passed: int,
    failed: int,
    skipped: int,
) -> None:
    """Create a Donut chart with LABELS categories coloured by COLORMAP using plotly.
    Writes the chart to the path specified by output_path."""

    fig = go.Figure(
        data=[
            go.Pie(
                labels=LABELS,
                values=[passed, failed, skipped],
                hole=0.3,
                marker=dict(colors=list(COLOURMAP.values())),
                sort=False,
                textinfo="label+value",
                textfont=dict(size=18),
            )
        ]
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            font=dict(size=20),
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(t=40, b=0, l=0, r=0),
    )
    fig.write_image(DONUT_PATH, width=800, height=500)


def plot_duration_bar_chart(df: pd.DataFrame) -> None:
    """Create a bar chart with datetimes on the X-axis and duration of test suite run
    on the Y-axis. Writes the chart to the path specified by output_path."""

    fig = px.bar(
        df,
        x="timestamp",
        y="duration",
        labels={"timestamp": "Run Time", "duration": "Duration (s)"},
    )

    fig.update_layout(
        xaxis_type="category", xaxis_tickangle=45, margin=dict(t=40, b=80, l=40, r=40)
    )

    fig.write_image(DURATION_PATH, width=800, height=500)


def plot_status_stacked_bar_chart(df: pd.DataFrame) -> None:
    """Create a stacked bar chart with datetimes on the X-axis and counts of test statuses"""

    # Plot stacked bar chart
    fig = px.bar(
        df,
        x="timestamp",
        y="count",
        color="status",
        color_discrete_map=COLOURMAP,
        labels={"timestamp": "Run Time", "count": "Number of Tests"},
    )

    fig.update_layout(
        barmode="stack",
        xaxis_type="category",
        xaxis_tickangle=45,
        margin=dict(t=40, b=80, l=40, r=40),
    )

    fig.write_image(STACKED_PATH)


def plot_stacked_horizontal(
    status_counts: dict[str, int], tag: str | None = None
) -> None:
    # Create stacked bar traces
    traces = []
    for status, count in status_counts.items():
        traces.append(
            go.Bar(
                y=[""],
                x=[count],
                name=status,
                orientation="h",
                marker_color=COLOURMAP.get(status, None),
                text=[count],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(size=32),
            )
        )

    # Create figure
    fig = go.Figure(data=traces)

    # Update layout
    fig.update_layout(
        # title=dict(
        #     text=f"Test Status Counts for {tag}" if tag else "Test Status Counts",
        #     x=0.5,
        #     xanchor="center",
        #     font=dict(size=24),
        # ),
        barmode="stack",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, visible=False),
        showlegend=True,
        legend=dict(yanchor="bottom", y=0.35),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=0, b=0),
    )

    figure_name = HORIZ_PATH.replace(".png", f"_{tag}.png") if tag else HORIZ_PATH
    fig.write_image(figure_name, width=800, height=250)
