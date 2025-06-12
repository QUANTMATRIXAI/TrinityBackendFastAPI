# import streamlit as st
# import pandas as pd
# import requests

# st.set_page_config(page_title="Chart Generator Frontend", layout="centered")
# st.title('Chart Generator Frontend')

# API_URL = "http://localhost:8000/generate-chart"

# # Upload CSV
# uploaded_file = st.file_uploader('Upload CSV', type=['csv'])
# if uploaded_file:
#     df = pd.read_csv(uploaded_file)
#     st.write("Data Preview:")
#     st.dataframe(df.head())

#     chart_type = st.selectbox('Chart type', ['line', 'bar', 'pie', 'histogram', 'area'])
#     label = st.text_input('Series label', value='Series 1')

#     # Select columns based on chart type
#     if chart_type == 'histogram':
#         y_col = st.selectbox('Y column', df.columns)
#         x_col = None
#     elif chart_type == 'pie':
#         x_col = st.selectbox('Category column (X)', df.columns)
#         y_col = st.selectbox('Value column (Y)', df.columns)
#     else:
#         x_col = st.selectbox('X column', df.columns)
#         y_col = st.selectbox('Y column', df.columns)

#     # General chart options
#     title = st.text_input('Chart Title', value='My Chart')
#     x_label = st.text_input('X-axis Label', value=x_col if x_col else "")
#     y_label = st.text_input('Y-axis Label', value=y_col if y_col else "")

#     show_legend = st.checkbox('Show Legend', value=True)
#     show_values = st.checkbox('Show Value Annotations', value=True)
#     show_grid = st.checkbox('Show Grid', value=True)
#     font_size = st.number_input('Font Size', value=12, min_value=8, max_value=32)
#     background_color = st.color_picker('Background Color', value='#ffffff')

#     # --- Chart-type-specific style options ---
#     style = {}

#     if chart_type == 'line':
#         st.subheader("Line Chart Style")
#         line_color = st.color_picker('Line Color', value='#1f77b4')
#         line_width = st.slider('Line Width', 1.0, 5.0, 2.0)
#         line_style = st.selectbox('Line Style', ['-', '--', '-.', ':'])
#         marker = st.selectbox('Marker', ['o', 's', '^', 'D', '*', 'None'])
#         style['line'] = {
#             "linewidth": line_width,
#             "linestyle": line_style,
#             "marker": marker if marker != 'None' else '',
#             "color": line_color
#         }
#     elif chart_type == 'bar':
#         st.subheader("Bar Chart Style")
#         bar_color = st.color_picker('Bar Color', value='#4e79a7')
#         bar_width = st.slider('Bar Width', 0.1, 1.0, 0.7)
#         bar_alpha = st.slider('Bar Alpha', 0.1, 1.0, 0.8)
#         style['bar'] = {
#             "color": bar_color,
#             "width": bar_width,
#             "alpha": bar_alpha
#         }
#     elif chart_type == 'pie':
#         st.subheader("Pie Chart Style")
#         pie_colors = st.text_input('Pie Colors (comma-separated HEX)', value='#66c2a5,#fc8d62,#8da0cb,#e78ac3')
#         explode_str = st.text_input('Explode (comma-separated, e.g. 0.1,0,0,0)', value='0,0,0,0')
#         autopct = st.text_input('Autopct Format', value='%1.1f%%')
#         startangle = st.slider('Start Angle', 0, 360, 140)
#         style['pie'] = {
#             "colors": [c.strip() for c in pie_colors.split(',')],
#             "explode": [float(e.strip()) for e in explode_str.split(',')],
#             "autopct": autopct,
#             "startangle": startangle
#         }
#     elif chart_type == 'histogram':
#         st.subheader("Histogram Style")
#         bins = st.number_input('Number of Bins', min_value=1, max_value=50, value=10)
#         hist_color = st.color_picker('Histogram Color', value='#1f77b4')
#         hist_alpha = st.slider('Bar Alpha', 0.1, 1.0, 0.7)
#         edgecolor = st.color_picker('Edge Color', value='#000000')
#         style['histogram'] = {
#             "bins": bins,
#             "alpha": hist_alpha,
#             "color": hist_color,
#             "edgecolor": edgecolor
#         }
#     elif chart_type == 'area':
#         st.subheader("Area Chart Style")
#         area_color = st.color_picker('Area Color', value='#2ca02c')
#         area_alpha = st.slider('Area Alpha', 0.1, 1.0, 0.4)
#         area_linewidth = st.slider('Line Width', 0.5, 5.0, 2.0)
#         style['area'] = {
#             "alpha": area_alpha,
#             "color": area_color,
#             "linewidth": area_linewidth
#         }

#     # Always add general and annotation styles
#     style['general'] = {
#         "show_legend": show_legend,
#         "font_size": font_size,
#         "background_color": background_color
#     }
#     style['annotations'] = {
#         "show_values": show_values,
#         "show_grid": show_grid,
#         "grid_alpha": 0.3
#     }

#     # Auto-generate chart on input change (no button)
#     # Prepare data for API
#     if chart_type == 'histogram':
#         data = [{"label": label, "y": df[y_col].tolist()}]
#     elif chart_type == 'pie':
#         data = [{"label": label, "x": df[x_col].astype(str).tolist(), "y": df[y_col].tolist()}]
#     else:
#         data = [{"label": label, "x": df[x_col].tolist(), "y": df[y_col].tolist()}]

#     payload = {
#         "chart_type": chart_type,
#         "data": data,
#         "config": {
#             "title": title,
#             "x_label": x_label,
#             "y_label": y_label,
#             "style": style
#         }
#     }

#     st.subheader("Request JSON")
#     st.json(payload)

#     try:
#         response = requests.post(API_URL, json=payload)
#         st.write(f"Status code: {response.status_code}")
#         if response.status_code == 200:
#             st.image(response.content)
#         else:
#             st.error(f"Error from API: {response.text}")
#     except Exception as e:
#         st.error(f"Could not connect to API: {e}")

# else:
#     st.info('Please upload a CSV file to get started.')
