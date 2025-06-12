from typing import List
import plotly.graph_objects as go
from app.features.chart_maker.Chart_Maker_API.app.schemas import Trace  # Make sure this is your Trace model with x_column, y_column, name
from .base_chart import BaseChart

class ScatterChart(BaseChart):
    def __init__(self, config):
        super().__init__(config)

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        fig = go.Figure()
        style = getattr(self.config.style, "scatter", None)
        if style is None:
            style = type('style', (), {
                'show_line': False,
                'mode': "markers",
                'marker_size': 8,
                'marker_color': "#1f77b4",
                'marker_symbol': "circle",
                'marker_opacity': 1.0,
                'marker_line_color': "#000000",
                'marker_line_width': 0,
                'line_color': "#1f77b4",
                'line_width': 2,
                'line_dash': "solid",
                'textposition': "none",
                'textfont_size': 12,
                'textfont_color': "#000000"
            })()

        for idx, trace in enumerate(traces):
            x_data = [row[trace.x_column] for row in data]
            y_data = [row[trace.y_column] for row in data]
            name = trace.name or f"Series {idx+1}"

            # Determine mode based on show_line and user mode
            show_line = getattr(style, "show_line", False)
            user_mode = getattr(style, "mode", "markers")
            mode = "lines+markers" if show_line and "markers" in user_mode else ("lines" if show_line else "markers")

            # Marker properties with index wrapping for lists
            marker_size = style.marker_size[idx % len(style.marker_size)] if isinstance(getattr(style, "marker_size", None), list) else getattr(style, "marker_size", 8)
            marker_color = style.marker_color[idx % len(style.marker_color)] if isinstance(getattr(style, "marker_color", None), list) else getattr(style, "marker_color", "#1f77b4")
            marker_symbol = style.marker_symbol[idx % len(style.marker_symbol)] if isinstance(getattr(style, "marker_symbol", None), list) else getattr(style, "marker_symbol", "circle")
            marker_opacity = style.marker_opacity[idx % len(style.marker_opacity)] if isinstance(getattr(style, "marker_opacity", None), list) else getattr(style, "marker_opacity", 1.0)
            marker_line_color = style.marker_line_color[idx % len(style.marker_line_color)] if isinstance(getattr(style, "marker_line_color", None), list) else getattr(style, "marker_line_color", "#000000")
            marker_line_width = style.marker_line_width[idx % len(style.marker_line_width)] if isinstance(getattr(style, "marker_line_width", None), list) else getattr(style, "marker_line_width", 0)

            marker = dict(
                size=marker_size,
                color=marker_color,
                symbol=marker_symbol,
                opacity=marker_opacity,
                line=dict(
                    color=marker_line_color,
                    width=marker_line_width
                )
            )

            # Line properties with index wrapping for lists
            line_color = style.line_color[idx % len(style.line_color)] if isinstance(getattr(style, "line_color", None), list) else getattr(style, "line_color", "#1f77b4")
            line_width = style.line_width[idx % len(style.line_width)] if isinstance(getattr(style, "line_width", None), list) else getattr(style, "line_width", 2)
            line_dash = style.line_dash[idx % len(style.line_dash)] if isinstance(getattr(style, "line_dash", None), list) else getattr(style, "line_dash", "solid")

            line = dict(
                color=line_color,
                width=line_width,
                dash=line_dash
            ) if show_line else None

            # Text labels
            textposition = getattr(style, "textposition", "none")
            textfont = dict(
                size=getattr(style, "textfont_size", 12),
                color=getattr(style, "textfont_color", "#000000")
            )

            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode=mode,
                name=name,
                marker=marker,
                line=line,
                text=[row.get("text") for row in data] if "text" in data[0] else None,
                textposition=None if textposition == "none" else textposition,
                textfont=textfont
            ))

        fig = self.apply_common_layout(fig)
        return fig
