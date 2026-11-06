import psycopg

def get_connection():
    return psycopg.connect(
        host="postgres",
        port=5432,
        dbname="weather_db",
        user="weather_user",
        password="weather_password"
    )
