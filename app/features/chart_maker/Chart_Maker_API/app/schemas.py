from typing import List, Optional, Literal, Union
from pydantic import BaseModel, conint, confloat

# Allowed types for style options
LineStyle = Literal['-', '--', '-.', ':']
MarkerStyle = Literal['o', 's', 'D', '^', 'v', '>', '<', 'p', '*', 'x']
GridType = Literal['both', 'horizontal', 'vertical', 'neither']
LegendPosition = Literal[  'top', 'bottom', 'left', 'right',
    'top+right', 'top+left', 'bottom+right', 'bottom+left',
    'left+top', 'left+bottom', 'right+top', 'right+bottom']
LegendOrientation = Literal['h', 'v']
PieTextPosition = Literal['inside', 'outside', 'auto', 'none']
PieTextInfo = Literal['label', 'percent', 'value', 'label+percent', 'label+value']

class Dataset(BaseModel):
    x: Optional[List[Union[str, float, int]]] = None
    y: Optional[List[Union[str, float, int]]] = None 
    z: Optional[List[List[float]]] = None            
    name: Optional[str] = None

class TitleConfig(BaseModel):
    text: str
    font_family: Optional[str] = "Arial"
    font_size: Optional[conint(ge=8, le=72)] = 24
    font_color: Optional[str] = "#2c3e50"

class AxisLabelConfig(BaseModel):
    text: str
    font_family: Optional[str] = "Arial"
    font_size: Optional[conint(ge=8, le=72)] = 16
    font_color: Optional[str] = "#3775b4"
    rotation: Optional[conint(ge=0, le=90)] = 0

class LineStyleConfig(BaseModel):
    linewidth: Optional[List[conint(ge=1, le=10)]] = [2]
    linestyle: Optional[List[LineStyle]] = ['-']
    marker: Optional[List[MarkerStyle]] = ['o']
    color: Optional[List[str]] = ["#27e230"]
    alpha: Optional[List[confloat(ge=0.0, le=1.0)]] = [1.0]
    markersize: Optional[List[conint(ge=4, le=20)]] = [8]


class BarStyleConfig(BaseModel):
    barmode: Literal['group', 'stack', 'overlay', 'relative'] = 'group'
    width: Optional[confloat(ge=0.1, le=1.0)] = None
    opacity: Optional[List[confloat(ge=0.0, le=1.0)]] = [0.8]
    color: Optional[List[str]] = ["#8da4b6", "#3C352F", "#83a183"]
    border_color: Optional[List[str]] = ["#A46161"]
    border_width: Optional[List[conint(ge=0, le=10)]] = [1]
    bargap: Optional[confloat(ge=0.0, le=1.0)] = 0.2
    bargroupgap: Optional[confloat(ge=0.0, le=1.0)] = 0.1
    orientation: Literal['v', 'h'] = 'v'
    textposition: Optional[Literal['auto', 'inside', 'outside', 'none']] = 'auto'
    texttemplate: Optional[str] = None
    insidetextanchor: Optional[Literal['start', 'middle', 'end']] = 'middle'
    textfont_size: Optional[int] = 8
    textfont_color: Optional[str] = "#222222"
    # Pattern shape (Plotly v5+): '', '/', '\\', 'x', '-', '|', '+', '.'
    pattern_shape: Optional[List[str]] = None
    pattern_fgcolor: Optional[List[str]] = None
    pattern_bgcolor: Optional[List[str]] = None

class PieStyleConfig(BaseModel):
    colors: Optional[List[str]] = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    opacity: Optional[confloat(ge=0.0, le=1.0)] = 1
    hole: Optional[confloat(ge=0.0, le=1.0)] = 0.0  # For donut charts (0=normal pie)
    textposition: Optional[PieTextPosition] = 'auto'
    textinfo: Optional[PieTextInfo] = 'percent'
    textfont_size: Optional[conint(ge=8, le=24)] = 14
    textfont_color: Optional[str] = "#19c833"
    rotation: Optional[conint(ge=0, le=360)] = 0
    pull: Optional[List[confloat(ge=0.0, le=1.0)]] = None  # For exploded segments
    sort: Optional[bool] = True  # Sort slices by size



class HistogramStyleConfig(BaseModel):
    # Existing histogram properties
    nbins: Optional[conint(ge=1)] = None
    bin_size: Optional[confloat(gt=0)] = None
    bin_start: Optional[float] = None
    bin_end: Optional[float] = None
    histnorm: Optional[Literal['', 'percent', 'probability', 'density', 'probability density']] = None
    cumulative: Optional[bool] = False
    color: Optional[List[str]] = None
    opacity: Optional[List[confloat(ge=0.0, le=1.0)]] = [0.8]
    border_color: Optional[List[str]] = None
    border_width: Optional[List[conint(ge=0, le=10)]] = [1]
    orientation: Literal['v', 'h'] = 'v'
    barmode: Optional[Literal['overlay', 'stack', 'group']] = 'overlay'
    showlegend: Optional[bool] = True
    textposition: Optional[Literal['auto', 'inside', 'outside', 'none']] = 'none'
    texttemplate: Optional[str] = None
    pattern_shape: Optional[List[str]] = None
    pattern_fgcolor: Optional[List[str]] = None
    pattern_bgcolor: Optional[List[str]] = None
    
    # New KDE/density curve properties
    show_kde: Optional[bool] = False
    kde_kernel: Optional[Literal['gaussian', 'tophat', 'epanechnikov', 
                               'exponential', 'linear', 'cosine']] = 'gaussian'
    kde_bandwidth: Optional[confloat(gt=0)] = None  # Auto-detected if None
    
    # New distribution fit properties
    show_distribution: Optional[bool] = False
    distribution_type: Optional[Literal['normal', 'lognormal', 'gamma', 
                                      'beta', 'weibull', 'uniform']] = 'normal'
    dist_line_color: Optional[str] = "#e74c3c"  # Red for contrast
    dist_line_width: Optional[conint(ge=1, le=5)] = 2



class AreaStyleConfig(BaseModel):
    # Stacking
    stack_mode: Literal['none', 'stack', 'percent'] = 'none'
    
    # Area Style
    fill_opacity: confloat(ge=0.0, le=1.0) = 0.5
    fill_pattern: Optional[Literal['/', '\\', 'x', '-', '|', '+', '.']] = None
    
    # Line Style
    line_color: List[str] = ["#1f77b4", "#ff7f0e"]
    line_width: List[conint(ge=1, le=5)] = [2]
    line_dash: List[Literal['solid', 'dash', 'dot']] = ['solid']
    
    # Markers
    markers_show: bool = False
    markers_size: conint(ge=4, le=20) = 6


class DistplotStyleConfig(BaseModel):
    nbins: Optional[int] = None
    bin_size: Optional[float] = None
    bin_start: Optional[float] = None
    bin_end: Optional[float] = None
    histnorm: Optional[Literal['', 'percent', 'probability', 'density']] = ''
    hist_color: Optional[str] = "#4B0082"
    hist_opacity: Optional[float] = 0.7
    
    kde_show: Optional[bool] = True
    kde_color: Optional[str] = "#e74c3c"
    kde_bandwidth: Optional[float] = None
    
    dist_show: Optional[bool] = False
    dist_type: Optional[Literal['normal', 'lognormal', 'gamma', 'beta', 'weibull', 'uniform']] = 'normal'
    dist_color: Optional[str] = "#2ca02c"
    dist_line_width: Optional[int] = 2

    orientation: Literal['v', 'h'] = 'v'
    showlegend: Optional[bool] = True

class ScatterStyleConfig(BaseModel):
    # Line control
    show_line: bool = False  
    mode: Literal['markers', 'lines', 'lines+markers'] = 'markers'
    
    marker_size: Union[int, List[int]] = 10
    marker_color: Union[str, List[str]] = '#1f77b4'
    marker_symbol: Union[str, List[str]] = 'circle'
    marker_opacity: Union[float, List[float]] = 0.8
    marker_line_color: Union[str, List[str]] = '#000000'
    marker_line_width: Union[int, List[int]] = 1
    
    line_color: Union[str, List[str]] = '#1f77b4'
    line_width: Union[int, List[int]] = 2
    line_dash: Union[str, List[str]] = 'solid'
    
    # Text labels
    textposition: Optional[Literal['top left', 'top center', 'top right', 
                                 'middle left', 'middle center', 'middle right',
                                 'bottom left', 'bottom center', 'bottom right', 
                                 'none']] = 'none'
    textfont_size: int = 12
    textfont_color: str = '#000000'


class WaterfallStyleConfig(BaseModel):
    measure: Optional[List[Literal['absolute', 'relative', 'total']]] = None
    base: Optional[float] = None
    connector_line_color: Optional[str] = '#444'
    connector_line_width: Optional[conint(ge=0, le=10)] = 1
    increasing_color: Optional[str] = '#3D9970'
    decreasing_color: Optional[str] = '#FF4136'
    total_color: Optional[str] = '#0074D9'
    orientation: Literal['v', 'h'] = 'v'
    showlegend: Optional[bool] = True
    textposition: Optional[Literal[
        'inside', 'outside', 'auto', 'none', 'top', 'bottom', 'middle', 'left', 'right'
    ]] = 'auto'
    textfont_size: Optional[conint(ge=8, le=24)] = 12
    textfont_color: Optional[str] = '#000000'

class HeatmapStyleConfig(BaseModel):
    colorscale: Optional[Union[str, List[Union[str, List[Union[float, str]]]]]] = "Viridis"
    colorbar_title: Optional[str] = None
    zmin: Optional[float] = None
    zmax: Optional[float] = None
    showscale: Optional[bool] = True
    reversescale: Optional[bool] = False
    opacity: Optional[confloat(ge=0.0, le=1.0)] = 1.0
    xgap: Optional[conint(ge=0)] = 0
    ygap: Optional[conint(ge=0)] = 0
    hoverinfo: Optional[str] = "z"
    zhoverformat: Optional[str] = None
    transpose: Optional[bool] = False
    heatmap_annotations_show: Optional[bool] = False
    heatmap_annotations_font_size: Optional[int] = 12
    heatmap_annotations_font_color: Optional[str] = "#000000"

class AnnotationConfig(BaseModel):
    show_values: Optional[bool] = False
    show_x_values: Optional[Union[List[Union[str, float, int]], Literal["all"]]] = None
    show_y_values: Optional[Union[List[Union[float, int]], Literal["all"]]] = None
    show_line: Optional[bool] = False  # New: toggle vertical lines
    line_color: Optional[str] = "#7f8c8d"
    line_width: Optional[conint(ge=1, le=5)] = 1
    line_dash: Optional[Literal["solid", "dot", "dash", "longdash"]] = "solid"
    font_size: Optional[conint(ge=8, le=24)] = 12
    font_color: Optional[str] = "#2c3e50"
    arrow_color: Optional[str] = "#7f8c8d"

class LegendConfig(BaseModel):
    show: Optional[bool] = True
    labels: Optional[List[str]] = None  # Overrides dataset names if provided
    position: Optional[LegendPosition] = "top"
    orientation: Optional[LegendOrientation] = "v"

class GridConfig(BaseModel):
    type: Optional[GridType] = "both"
    color: Optional[str] = "#e0e0e0"

class StyleConfig(BaseModel):
    line: Optional[LineStyleConfig] = None
    bar: Optional[BarStyleConfig] = None
    # Add other chart types as needed:
    pie: Optional[PieStyleConfig] = None
    histogram: Optional[HistogramStyleConfig] = None
    area: Optional[AreaStyleConfig] = None
    distplot : Optional[DistplotStyleConfig] = None
    scatter: Optional[ScatterStyleConfig] = None
    waterfall: Optional[WaterfallStyleConfig] = None
    heatmap: Optional[HeatmapStyleConfig] = None


class SubplotConfig(BaseModel):
    rows: int
    cols: int
    subplot_titles: List[str] = []
    horizontal_spacing: float = 0.1
    vertical_spacing: float = 0.1

class SubplotSpec(BaseModel):
    chart_type: Literal['line', 'bar', 'scatter', 'area', 'histogram']
    x_label: AxisLabelConfig
    y_label: AxisLabelConfig


class Trace(BaseModel):
    x_column: str
    y_column: str
    name: str

class ChartConfig(BaseModel):
    title: TitleConfig
    x_label: Optional[AxisLabelConfig] = None  # Make optional
    y_label: Optional[AxisLabelConfig] = None  # Make optional
    style: Optional[StyleConfig] = StyleConfig()
    annotations: Optional[AnnotationConfig] = AnnotationConfig()
    legend: Optional[LegendConfig] = LegendConfig()
    grid: Optional[GridConfig] = GridConfig()
    subplots: Optional[SubplotConfig] = None
    subplot_specs: List[SubplotSpec] = []


class ChartRequest(BaseModel):
    config: ChartConfig
    chart_type: Literal['line', 'bar', "pie", "histogram", "area", "distplot", "scatter", "waterfall", "heatmap", "subplots"]
    traces: List[Trace]


############################ Filter Schema ##################################################################
class CategoricalFilter(BaseModel):
    column:str
    selected_values: List[Union[str, int, float]]
    type: Literal['categorical'] = 'categorical'

class NumericalFilter(BaseModel):
    column: str
    operator: Literal['>', '<', '>=', '<=', '==', '!=']
    value: float
    type: Literal['numerical'] = 'numerical'

class FilterRequest(BaseModel):
    filters: List[Union[CategoricalFilter, NumericalFilter]]

