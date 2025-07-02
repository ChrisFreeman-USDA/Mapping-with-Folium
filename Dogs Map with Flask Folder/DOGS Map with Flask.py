#import libraries
import numpy as np
import matplotlib as plt
import openpyxl as openpy
import xlrd as xlrd
#Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
#API and geocoding libraries
import googlemaps
import gmplot
#Library to generate an HTML file
import webbrowser
#Library that can implement a delay before or after a call
from time import sleep
#Map visualization libraries
import folium
from folium.plugins import Draw
import geopandas as gpd
import branca
from branca.element import Element
#Library that allows viewing of file in Jupyter
from IPython.display import display, IFrame
import base64
from flask import Flask, render_template_string


app = Flask(__name__)



# Load data and images

df = pd.read_excel(r"SPREADSHEEET LOCATION")

with open("water.png", "rb") as f:
    data = f.read()
    encoded = base64.b64encode(data).decode("utf-8")
with open("housing programs.png", "rb") as f:
    data = f.read()
    encoded2 = base64.b64encode(data).decode("utf-8")
with open("community programs.png", "rb") as f:
    data = f.read()
    encoded3 = base64.b64encode(data).decode("utf-8")
with open("business programs.png", "rb") as f:
    data = f.read()
    encoded4 = base64.b64encode(data).decode("utf-8")

df = df.replace({
    "BUSINESS PROGRAMS": "Business Programs",
    "COMMUNITY FACILITIES": "Community Facilities",
    "WATER ENVIRONMENTAL PROGRAMS": "Water & Environmental Programs",
    "HOUSING PROGRAMS": "Housing Programs"
})

counties = gpd.read_file("GeoJSON file")

df['latitudes'] = pd.to_numeric(df['latitudes'], errors='coerce')
df['longitudes'] = pd.to_numeric(df['longitudes'], errors='coerce')
df = df.dropna(subset=['latitudes', 'longitudes'])
df['coordinates'] = list(zip(df['latitudes'], df['longitudes']))

@app.route('/test')
def test():
    return "Flask deployment successful"


@app.route('/')
def index():
    fmap = folium.Map(location=(34.0489, -111.0937), control_scale=True, zoom_start=7, tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', attr='OpenStreetMap')

    draw = Draw(
        draw_options={
            'polyline': {
                'shapeOptions': {
                    'color': 'blue', 'weight': 8, 'opacity': 0.7
                }
            },
            'rectangle': False, 'circle': False, 'marker': False,
            'polygon': False, 'circlemarker': False
        },
        edit_options={'edit': True}
    )
    draw.add_to(fmap)

    folium.GeoJson(counties, name="counties", style_function=lambda feature: {
        "fillColor": "#16254C", "color": "#26254C", "weight": 1, "fillOpacity": 0.1,
    }).add_to(fmap)

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
            if program == 'Business Programs':
                icon = folium.CustomIcon('business programs.png', icon_size=(20,20))
            elif program == 'Single Family Housing':
                icon = folium.CustomIcon('housing programs.png', icon_size=(20,20))
            elif program == 'Water and Environmental':
                icon = folium.CustomIcon('water.png', icon_size=(20,20))
            elif program == 'Community Facilities':
                icon = folium.CustomIcon('community programs.png', icon_size=(20,20))

            folium.Marker(
                location=latlon, tooltip=pname, popup=folium.Popup(pop_text, max_width=300), icon=icon
            ).add_to(fg)

        fg.add_to(fmap)

    folium.LayerControl(collapsed=True).add_to(fmap)

    legend_html = f"""
    {{% macro html(this, kwargs) %}}
    <div style="position: fixed; bottom: 0px; left: 0px; width: 195px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; opacity: 0.9; padding: 10px;">
        <b>Legend</b><br>
        <img src='data:image/png;base64,{encoded}' style='height:20px;'> Water & Environmental<br>
        <img src='data:image/png;base64,{encoded2}' style='height:20px;'> Housing<br>
        <img src='data:image/png;base64,{encoded3}' style='height:20px;'> Community Facilities<br>
        <img src='data:image/png;base64,{encoded4}' style='height:20px;'> Business Programs<br>
    </div>
    {{% endmacro %}}
    """

    legend = branca.element.MacroElement()
    legend._template = branca.element.Template(legend_html)
    fmap.get_root().add_child(legend)

    custom_html = Element("""
        <div style="position: fixed; bottom: 10px; right: 0px; width: 300px; height: 20px; 
                    border: 2px solid black; z-index: 9999; font-size: 12px;
                    background-color: white; opacity: 0.9; padding: 0px; text-align: center;">
            Created by <a href='mailto:EMAIL?subject=SUBJECT' 
            style='text-decoration: none; color: blue;'><b>NAME</b></a> / ORGANIZATION
        </div>
    """)
    fmap.get_root().html.add_child(custom_html)

    return fmap._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)

