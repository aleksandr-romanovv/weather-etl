CREATE TABLE IF NOT EXISTS staging.weather_raw (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id UUID NOT NULL,
    raw_data JSONB NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analytics.weather (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id UUID NOT NULL,
    city TEXT NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    temperature NUMERIC(5, 2),
    humidity NUMERIC(5, 2),
    wind_speed NUMERIC(5, 2),
    loaded_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_weather_city_time UNIQUE (city, time)
);

CREATE TABLE IF NOT EXISTS analytics.weather_invalid (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    batch_id UUID NOT NULL,
    raw_data JSONB NOT NULL,
    error_reason TEXT NOT NULL,
    loaded_at TIMESTAMPTZ DEFAULT NOW()
);