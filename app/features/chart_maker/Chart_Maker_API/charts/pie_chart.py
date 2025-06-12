from .base_chart import BaseChart
import plotly.graph_objects as go
from typing import List
from app.features.chart_maker.Chart_Maker_API.app.schemas import Trace  # Make sure this is your Trace model with x_column, y_column, name

class PieChart(BaseChart):
    def __init__(self, config):
        super().__init__(config)

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        fig = go.Figure()
        style = getattr(self.config.style, "pie", None)
        if style is None:
            style = type('style', (), {
                'colors': None,
                'opacity': 1.0,
                'hole': 0,
                'textposition': 'inside',
                'textinfo': 'label+percent',
                'textfont_size': 12,
                'textfont_color': '#000000',
                'rotation': 0,
                'pull': None,
                'sort': True
            })()

        # Use the first trace for pie chart
        if not traces or not data:
            return fig
        trace = traces[0]

        # Extract labels and values from data
        labels = [row[trace.x_column] for row in data]
        values = [row[trace.y_column] for row in data]

        # Fallback for missing or empty labels
        if not labels or all(label is None for label in labels):
            labels = [f"Item {i+1}" for i in range(len(values))]

        # Ensure pull is a list of appropriate length
        pull = style.pull if style.pull and len(style.pull) == len(values) else [0] * len(values)

        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            name=trace.name or "Pie",
            marker=dict(
                colors=style.colors,
                line=dict(color='#ffffff', width=1)
            ),
            opacity=style.opacity,
            hole=style.hole,
            textposition=style.textposition,
            textinfo=style.textinfo,
            textfont=dict(
                size=style.textfont_size,
                color=style.textfont_color
            ),
            rotation=style.rotation,
            pull=pull,
            sort=style.sort
        ))

        # Apply common layout (title, legend)
        fig = self.apply_common_layout(fig)
        return fig
