from .base_chart import BaseChart
import plotly.graph_objects as go
from typing import List
from app.features.chart_maker.Chart_Maker_API.app.schemas import Trace  # Use Trace, not Dataset, for new workflow

class BarChart(BaseChart):
    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        """
        Generate a bar chart from a list of traces and CSV data.
        traces: List of Trace objects (with x_column, y_column, name)
        data: List of dicts (from CSV)
        """
        fig = go.Figure()

        # Get bar style config, default to empty if not present
        style = getattr(getattr(self.config, 'style', {}), 'bar', None)
        if style is None:
            style = type('style', (), {
                'color': ["#1f77b4"],
                'opacity': [0.8],
                'border_color': ["#000000"],
                'border_width': [1],
                'pattern_shape': [None],
                'pattern_fgcolor': [None],
                'pattern_bgcolor': [None],
                'orientation': 'v',
                'width': None,
                'textposition': 'auto',
                'texttemplate': None,
                'insidetextanchor': None,
                'textfont_size': 12,
                'textfont_color': '#000000',
                'barmode': 'group',
                'bargap': 0.2,
                'bargroupgap': 0.1
            })()

        for idx, trace in enumerate(traces):
            x = [row[trace.x_column] for row in data]
            y = [row[trace.y_column] for row in data]

            # Get style with index wrapping
            color = style.color[idx % len(style.color)] if hasattr(style, 'color') else "#1f77b4"
            opacity = style.opacity[idx % len(style.opacity)] if hasattr(style, 'opacity') else 0.8
            border_color = style.border_color[idx % len(style.border_color)] if hasattr(style, 'border_color') else "#000000"
            border_width = style.border_width[idx % len(style.border_width)] if hasattr(style, 'border_width') else 1
            pattern_shape = style.pattern_shape[idx % len(style.pattern_shape)] if hasattr(style, 'pattern_shape') else None
            pattern_fgcolor = style.pattern_fgcolor[idx % len(style.pattern_fgcolor)] if hasattr(style, 'pattern_fgcolor') else None
            pattern_bgcolor = style.pattern_bgcolor[idx % len(style.pattern_bgcolor)] if hasattr(style, 'pattern_bgcolor') else None

            # Bar trace
            bar = go.Bar(
                x=x if getattr(style, 'orientation', 'v') == 'v' else y,
                y=y if getattr(style, 'orientation', 'v') == 'v' else x,
                name=trace.name or f"Series {idx+1}",
                marker=dict(
                    color=color,
                    opacity=opacity,
                    line=dict(
                        color=border_color,
                        width=border_width
                    ),
                    pattern=dict(
                        shape=pattern_shape,
                        fgcolor=pattern_fgcolor,
                        bgcolor=pattern_bgcolor
                    ) if pattern_shape else None
                ),
                width=getattr(style, 'width', None),
                orientation=getattr(style, 'orientation', 'v'),
                text=y if getattr(style, 'orientation', 'v') == 'v' else x,
                textposition=getattr(style, 'textposition', 'auto'),
                texttemplate=getattr(style, 'texttemplate', None),
                insidetextanchor=getattr(style, 'insidetextanchor', None),
                textfont=dict(
                    size=getattr(style, 'textfont_size', 12),
                    color=getattr(style, 'textfont_color', '#000000')
                )
            )
            fig.add_trace(bar)

        # Apply bar mode and gaps
        fig.update_layout(
            barmode=getattr(style, 'barmode', 'group'),
            bargap=getattr(style, 'bargap', 0.2),
            bargroupgap=getattr(style, 'bargroupgap', 0.1)
        )

        # Apply common layout (title, axes, legend, grid)
        fig = self.apply_common_layout(fig)
        return fig
