import json
import requests
from datetime import datetime, timedelta
import os


def try_get(key, container):

    if key in container:
        return str(container[key])
    else:
        return ""


def save_daily_data(weather_data, file):
    time = datetime.fromtimestamp(weather_data["time"])
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")

    output = [time_str]

    output.append(try_get("precipIntensity", weather_data))
    output.append(try_get("precipIntensityMax", weather_data))
    output.append(try_get("precipProbability", weather_data))
    output.append(try_get("precipAccumulation", weather_data))
    output.append(try_get("precipType", weather_data))
    output.append(try_get("temperatureHigh", weather_data))
    output.append(try_get("temperatureLow", weather_data))
    output.append(try_get("dewPoint", weather_data))
    output.append(try_get("humidity", weather_data))
    output.append(try_get("pressure", weather_data))
    output.append(try_get("windSpeed", weather_data))
    output.append(try_get("windBearing", weather_data))
    output.append(try_get("cloudCover", weather_data))
    output.append(try_get("uvIndex", weather_data))
    output.append(try_get("visibility", weather_data))
    output.append(try_get("ozone", weather_data))
    output.append(try_get("sunriseTime ", weather_data))
    output.append(try_get("sunsetTime ", weather_data))

    out_str = ",".join(output) + "\n"
    file.write(out_str)


def save_hourly_data(weather_data, file):
    time = datetime.fromtimestamp(weather_data["time"])
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")

    output = [time_str]

    output.append(try_get("precipIntensity", weather_data))
    output.append(try_get("precipProbability", weather_data))
    output.append(try_get("precipAccumulation", weather_data))
    output.append(try_get("precipType", weather_data))
    output.append(try_get("temperature", weather_data))
    output.append(try_get("apparentTemperature", weather_data))
    output.append(try_get("dewPoint", weather_data))
    output.append(try_get("humidity", weather_data))
    output.append(try_get("pressure", weather_data))
    output.append(try_get("windSpeed", weather_data))
    output.append(try_get("windBearing", weather_data))
    output.append(try_get("windGust", weather_data))
    output.append(try_get("cloudCover", weather_data))
    output.append(try_get("uvIndex", weather_data))
    output.append(try_get("visibility", weather_data))
    output.append(try_get("ozone", weather_data))

    out_str = ",".join(output) + "\n"
    file.write(out_str)


API_KEY = "abfe41114c64ca236e3443b9e6f7376a"
URL = "https://api.darksky.net/forecast/{}/{},{},{}"

lat_lng = {}
with open("locations.csv", "r") as f:
    next(f)
    for line in f:
        [location_id, lat, lng] = line.split(",")
        lat_lng[int(location_id)] = (float(lat), float(lng))

with open("../site_information.json") as f:
    site_info_json = json.load(f)
    sites = site_info_json["sites"]["site"]

for site in sites:
    start_date = datetime.strptime(site["installationDate"], "%Y-%m-%d")
    end_date = datetime.strptime(site["lastUpdateTime"], "%Y-%m-%d")
    site_id = site["id"]
    lat, lng = lat_lng[site_id]

    directory = site["name"]
    if not os.path.exists(directory):
        os.mkdir(directory)

    with open(f"{directory}/weather_data_hourly.csv", "w+") as file:
        file.write("date,precipIntensity,precipProbability,precipAccumulation,precipType,temperature,apparentTemperature,dewPoint,humidity,pressure,windSpeed,windBearing,windGust,cloudCover,uvIndex,visibility,ozone\n")

    with open(f"{directory}/weather_data_daily.csv", "w+") as file:
        file.write("date,precipIntensity,precipIntensityMax,precipProbability,precipAccumulation,precipType,temperatureHigh,temperatureLow,dewPoint,humidity,pressure,windSpeed,windBearing,cloudCover,uvIndex,visibility,ozone,sunriseTime,sunsetTime\n")

    n = 0
    current_date = start_date
    while current_date < end_date:

        print(n, current_date)

        date_format = current_date.strftime('%Y-%m-%d')
        time_format = current_date.strftime('%H:%M:%S')

        time_string = f"{date_format}T{time_format}"

        request_url = URL.format(API_KEY, lat, lng, time_string)

        response = requests.get(request_url)
        assert(response.status_code == 200)
        response_json = response.json()

        with open(f"{directory}/weather_data_hourly.csv", "a") as file:
            hourly_weather_data = response_json["hourly"]["data"]

            for weather_data in hourly_weather_data:
                save_hourly_data(weather_data, file)

        with open(f"{directory}/weather_data_daily.csv", "a") as file:
            daily_weather_data = response_json["daily"]["data"][0]
            save_daily_data(daily_weather_data, file)

        current_date = current_date + timedelta(days=1)
