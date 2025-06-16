import plotly.graph_objects as go
from app.features.chart_maker.Chart_Maker_API.app.schemas import ChartConfig

class BaseChart:
    def __init__(self, config: ChartConfig):
        self.config = config

    def _get_legend_position(self):
        mapping = {
            "top": dict(x=0.5, y=1.0, xanchor="center", yanchor="top"),
            "bottom": dict(x=0.5, y=0.0, xanchor="center", yanchor="bottom"),
            "left": dict(x=0.0, y=0.5, xanchor="left", yanchor="middle"),
            "right": dict(x=1.0, y=0.5, xanchor="right", yanchor="middle"),
            "top+right": dict(x=1.0, y=1.0, xanchor="right", yanchor="top"),
            "top+left": dict(x=0.0, y=1.0, xanchor="left", yanchor="top"),
            "bottom+right": dict(x=1.0, y=0.0, xanchor="right", yanchor="bottom"),
            "bottom+left": dict(x=0.0, y=0.0, xanchor="left", yanchor="bottom"),
            "left+top": dict(x=0.0, y=1.0, xanchor="left", yanchor="top"),
            "left+bottom": dict(x=0.0, y=0.0, xanchor="left", yanchor="bottom"),
            "right+top": dict(x=1.0, y=1.0, xanchor="right", yanchor="top"),
            "right+bottom": dict(x=1.0, y=0.0, xanchor="right", yanchor="bottom"),
        }
        return mapping.get(self.config.legend.position, mapping["top"])


    def apply_common_layout(self, fig: go.Figure) -> go.Figure:
        """Applies title, axis labels, fonts, grids, legend, and annotations"""
        # Title
        fig.update_layout(
            title=dict(
                text=self.config.title.text,
                font=dict(
                    family=self.config.title.font_family,
                    size=self.config.title.font_size,
                    color=self.config.title.font_color
                )
            )
        )

        # X-axis
        fig.update_xaxes(
            title=dict(
                text=self.config.x_label.text,
                font=dict(
                    family=self.config.x_label.font_family,
                    size=self.config.x_label.font_size,
                    color=self.config.x_label.font_color
                )
            ),
            showgrid=self.config.grid.type in ['both', 'vertical'],
            gridcolor=self.config.grid.color,
            tickangle=self.config.x_label.rotation
        )

        # Y-axis
        fig.update_yaxes(
            title=dict(
                text=self.config.y_label.text,
                font=dict(
                    family=self.config.y_label.font_family,
                    size=self.config.y_label.font_size,
                    color=self.config.y_label.font_color
                )
            ),
            showgrid=self.config.grid.type in ['both', 'horizontal'],
            gridcolor=self.config.grid.color,
            tickangle=self.config.y_label.rotation
        )

        # Legend
        fig.update_layout(
            showlegend=self.config.legend.show,
            legend=dict(
                orientation=self.config.legend.orientation,
                **self._get_legend_position()
            )
        )

        # Annotations with optional vertical lines
        ann = self.config.annotations
        if ann and ann.show_values:
            # Get y-axis baseline (handles both zero and non-zero baselines)
            y_min = fig.layout.yaxis.range[0] if fig.layout.yaxis and fig.layout.yaxis.range else 0

            for trace in fig.data:
                x_vals = trace.x if hasattr(trace, 'x') else []
                y_vals = trace.y if hasattr(trace, 'y') else []
                
                for x, y in zip(x_vals, y_vals):
                    # X condition
                    x_match = (
                        ann.show_x_values is None or
                        ann.show_x_values == "all" or
                        (isinstance(ann.show_x_values, list) and x in ann.show_x_values)
                    )

                    # Y condition
                    y_match = (
                        ann.show_y_values is None or
                        ann.show_y_values == "all" or
                        (isinstance(ann.show_y_values, list) and y in ann.show_y_values)
                    )

                    if x_match and y_match:
                        # Add annotation
                        fig.add_annotation(
                            x=x,
                            y=y,
                            text=f"({x}, {y})",
                            showarrow=True,
                            font=dict(
                                size=ann.font_size,
                                color=ann.font_color
                            ),
                            arrowcolor=ann.arrow_color,
                            yshift=10
                        )

                        # Add vertical line if enabled
                        if ann.show_line:
                            fig.add_shape(
                                type="line",
                                x0=x, y0=0,
                                x1=x, y1=y,
                                line=dict(
                                    color=ann.line_color,
                                    width=ann.line_width,
                                    dash=ann.line_dash
                                ),
                                layer='below'  # Draw line behind the chart elements
                            )

        return fig
