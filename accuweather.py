import json
import requests

import matplotlib.pyplot as plt

lat, lon = 42.362389, -71.091083

# AccuWeather API
accu_api_key = "xmhcAfLZUOq4TI8MZ3X74GgOvxxq3cgg"

search_params = {
    'apikey': accu_api_key,
    'q': "{:.4f},{:.4f}".format(lat, lon)
}

location = json.loads(requests.get("http://dataservice.accuweather.com/locations/v1/cities/geoposition/search", params=search_params).content)
location_key = int(location['Key'])

print(location)
