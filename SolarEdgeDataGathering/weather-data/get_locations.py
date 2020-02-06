import googlemaps
import json

API_KEY = ''
gmaps = googlemaps.Client(key=API_KEY)

with open("../site_information.json") as f:
    json_data = json.load(f)

locations = {}
for site in json_data["sites"]["site"]:
    site_id = site["id"]
    loc = site["location"]
    location_string = f"{loc['address']}, {loc['city']}, {loc['stateCode']}, {loc['zip']}"
    geocode_results = gmaps.geocode(location_string)

    geocode_result = geocode_results[0]
    lat_lng = geocode_result['geometry']['location']
    locations[site_id] = lat_lng

with open('locations.csv', "w+") as f:
    f.write(f"id,lat,long\n")
    for site_id, loc in locations.items():
        f.write(f"{site_id},{loc['lat']},{loc['lng']}\n")
