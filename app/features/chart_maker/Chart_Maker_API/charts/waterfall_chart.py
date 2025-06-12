from typing import List
import plotly.graph_objects as go
from app.features.chart_maker.Chart_Maker_API.app.schemas import Trace  # Make sure this is your Trace model with x_column, y_column, name
from .base_chart import BaseChart

class WaterfallChart(BaseChart):
    def __init__(self, config):
        super().__init__(config)

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        fig = go.Figure()
        style = getattr(self.config.style, "waterfall", None)
        if style is None:
            style = type('style', (), {
                "measure": None,
                "base": 0,
                "textposition": "auto",
                "connector_line_color": "#444",
                "connector_line_width": 1,
                "increasing_color": "#3D9970",
                "decreasing_color": "#FF4136",
                "total_color": "#0074D9",
                "orientation": "v",
                "textfont_size": 12,
                "textfont_color": "#000000",
                "showlegend": True
            })()

        # Use the first trace for waterfall chart
        if not traces or not data:
            return fig
        trace = traces[0]

        # Extract x and y data from CSV rows
        x_data = [row[trace.x_column] for row in data]
        y_data = [row[trace.y_column] for row in data]
        # Extract text if available (optional)
        text = [row.get("text") for row in data] if "text" in data[0] else None

        # Handle measure, base, and textposition with fallbacks
        measure = style.measure if style.measure and len(style.measure) == len(x_data) else ['relative'] * len(x_data)
        base = style.base if style.base is not None else 0
        textposition = style.textposition if style.textposition else "auto"

        fig.add_trace(go.Waterfall(
            x=x_data,
            y=y_data,
            measure=measure,
            base=base,
            text=text,
            textposition=textposition,
            name=trace.name or "Waterfall",
            connector=dict(
                line=dict(
                    color=style.connector_line_color or "#444",
                    width=style.connector_line_width or 1
                )
            ),
            increasing=dict(marker=dict(color=style.increasing_color or "#3D9970")),
            decreasing=dict(marker=dict(color=style.decreasing_color or "#FF4136")),
            totals=dict(marker=dict(color=style.total_color or "#0074D9")),
            orientation=style.orientation or "v",
            textfont=dict(
                size=style.textfont_size or 12,
                color=style.textfont_color or "#000000"
            ),
            showlegend=style.showlegend if style.showlegend is not None else True
        ))

        # Apply common layout (title, legend, grid, etc.)
        fig = self.apply_common_layout(fig)
        return fig
