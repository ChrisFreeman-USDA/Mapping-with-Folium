import os
import json
import base64
import pandas as pd
import folium
from folium.plugins import Draw
from branca.element import Element, MacroElement, Template

# 1. Databricks widgets for user input
dbutils.widgets.text("spreadsheet_file", "", "Spreadsheet File Path")
dbutils.widgets.text("geojson_file", "", "GeoJSON File Path (optional)")
dbutils.widgets.text("output_file", "/dbfs/tmp/output_map.html", "Output HTML Path")
dbutils.widgets.dropdown("state", "North Dakota", [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
    "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
], "State")

# 2. Get widget values
spreadsheet_file = dbutils.widgets.get("spreadsheet_file")
geojson_file = dbutils.widgets.get("geojson_file")
output_file = dbutils.widgets.get("output_file")
selected_state = dbutils.widgets.get("state")

# 3. State coordinates dictionary
state_coords = {
    "Alabama": (32.806671, -86.791130),
    "Alaska": (61.370716, -152.404419),
    "Arizona": (34.168218, -111.930907),
    "Arkansas": (34.746613, -92.288986),
    "California": (37.271874, -119.270415),
    "Colorado": (38.997934, -105.550567),
    "Connecticut": (41.518783, -72.757507),
    "Delaware": (38.989597, -75.505571),
    "Florida": (27.994402, -81.760254),
    "Georgia": (32.165622, -82.900075),
    "Hawaii": (20.798362, -156.331925),
    "Idaho": (44.068203, -114.742043),
    "Illinois": (40.633125, -89.398528),
    "Indiana": (39.849426, -86.258278),
    "Iowa": (42.011539, -93.210526),
    "Kansas": (38.526600, -98.362885),
    "Kentucky": (37.839333, -84.270020),
    "Louisiana": (30.984298, -91.962333),
    "Maine": (45.253783, -69.445469),
    "Maryland": (39.045753, -76.641273),
    "Massachusetts": (42.407211, -71.382437),
    "Michigan": (44.314844, -85.602364),
    "Minnesota": (46.729553, -94.685900),
    "Mississippi": (32.741646, -89.678696),
    "Missouri": (38.573936, -92.603760),
    "Montana": (46.879682, -110.362566),
    "Nebraska": (41.492537, -99.901813),
    "Nevada": (38.802610, -116.419389),
    "New Hampshire": (43.193852, -71.572395),
    "New Jersey": (40.058324, -74.405661),
    "New Mexico": (34.972730, -105.032363),
    "New York": (42.165726, -74.948051),
    "North Carolina": (35.759573, -79.019300),
    "North Dakota": (47.551493, -101.002012),
    "Ohio": (40.417287, -82.907123),
    "Oklahoma": (35.007752, -97.092877),
    "Oregon": (43.804133, -120.554201),
    "Pennsylvania": (41.203323, -77.194525),
    "Rhode Island": (41.580095, -71.477429),
    "South Carolina": (33.836081, -81.163725),
    "South Dakota": (43.969515, -99.901813),
    "Tennessee": (35.517491, -86.580447),
    "Texas": (31.968599, -99.901813),
    "Utah": (39.320980, -111.093731),
    "Vermont": (44.558803, -72.577841),
    "Virginia": (37.431573, -78.656894),
    "Washington": (47.751074, -120.740139),
    "West Virginia": (38.597626, -80.454903),
    "Wisconsin": (43.784439, -88.787868),
    "Wyoming": (43.075968, -107.290283)
}

def encode_img(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {path}: {e}")
        return ""

def generate_map(spreadsheet_file, geojson_file, output_file, selected_state):
    if not spreadsheet_file or not os.path.exists(spreadsheet_file):
        print("No spreadsheet file selected or file does not exist.")
        return

    # Center map on selected state
    lat, lon = state_coords.get(selected_state, (47.551493, -101.002012))
    fmap = folium.Map(
        location=[lat, lon],
        control_scale=True,
        zoom_start=6,
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='OpenStreetMap'
    )

    # Load DataFrame
    if spreadsheet_file.lower().endswith(('.xlsx', '.xls')):
        df = pd.read_excel(spreadsheet_file)
    elif spreadsheet_file.lower().endswith('.csv'):
        df = pd.read_csv(spreadsheet_file)
    else:
        print("Unsupported spreadsheet format.")
        return

    # Add drawing tools
    draw = Draw(
        draw_options={
            'polyline': {'shapeOptions': {'color': 'blue', 'weight': 8, 'opacity': 0.7}},
            'rectangle': False, 'circle': False, 'marker': False, 'polygon': False, 'circlemarker': False
        },
        edit_options={'edit': True}
    )
    draw.add_to(fmap)

    # Optionally load GeoJSON
    if geojson_file and os.path.exists(geojson_file):
        try:
            with open(geojson_file, "r") as geo:
                counties = json.load(geo)
            folium.GeoJson(
                counties,
                name="counties",
                style_function=lambda feature: {
                    "fillColor": "#16254C",
                    "color": "#26254C",
                    "weight": 1,
                    "fillOpacity": 0.1,
                }
            ).add_to(fmap)
        except Exception as e:
            print("Error loading GeoJSON file:", e)

    # Create Feature Groups by Program
    for program in df['Program'].unique():
        fg = folium.FeatureGroup(name=program)
        subset = df[df['Program'] == program]
        for _, row in subset.iterrows():
            latlon = (row['latitudes'], row['longitudes'])
            pname = row['Project Name']
            pop_text = (
                f"<b>Project Description:</b> {row['Project Description']}<br>"
                f"<b>Program:</b> {program}<br>"
                f"<b>County:</b> {row['County']}<br>"
                f"<b>Fiscal Year:</b> {row['Fiscal Year']}"
            )
            # Custom icons based on program names
            icon = None
            icon_paths = {
                'Business Programs': '/dbfs/Icons/business programs.png',
                'Single Family Housing': '/dbfs/Icons/housing programs.png',
                'Water and Environmental': '/dbfs/Icons/water.png',
                'Community Facilities': '/dbfs/Icons/community programs.png'
            }
            if program in icon_paths and os.path.exists(icon_paths[program]):
                icon = folium.CustomIcon(icon_paths[program], icon_size=(20, 20))
            marker_params = dict(
                location=latlon,
                tooltip=pname,
                popup=folium.Popup(pop_text, max_width=300)
            )
            if icon:
                marker_params['icon'] = icon
            folium.Marker(**marker_params).add_to(fg)
        fg.add_to(fmap)

    folium.LayerControl(collapsed=True).add_to(fmap)

    # Add Legend (update icon paths as needed)
    encoded = encode_img('/dbfs/Icons/water.png')
    encoded2 = encode_img('/dbfs/Icons/housing programs.png')
    encoded3 = encode_img('/dbfs/Icons/community programs.png')
    encoded4 = encode_img('/dbfs/Icons/business programs.png')
    legend_html = f"""
    {{% macro html(this, kwargs) %}}
    <div style="
        position: fixed; 
        bottom: 0px; left: 0px; width: 195px; height: 120px; 
        border:2px solid grey; z-index:9999; font-size:14px;
        background-color:white; opacity: 0.9;
        padding: 10px;">
    <b>Legend</b><br>
    <img src="data:image/png;base64,{encoded}" style="height:20px;"> Water & Environmental<br>
    <img src="data:image/png;base64,{encoded2}" style="height:20px;"> Housing<br>
    <img src="data:image/png;base64,{encoded3}" style="height:20px;"> Community Facilities<br>
    <img src="data:image/png;base64,{encoded4}" style="height:20px;"> Business Programs<br>
    </div>
    {{% endmacro %}}
    """
    legend = MacroElement()
    legend._template = Template(legend_html)
    fmap.get_root().add_child(legend)

    # Custom Footer
    custom_html = Element("""
        <div style="
            position: fixed; 
            bottom: 10px; right: 0px; width: 300px; height: 20px; 
            border: 2px solid black; z-index: 9999; font-size: 12px;
            background-color: white; opacity: 0.9;
            padding: 0px; text-align: center;">
          Created by <a href="mailto:christopher.freeman@usda.gov?subject=DOGS Map" 
          style="text-decoration: none; color: blue;"><b>Christopher Freeman</b></a> / USDA RD ND
        </div>
    """)
    fmap.get_root().html.add_child(custom_html)

    # Save map
    fmap.save(output_file)
    print(f"Map successfully saved to {output_file}")

# 4. Run the map generation
generate_map(spreadsheet_file, geojson_file, output_file, selected_state)

# 5. Display the map in Databricks notebook
from IPython.display import display, HTML
display(HTML(f'<iframe src="/files{output_file[5:]}" width=900 height=600></iframe>'))