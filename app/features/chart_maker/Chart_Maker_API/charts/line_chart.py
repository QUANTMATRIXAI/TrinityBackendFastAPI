from .base_chart import BaseChart
import plotly.graph_objects as go
from typing import List
from app.features.chart_maker.Chart_Maker_API.app.schemas import Trace  # <-- This is the Trace model with x_column, y_column, name

class LineChart(BaseChart):
    def __init__(self, config):
        super().__init__(config)
        self.linestyle_map = {
            '-': 'solid',
            '--': 'dash',
            '-.': 'dashdot',
            ':': 'dot'
        }
        self.marker_symbol_map = {
            "o": "circle",
            "s": "square",
            "d": "diamond",
            "^": "triangle-up",
            "v": "triangle-down",
            "<": "triangle-left",
            ">": "triangle-right",
            "x": "x",
            "+": "cross",
            "*": "star",
            "p": "pentagon",
            "h": "hexagon",
        }

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        """
        Generate a line chart from a list of traces and CSV data.
        traces: List of Trace objects (with x_column, y_column, name)
        data: List of dicts (from CSV)
        """
        fig = go.Figure()

        # Get line style config, default to empty if not present
        style = getattr(getattr(self.config, 'style', {}), 'line', None)
        if style is None:
            style = type('style', (), {
                'color': ["#1f77b4"],
                'linewidth': [2],
                'linestyle': ["-"],
                'marker': ["o"],
                'markersize': [8],
                'alpha': [1.0]
            })()

        for idx, trace in enumerate(traces):
            x = [row[trace.x_column] for row in data]
            y = [row[trace.y_column] for row in data]

            # Get style with index wrapping
            line_color = style.color[idx % len(style.color)] if hasattr(style, 'color') else "#1f77b4"
            line_width = style.linewidth[idx % len(style.linewidth)] if hasattr(style, 'linewidth') else 2
            line_dash = self.linestyle_map.get(
                style.linestyle[idx % len(style.linestyle)] if hasattr(style, 'linestyle') else "-",
                "solid"
            )
            marker_symbol = self.marker_symbol_map.get(
                style.marker[idx % len(style.marker)] if hasattr(style, 'marker') else "o",
                "circle"
            )
            marker_size = style.markersize[idx % len(style.markersize)] if hasattr(style, 'markersize') else 8
            opacity = style.alpha[idx % len(style.alpha)] if hasattr(style, 'alpha') else 1.0

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                name=trace.name or f"Series {idx+1}",
                mode="lines",
                line=dict(
                    color=line_color,
                    width=line_width,
                    dash=line_dash
                ),
                marker=dict(
                    symbol=marker_symbol,
                    size=marker_size,
                    opacity=opacity
                )
            ))

        fig = self.apply_common_layout(fig)
        return fig
