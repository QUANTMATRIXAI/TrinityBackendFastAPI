from .schemas import ChartRequest
from app.features.chart_maker.Chart_Maker_API.charts.line_chart import LineChart
from app.features.chart_maker.Chart_Maker_API.charts.bar_chart import BarChart
from app.features.chart_maker.Chart_Maker_API.charts.pie_chart import PieChart
from app.features.chart_maker.Chart_Maker_API.charts.histogram_chart import HistogramChart
from app.features.chart_maker.Chart_Maker_API.charts.area import AreaChart
from app.features.chart_maker.Chart_Maker_API.charts.distplot import DistplotChart
from app.features.chart_maker.Chart_Maker_API.charts.scatter_chart import ScatterChart
from app.features.chart_maker.Chart_Maker_API.charts.waterfall_chart import WaterfallChart
from app.features.chart_maker.Chart_Maker_API.charts.heatmap_chart import HeatmapChart
from app.features.chart_maker.Chart_Maker_API.charts.subplots import SubplotChart
from typing import List
import plotly.graph_objects as go

def create_chart(request: ChartRequest, data: List[dict]) -> go.Figure:
    if request.chart_type == "subplots":
        chart = SubplotChart(request.config)
        return chart.generate(data)
    else:
        # Instantiate the appropriate chart class
        if request.chart_type == "line":
            chart = LineChart(request.config)
        elif request.chart_type == "bar":
            chart = BarChart(request.config)
        elif request.chart_type == "pie":
            chart = PieChart(request.config)
        elif request.chart_type == "histogram":
            chart = HistogramChart(request.config)
        elif request.chart_type == "area":
            chart = AreaChart(request.config)
        elif request.chart_type == "distplot":
            chart = DistplotChart(request.config)
        elif request.chart_type == "scatter":
            chart = ScatterChart(request.config)
        elif request.chart_type == "waterfall":
            chart = WaterfallChart(request.config)
        elif request.chart_type == "heatmap":
            chart = HeatmapChart(request.config)
        else:
            raise ValueError(f"Unsupported chart type: {request.chart_type}")
        
        print("line")
        # For single charts, pass traces and data
        return chart.generate(request.traces, data)



