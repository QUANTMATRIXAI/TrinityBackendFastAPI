from typing import List
import plotly.graph_objects as go
from app.features.chart_maker.Chart_Maker_API.app.schemas import Dataset, ChartConfig  # Adjust import as needed
from app.features.chart_maker.Chart_Maker_API.charts.base_chart import BaseChart                # Adjust import as needed

class AreaChart(BaseChart):
    def __init__(self, config: ChartConfig):
        super().__init__(config)

    def generate(self, data: List[Dataset]) -> go.Figure:
        fig = go.Figure()
        style = self.config.style.area
        stack_mode = style.stack_mode if style and style.stack_mode else 'none'
        for idx, dataset in enumerate(data):
            x_data = dataset.x if dataset.x else []
            y_data = dataset.y if dataset.y else []

            line_color = style.line_color[idx % len(style.line_color)] if style and style.line_color else '#1f77b4'
            line_width = style.line_width[idx % len(style.line_width)] if style and style.line_width else 2
            line_dash = style.line_dash[idx % len(style.line_dash)] if style and style.line_dash else 'solid'

            fill_opacity = style.fill_opacity if style and style.fill_opacity is not None else 0.5
            fill_pattern = style.fill_pattern if style else None

            marker_show = style.markers_show if style else False
            marker_size = style.markers_size if style else 6

            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines+markers' if marker_show else 'lines',
                name=dataset.name or f'Series {idx+1}',
                line=dict(
                    color=line_color,
                    width=line_width,
                    dash=line_dash
                ),
                fill='tonexty' if idx > 0 and stack_mode in ['stack', 'percent'] else 'tozeroy',
                fillpattern=dict(
                    shape=fill_pattern
                ) if fill_pattern else None,
                opacity=fill_opacity,
                marker=dict(
                    size=marker_size,
                    symbol='circle',
                    opacity=fill_opacity
                ) if marker_show else None
            ))

        if stack_mode == 'percent':
            fig.update_layout(yaxis=dict(tickformat='%'))

        fig = self.apply_common_layout(fig)
        return fig

