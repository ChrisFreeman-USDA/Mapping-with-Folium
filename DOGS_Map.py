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

#Library that allows for dropdown filters(not functioning as this is an executable library)
#from streamlit_folium import st_folium

df = pd.read_excel(r"YOUR SPREADSHEET")

#convert custom images using base64 to work with HTML elements
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

df=df.replace(to_replace="col1", value="updated col 1")


#shape file for single state filter
# shape_file = gpd.read_file(r"SHP FILE")
# SDC = shape_file[shape_file["STATEFP"]=="04"]
# SDC.to_file('AZ Counties.geojson', driver = "GeoJson")

#shape file for multi state filter
#shape_file = gpd.read_file(r"SHP FILE")
# filter1 = shape_file["STATEFP"] == "38"
# filter2 = shape_file["STATEFP"] == "46"
# combined_filter = filter1 & filter2
# filter_gdf = shape_file[combined_filter]
# filter_gdf.to_file('filter_gdf.geojson', driver = "GeoJson")

#Create a DF from the GeoJson file for county outlines from their geometry
counties = gpd.read_file("GEOJSON FILE")

column_headers = df.columns.tolist()
# print(column_headers)

# Convert the entire 'latitudes' and 'longitudes' columns to numeric,
# coercing errors to NaN
df['latitudes'] = pd.to_numeric(df['latitudes'], errors='coerce')
df['longitudes'] = pd.to_numeric(df['longitudes'], errors='coerce')

# Combine the columns into a tuple, filtering out rows with missing values if needed
df = df.dropna(subset=['latitudes', 'longitudes'])
df['coordinates'] = list(zip(df['latitudes'], df['longitudes']))

#Create a base map
fmap = folium.Map(location=(34.0489, -111.0937), control_scale=True, zoom_start=7, tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', attr='OpenStreetMap')
#47.54 -100.437012 for ND
#Ability to draw lines on the map
draw = Draw(
    draw_options={
        'polyline': {
            'shapeOptions': {
                'color': 'blue',
                'weight': 8,  # Thickness of line
                'opacity': 0.7
            }
        },
        'rectangle': False,  # Hide rectangle tool
        'circle': False,
        'marker': False,
        'polygon': False,
        'circlemarker': False
    },
    edit_options={'edit': True}
)

# Add Draw to map
draw.add_to(fmap)


#Outline counties
folium.GeoJson(counties, name="counties", style_function=lambda feature: {
    "fillColor": "#16254C",
    "color": "#26254C",
    "weight": 1,
    "fillOpacity": 0.1,
}).add_to(fmap)
#Opacity think in revese. 0.9 is only 10% opaque
            

# #Define colors for each category
# program_icon_color = {
#     'Business Programs': 'green',
#     'Community Facilities': 'orange',
#     'Water & Environmental Programs': 'darkblue',
#     'Housing Programs': 'red'
# }



# #Define Icons for each category
# program_icon_name = {
#     'Business Programs': 'shop',
#     'Community Facilities': 'hospital',
#     'Water & Environmental Programs': 'water',
#     'Housing Programs': 'house'
# }
   
    
# For each Program, create a separate FeatureGroup
for program in df['COL0'].unique():
    fg = folium.FeatureGroup(name=program) 
    subset = df[df['COL0'] == program]
    
#Plot the points    
    for _, row in subset.iterrows():
        latlon = (row['latitudes'], row['longitudes'])
        pname = row['COL0']
       
     
        pop_text = (
            f"<b>COL1:</b> {row['COL1']}<br>"
            f"<b>COL2:</b> {COL2}<br>"
            f"<b>COL3:</b> {row['COL3']}<br>"
            f"<b>COL4:</b> {row['COL4']}"
        )
    
        if program == 'Business Programs':
            icon = folium.CustomIcon('CUSTOM ICON LOCATION', icon_size=(20,20))
        elif program == 'Single Family Housing':
            icon = folium.CustomIcon('CUSTOM ICON LOCATION', icon_size=(20,20))
        elif program == 'Water and Environmental':
            icon = folium.CustomIcon('CUSTOM ICON LOCATION', icon_size=(20,20))
        elif program == 'Community Facilities':
            icon = folium.CustomIcon('CUSTOM ICON LOCATION', icon_size=(20,20))
            
            
        folium.Marker(
            location=latlon,
            tooltip=pname,
            popup=folium.Popup(pop_text, max_width=300),
            icon=icon
            ).add_to(fg)

        fg.add_to(fmap) 


#Create a feature group
folium.LayerControl(collapsed=True).add_to(fmap)
              

legend_html = f"""
{{% macro html(this, kwargs) %}}
<div style="
    position: fixed; 
    bottom: 0px; left: 0px; width: 195px; height: 120px; 
    border:2px solid grey; z-index:9999; font-size:14px;
    background-color:white; opacity: 0.9;
    padding: 10px;">
<b>Legend</b><br>
<img src="data:image/png;base64,{encoded}" style="height:20px;"> CUSTOM IMAGE<br>
<img src="data:image/png;base64,{encoded2}" style="height:20px;"> CUSTOM IMAGE<br>
<img src="data:image/png;base64,{encoded3}" style="height:20px;"> CUSTOM IMAGE<br>
<img src="data:image/png;base64,{encoded4}" style="height:20px;"> CUSTOM IMAGE<br>
</div>
{{% endmacro %}}
"""


#Custom Text Box
custom_html = Element("""
    <div style="
        position: fixed; 
        bottom: 10px; right: 0px; width: 300px; height: 20px; 
        border: 2px solid black; z-index: 9999; font-size: 12px;
        background-color: white; opacity: 0.9;
        padding: 0px; text-align: center;">
      Created by <a href="mailto:EMAIL?subject=SUBJECT" 
      style="text-decoration: none; color: blue;">
      <b>NAME</b></a> / ORGANIZATION
    </div>
""")
fmap.get_root().html.add_child(custom_html)


legend = branca.element.MacroElement()
legend._template = branca.element.Template(legend_html)

fmap.get_root().add_child(legend)
    
#Print the map  
fmap.save('NAME OF OUTPUT FILE')

#Display map in Juypter
#display(IFrame('NAME OF OUTPUT FILE', width='100%', height='500px'))
