from .base_chart import BaseChart
import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde, norm, lognorm, gamma, beta, weibull_min, uniform
from typing import List
from app.features.chart_maker.Chart_Maker_API.app.schemas import Trace  # Make sure this is your Trace model with x_column, y_column, name

class HistogramChart(BaseChart):
    def __init__(self, config):
        super().__init__(config)

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        fig = go.Figure()
        style = getattr(self.config.style, "histogram", None)
        if style is None:
            style = type('style', (), {
                'nbins': None,
                'bin_start': None,
                'bin_end': None,
                'bin_size': None,
                'histnorm': None,
                'cumulative': False,
                'color': ['#1f77b4'],
                'opacity': [0.8],
                'border_color': ['#222222'],
                'border_width': [1],
                'orientation': 'v',
                'show_kde': False,
                'kde_bandwidth': 'scott',
                'show_distribution': False,
                'distribution_type': 'normal',
                'dist_line_color': '#e74c3c',
                'dist_line_width': 2
            })()

        # Use the first trace for histogram
        if not traces or not data:
            return fig
        trace = traces[0]
        x_data = [row[trace.x_column] for row in data]
        if not isinstance(x_data, list) or len(x_data) == 0:
            return fig

        # Histogram trace
        fig.add_trace(go.Histogram(
            x=x_data,
            nbinsx=style.nbins or None,
            xbins=dict(
                start=style.bin_start,
                end=style.bin_end,
                size=style.bin_size
            ) if any([style.bin_size, style.bin_start, style.bin_end]) else None,
            histnorm=style.histnorm or None,
            cumulative=dict(enabled=bool(style.cumulative)),
            marker=dict(
                color=style.color[0] if style.color and len(style.color) > 0 else '#1f77b4',
                opacity=style.opacity[0] if style.opacity and len(style.opacity) > 0 else 0.8,
                line=dict(
                    color=style.border_color[0] if style.border_color and len(style.border_color) > 0 else '#222222',
                    width=style.border_width[0] if style.border_width and len(style.border_width) > 0 else 1
                )
            ),
            orientation=style.orientation or 'v',
            name=trace.name or 'Histogram'
        ))

        # KDE curve
        if getattr(style, 'show_kde', False) and x_data:
            try:
                kde = gaussian_kde(x_data, bw_method=style.kde_bandwidth or 'scott')
                x_min, x_max = min(x_data), max(x_data)
                x_vals = np.linspace(x_min, x_max, 200)
                kde_vals = kde(x_vals)
                bin_width = (style.bin_size or (x_max - x_min) / (style.nbins or 10))
                fig.add_trace(go.Scatter(
                    x=x_vals.tolist(),
                    y=(kde_vals * len(x_data) * bin_width).tolist(),
                    mode='lines',
                    name='KDE',
                    line=dict(color='#e74c3c', width=2)
                ))
            except Exception as e:
                print(f"KDE calculation failed: {str(e)}")

        # Distribution fit curve
        if getattr(style, 'show_distribution', False) and x_data:
            try:
                x_min, x_max = min(x_data), max(x_data)
                x_vals = np.linspace(x_min, x_max, 200)
                dist_name = style.distribution_type or 'normal'
                bin_width = (style.bin_size or (x_max - x_min) / (style.nbins or 10))
                dist_y = self._calculate_distribution_fit(
                    x_data, x_vals, dist_name, bin_width
                )
                if dist_y is not None:
                    fig.add_trace(go.Scatter(
                        x=x_vals.tolist(),
                        y=dist_y.tolist(),
                        mode='lines',
                        name=f'{dist_name.capitalize()} Fit',
                        line=dict(
                            color=style.dist_line_color or '#e74c3c',
                            width=style.dist_line_width or 2
                        )
                    ))
            except Exception as e:
                print(f"Distribution fit failed: {str(e)}")

        return self.apply_common_layout(fig)

    def _calculate_distribution_fit(self, data, x_vals, dist_name, bin_width):
        """Helper method for distribution calculations"""
        x_vals_np = np.array(x_vals)
        try:
            if dist_name == 'normal':
                mu, std = norm.fit(data)
                return norm.pdf(x_vals_np, mu, std) * len(data) * bin_width
            elif dist_name == 'lognormal':
                shape, loc, scale = lognorm.fit(data, floc=0)
                return lognorm.pdf(x_vals_np, shape, loc, scale) * len(data) * bin_width
            elif dist_name == 'gamma':
                a, loc, scale = gamma.fit(data)
                return gamma.pdf(x_vals_np, a, loc, scale) * len(data) * bin_width
            elif dist_name == 'beta':
                a, b, loc, scale = beta.fit(data)
                return beta.pdf(x_vals_np, a, b, loc, scale) * len(data) * bin_width
            elif dist_name == 'weibull':
                c, loc, scale = weibull_min.fit(data)
                return weibull_min.pdf(x_vals_np, c, loc, scale) * len(data) * bin_width
            elif dist_name == 'uniform':
                loc, scale = uniform.fit(data)
                return uniform.pdf(x_vals_np, loc, scale) * len(data) * bin_width
        except Exception as e:
            print(f"Distribution {dist_name} fit error: {str(e)}")
            return None
