import requests
from uuid import uuid4

from database import get_connection
from load import stage_load
from transform import transform_batch

url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
headers = {
    "User-Agent": "weather-etl/1.0 (educational project)"
}
cities = [
    {'city': 'Moscow', 'lat': 55.7558, 'lon': 37.6173},
    {'city': 'Saint Petersburg', 'lat': 59.9343, 'lon': 30.3351},
    {'city': 'Kazan', 'lat': 55.7961, 'lon': 49.1064},
    {"city": "Novosibirsk", "lat": 55.0084, "lon": 82.9357},
    {'city': 'Yekaterinburg', 'lat': 56.8389, 'lon': 60.6057},
]

def data_from_api(data, city):
    for itm in data["properties"]["timeseries"]:
        time = itm["time"]
        temperature = itm["data"]["instant"]["details"]["air_temperature"]
        humidity = itm["data"]["instant"]["details"]["relative_humidity"]
        wind_speed = itm["data"]["instant"]["details"]["wind_speed"]
        
        yield{
            'city': city,
            'time':time,
            'temperature':temperature,
            'humidity':humidity,
            'wind_speed':wind_speed
        }

batch_id = uuid4()
batch_size = 100
batch = []

with get_connection() as conn:
    print("Подключение к PostgreSQL успешно!")
    batch = []
    for city in cities:
        params = {
        "lat": city["lat"],
        "lon": city["lon"],
        }
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json() 

        print(f"Получены данные для {city['city']}")

        for record in data_from_api(data, city['city']):
            batch.append(record)
            if len(batch) >= batch_size:
                stage_load(conn, batch_id, batch)
                batch = []
    if batch:
        stage_load(conn, batch_id, batch)

    print('Загрузка завершена!')
    transform_batch(conn, batch_id)
    print('Трансформация завершена!')