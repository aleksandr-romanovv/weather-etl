def transform_batch(conn, batch_id):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TEMP TABLE weather_temp AS
            SELECT
	            id AS staging_id,
	            batch_id,
                raw_data,
                raw_data->>'city' AS city,
                raw_data->>'time' AS time,
                raw_data->>'temperature' AS temperature,
                raw_data->>'humidity' AS humidity,
                raw_data->>'wind_speed' AS wind_speed
            FROM staging.weather_raw wr 
            WHERE jsonb_typeof(raw_data) = 'object' and batch_id = %s;
        """, (batch_id,))

        cur.execute("""
            CREATE TEMP TABLE weather_validated AS
            SELECT
                *,
                CASE
                    WHEN city IS NULL OR TRIM(city) = ''
                        THEN 'Missing city'

                    WHEN time IS NULL OR TRIM(time) = ''
                        THEN 'Missing time'

                    WHEN temperature IS NULL
                        THEN 'Missing temperature'

                    WHEN humidity IS NULL
                        THEN 'Missing humidity'

                    WHEN wind_speed IS NULL
                        THEN 'Missing wind speed'
                    
                    WHEN NOT pg_input_is_valid(time, 'timestamp with time zone')
                        THEN 'Invalid time format'

                    WHEN humidity !~ '^-?[0-9]+(\.[0-9]+)?$'
                        THEN 'Invalid humidity format'

                    WHEN wind_speed !~ '^-?[0-9]+(\.[0-9]+)?$'
                        THEN 'Invalid wind speed format'

                    WHEN temperature !~ '^-?[0-9]+(\.[0-9]+)?$'
                        THEN 'Invalid temperature format'

                    WHEN humidity::NUMERIC < 0 OR humidity::NUMERIC > 100
                        THEN 'Humidity out of range'

                    WHEN temperature::NUMERIC < -100 or temperature::NUMERIC > 100
                        THEN 'Temperature out of range'

                    WHEN wind_speed::NUMERIC < 0
                        THEN 'Negative wind speed'

                    ELSE NULL
                END AS error_reason
            FROM weather_temp;
        """)

        cur.execute("""
            INSERT INTO analytics.weather (
                batch_id,
                city,
                time,
                temperature,
                humidity,
                wind_speed
            )
            SELECT
                batch_id,
                city,
                time::TIMESTAMPTZ,
                temperature::NUMERIC,
                humidity::NUMERIC,
                wind_speed::NUMERIC
            FROM weather_validated
            WHERE error_reason IS NULL
            ON CONFLICT (city, time)
            DO UPDATE SET
                temperature = EXCLUDED.temperature,
                humidity = EXCLUDED.humidity,
                wind_speed = EXCLUDED.wind_speed,
                batch_id = EXCLUDED.batch_id,
                loaded_at = NOW();
        """)

        cur.execute("""
            INSERT INTO analytics.weather_invalid (
                batch_id,
                raw_data,
                error_reason
            )
            SELECT
                batch_id,
                raw_data,
                error_reason
            FROM weather_validated
            WHERE error_reason IS NOT NULL;
        """)

        cur.execute("""
            DELETE FROM staging.weather_raw
            WHERE batch_id = %s;
        """, (batch_id,))