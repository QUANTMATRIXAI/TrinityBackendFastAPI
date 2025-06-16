from typing import List
import plotly.graph_objects as go
import numpy as np
from scipy.stats import gaussian_kde, norm, lognorm, gamma, beta, weibull_min, uniform
from app.features.chart_maker.Chart_Maker_API.app.schemas import Trace  # Make sure this is your Trace model with x_column, y_column, name
from .base_chart import BaseChart

class DistplotChart(BaseChart):
    def __init__(self, config):
        super().__init__(config)

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        fig = go.Figure()
        style = getattr(self.config.style, "distplot", None)
        if style is None:
            style = type('style', (), {
                'nbins': None,
                'bin_start': None,
                'bin_end': None,
                'bin_size': None,
                'histnorm': None,
                'hist_color': "#4B0082",
                'hist_opacity': 0.7,
                'orientation': 'v',
                'showlegend': True,
                'kde_show': False,
                'kde_bandwidth': 'scott',
                'kde_color': "#e74c3c",
                'dist_show': False,
                'dist_type': 'normal',
                'dist_color': "#2ca02c",
                'dist_line_width': 2
            })()

        # Use the first trace for distplot (only one trace supported for distplot)
        trace = traces[0] if traces else None
        if not trace or not data:
            return fig

        x_data = [row[trace.x_column] for row in data]
        name = trace.name or 'Histogram'

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
            marker=dict(
                color=style.hist_color or "#4B0082",
                opacity=style.hist_opacity if style.hist_opacity is not None else 0.7
            ),
            orientation=style.orientation or 'v',
            name=name,
            showlegend=style.showlegend if style.showlegend is not None else True
        ))

        # KDE curve
        if getattr(style, 'kde_show', False) and x_data:
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
                    line=dict(
                        color=style.kde_color or "#e74c3c",
                        width=2
                    ),
                    showlegend=style.showlegend if style.showlegend is not None else True
                ))
            except Exception as e:
                print(f"KDE calculation failed: {str(e)}")

        # Distribution fit curve
        if getattr(style, 'dist_show', False) and x_data:
            try:
                x_min, x_max = min(x_data), max(x_data)
                x_vals = np.linspace(x_min, x_max, 200)
                dist_name = style.dist_type or 'normal'
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
                            color=style.dist_color or "#2ca02c",
                            width=style.dist_line_width or 2
                        ),
                        showlegend=style.showlegend if style.showlegend is not None else True
                    ))
            except Exception as e:
                print(f"Distribution fit failed: {str(e)}")

        # Apply common layout (title, labels, grid, legend, annotations)
        fig = self.apply_common_layout(fig)
        return fig

    def _calculate_distribution_fit(self, data, x_vals, dist_name, bin_width):
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
