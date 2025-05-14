# Mapping-with-Folium
This allows users who have a data set (and a Google Maps API key if geocoding is needed) to create an interactive map.

There are a lot of markdowns in this code. That is because different scenarios warrant different code, but they remain there just in case. Below is the code snippet needed to geocode.


# Initialize Google Maps client with API key
gmaps = googlemaps.Client(key='Your API Key')
#https://developers.google.com/maps/documentation/javascript/cloud-setup


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

If you wish to add this to your current data frame and save it so you don't have to geocode the same items multiple times, see below.


latitudes = [lat for lat, lon in coordinates]
longitudes = [lon for lat, lon in coordinates]

df['latitudes'] = latitudes
df['longitudes'] = longitudes
# df.to_excel('Test.xlsx', engine="openpyxl")

If you do not with to use custom icons with base64, bootstrap icons also work.
