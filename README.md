# Summary 
As a communicator in a government agency, maximizing efforts to inform and interact with our audiences is a cornerstone of the profession. This becomes more challenging as we travel across the state, often to the most rural of areas. Our current tools in use require us to know every location across a state, which is not generally feasible. According to the North Dakota League of Cities, there are 355 incorporated cities spread across the state. With the large majority of those being classified as rural or frontier, our eligible program areas encompass most of the state. Relying on someone to know where every single one of our obligated projects are, then to aggregate it with funded projects within a reasonable travel distance is inefficient use of time and resources. 

When planning for outreach events, trying to coordinate additional visits in conjunction with the main outreach event presents a challenge. The information needed is not plotted on a map and is instead relegated to a spreadsheet. The Python script for this capstone shows a way to visualize projects, with usage for both past and present. The script scrubs the spreadsheet and plots the points in an HTML format that is shareable with others. DOGS stands for Data on Geocoded Sites. This is a reference to a previous system called CATS that was used.

# Mapping-with-Folium
This allows users who have a data set (and a Google Maps API key if geocoding is needed) to create an interactive map. The purpose of this is to give the end user a simple way to create an interactive map.

https://python-visualization.github.io/folium/latest/

There are a lot of comment in the code. That is because different scenarios warrant different code, but they remain there just in case. Below is the code snippet needed to geocode.

# Initialize Google Maps client with API key

If geocoding is needed, you will need an API key. There is a free tier, but it has limited calls per month. Reference their documentation for specific information.
gmaps = googlemaps.Client(key='Your API Key')
https://developers.google.com/maps/documentation/javascript/cloud-setup

# GeoJSON
Shape files can be used here. I have tested one with state county boundaries and congressional district boundaries. Both have worked. For most of the scripts, you would need to manually change the coodinates (in the original script, it is on line 81: fmap = folium.Map(location=(34.0489, -111.0937))

I also commented out the GeoJSON file creation because if you run it more than once, it will throw errors.

# Notes

If you do not with to use custom icons with base64, bootstrap icons also work. These scripts have custom visualization, ranging from custom icons using base64, to popups, and a draw feature (draw has additional polygons you can draw with, but they were not needed for this application)

In order to change which columns are referenced in which popup, you would need to change the column names in the code.

This Read Me will not cover every scenario. If you run into errors, I would suggest referencing the folium repositories as well as paying attention to the logs in your terminal. This helped me debug numerous items throughout the creation of the scripts.

# Thanks and Appreciation
This would not have been possible without the immense help from the USDA Data Science Training Program facilitators, Michael Frye, Chris Stewart, Tegan Fager, and db55falcon. What started as a "what if" turned into a project I am extremely proud of.