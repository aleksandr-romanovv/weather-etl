import requests
import pandas as pd
import time

url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
params = {"lat": 55.7558, "lon": 37.6173}
headers = {"User-Agent": "weather-etl/1.0 (educational project)"}
response = requests.get(url, params=params, headers=headers, timeout=15)
data = response.json()
weather_data = []

start_1 = time.perf_counter()
df = pd.json_normalize(data["properties"]["timeseries"])
end_1 = time.perf_counter()
time_1 = end_1 - start_1

start_2 = time.perf_counter()
for itm in data["properties"]["timeseries"]:
    weather_data.append({
        'time': itm["time"],
        'temperature': itm["data"]["instant"]["details"]["air_temperature"],
        'humidity': itm["data"]["instant"]["details"]["relative_humidity"],
        'wind_speed': itm["data"]["instant"]["details"]["wind_speed"]
    })
end_2 = time.perf_counter()
time_2 = end_2 - start_2

start_3 = time.perf_counter()
flat_list = [
    {
        'time': itm["time"],
        'temperature': itm["data"]["instant"]["details"]["air_temperature"],
        'humidity': itm["data"]["instant"]["details"]["relative_humidity"],
        'wind_speed': itm["data"]["instant"]["details"]["wind_speed"]
    }
    for itm in data["properties"]["timeseries"]
]
df_fast = pd.DataFrame(flat_list)
end_3 = time.perf_counter()
time_3 = end_3 - start_3

print(f"Способ 1 (json_normalize): {time_1:.6f} сек")
print(f"Способ 2 (Цикл for):       {time_2:.6f} сек")
print(f"Способ 3 (Гибридный):     {time_3:.6f} сек")