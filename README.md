# Mapping-with-Folium
This allows users who have a data set (and a Google Maps API key if geocoding is needed) to create an interactive map.

https://python-visualization.github.io/folium/latest/

There are a lot of markdowns in this code. That is because different scenarios warrant different code, but they remain there just in case. Below is the code snippet needed to geocode.


# Initialize Google Maps client with API key
gmaps = googlemaps.Client(key='Your API Key')
https://developers.google.com/maps/documentation/javascript/cloud-setup


# Geocode addresses to get coordinates
coordinates = []
for address in addresses:
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        coordinates.append((lat, lng))
        #consider removing the print line
        print(f"Geocoded: {address} -> ({lat}, {lng})")  

# How to save the coordinates so you don't need geocoding


latitudes = [lat for lat, lon in coordinates]
longitudes = [lon for lat, lon in coordinates]

df['latitudes'] = latitudes
df['longitudes'] = longitudes
df.to_excel('Test.xlsx', engine="openpyxl")

If you do not with to use custom icons with base64, bootstrap icons also work.

DOGS stands for Data on Geocoded Sites. It was chosen because we used to have a system called CATS that was used.
