# Weather ETL

An educational ETL project for collecting, processing, and storing weather forecast data in PostgreSQL.

The project retrieves weather forecast data from the [MET Norway API](https://api.met.no/weatherapi/locationforecast/2.0/documentation), loads raw data into a staging layer, validates and transforms it, and stores the results in an analytical table.

## Tech Stack

- **Python 3.14** — data extraction and processing
- **PostgreSQL 17** — data storage
- **Psycopg 3** — PostgreSQL connectivity
- **Requests** — HTTP requests to the weather API
- **Docker** — application containerization
- **Docker Compose** — multi-container orchestration

## ETL Pipeline

The pipeline consists of three main stages:

1. **Extract** — retrieves weather forecast data from the MET Norway API for five cities: Moscow, Saint Petersburg, Kazan, Novosibirsk, and Yekaterinburg.
2. **Load** — stores raw API responses in the `staging.weather_raw` table as JSONB.
3. **Transform** — validates the data, converts values to appropriate data types, and loads valid records into the analytical layer.

## Database Design

The database contains two schemas:

- `staging` — stores raw data received from the API.
- `analytics` — stores validated and transformed data.

### Main Tables

| Table | Description |
|---|---|
| `staging.weather_raw` | Raw API responses stored as JSONB |
| `analytics.weather` | Validated and transformed weather data |
| `analytics.weather_invalid` | Records that failed validation |

### Data Validation and Transformation

The transformation process includes:

- Checking required fields.
- Validating numeric formats.
- Checking valid ranges for temperature, humidity, and wind speed.
- Separating valid and invalid records.
- Converting values to PostgreSQL data types.

The `analytics.weather` table uses a unique constraint on `(city, time)` to prevent duplicate forecast records.

When a record with the same city and forecast time already exists, its values are updated using `INSERT ... ON CONFLICT DO UPDATE`.

After successful transformation, raw records belonging to the processed batch are deleted from the staging table.

## Project Structure

```text
weather-etl/
├── sql/
│   ├── create-schemas.sql
│   └── create_tables.sql
├── src/
│   ├── database.py
│   ├── load.py
│   ├── main.py
│   └── transform.py
├── tests/
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Docker Desktop
- Git

### Run the Project

Clone the repository:

```bash
git clone <repository-url>
cd weather-etl
```

Build the Docker image and start the containers:

```bash
docker compose up --build
```

Docker Compose starts PostgreSQL, waits until the database is healthy, and then runs the ETL pipeline.

Once the ETL process finishes successfully, its container exits with code `0`. This is expected behavior because the pipeline runs once and then terminates.

### Stop the Containers

```bash
docker compose down
```

PostgreSQL data is persisted in the Docker volume `postgres_data`.

**Note:** Running `docker compose down -v` removes the volume and deletes the persisted database data.

## Project Results

The project demonstrates:

- Extracting weather forecast data from an external REST API.
- Loading raw data into a PostgreSQL staging layer.
- SQL-based data validation and transformation.
- Separating valid and invalid records.
- Implementing an upsert strategy to prevent duplicate records.
- Running an ETL pipeline using Docker Compose.

## Author

Educational project focused on Data Engineering.