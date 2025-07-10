# Databricks notebook version using dbutils.widgets for user input

import pandas as pd
import folium
from IPython.display import display, HTML

# Create widgets for user input
dbutils.widgets.text("spreadsheet_file", "", "Spreadsheet File Path (e.g., /dbfs/FileStore/tables/yourfile.xlsx)")
dbutils.widgets.text("geojson_file", "", "GeoJSON File Path (optional, e.g., /dbfs/FileStore/tables/yourfile.geojson)")
dbutils.widgets.dropdown("state", "North Dakota", ["North Dakota", "South Dakota", "Minnesota"], "State")

# Get widget values
spreadsheet_file = dbutils.widgets.get("spreadsheet_file")
geojson_file = dbutils.widgets.get("geojson_file")
state = dbutils.widgets.get("state")

# Only run if spreadsheet_file is provided
if spreadsheet_file:
    # Read spreadsheet
    if spreadsheet_file.endswith(".csv"):
        df = pd.read_csv(spreadsheet_file)
    else:
        df = pd.read_excel(spreadsheet_file)
    
    # Set map center based on state
    state_coords = {
        "North Dakota": [47.551493, -101.002012],
        "South Dakota": [43.969515, -99.901813],
        "Minnesota": [46.729553, -94.685900]
    }
    center = state_coords.get(state, [47.551493, -101.002012])
    fmap = folium.Map(location=center, zoom_start=6)
    
    # Optionally add GeoJSON overlay
    if geojson_file:
        import json
        with open(geojson_file, "r") as gj:
            geojson_data = json.load(gj)
        folium.GeoJson(geojson_data, name="geojson").add_to(fmap)
    
    # Example: Add points from DataFrame if lat/lon columns exist
    if "latitudes" in df.columns and "longitudes" in df.columns:
        for _, row in df.iterrows():
            folium.Marker(
                location=[row["latitudes"], row["longitudes"]],
                popup=str(row.get("Project Name", "")),
            ).add_to(fmap)
    
    # Save and display the map
    output_path = "/dbfs/tmp/output_map.html"
    fmap.save(output_path)
    display(HTML(f'<iframe src="/files/tmp/output_map.html" width=900 height=600></iframe>'))
else:
    print("Please provide a spreadsheet file path in the widget above.")