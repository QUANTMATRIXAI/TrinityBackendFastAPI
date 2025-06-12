from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import List
from app.features.chart_maker.Chart_Maker_API.app.schemas import Trace  # Or use your subplot spec model if different

class SubplotChart:
    def __init__(self, config):
        self.config = config

    def generate(self, data: List[dict]) -> go.Figure:
        subplot_cfg = self.config.subplots
        specs = self.config.subplot_specs

        fig = make_subplots(
            rows=subplot_cfg.rows,
            cols=subplot_cfg.cols,
            subplot_titles=subplot_cfg.subplot_titles or [],
            horizontal_spacing=subplot_cfg.horizontal_spacing,
            vertical_spacing=subplot_cfg.vertical_spacing
        )

        # Iterate over each data entry and subplot spec
        for idx, (row_data, subplot) in enumerate(zip(data, specs)):
            row = (idx // subplot_cfg.cols) + 1
            col = (idx % subplot_cfg.cols) + 1

            # Extract x and y from row_data (dict)
            # If you use Trace, make sure the subplot_specs model matches your needs
            # For CSV data, you may have a separate Trace for each subplot, or use the same columns for all
            # Here, we assume you have x_column, y_column, and name in your subplot_specs or Trace
            x = row_data[subplot.x_column]
            y = row_data[subplot.y_column]
            name = subplot.name or f"Series {idx+1}"

            # Choose trace type
            if subplot.chart_type == "line":
                trace = go.Scatter(x=x, y=y, name=name, mode="lines")
            elif subplot.chart_type == "bar":
                trace = go.Bar(x=x, y=y, name=name)
            elif subplot.chart_type == "scatter":
                trace = go.Scatter(x=x, y=y, name=name, mode="markers")
            else:
                # Default to line if unknown
                trace = go.Scatter(x=x, y=y, name=name, mode="lines")

            fig.add_trace(trace, row=row, col=col)

            # Per-subplot axis labels and font sizes
            fig.update_xaxes(
                title_text=subplot.x_label.text,
                title_font=dict(size=subplot.x_label.font_size, color=subplot.x_label.font_color),
                tickangle=subplot.x_label.rotation,
                row=row, col=col
            )
            fig.update_yaxes(
                title_text=subplot.y_label.text,
                title_font=dict(size=subplot.y_label.font_size, color=subplot.y_label.font_color),
                tickangle=subplot.y_label.rotation,
                row=row, col=col
            )

        # Optionally update overall layout title if present
        if hasattr(self.config, 'title') and self.config.title and hasattr(self.config.title, 'text'):
            fig.update_layout(title_text=self.config.title.text)

        return fig
