from psycopg.types.json import Jsonb

def stage_load(conn, batch_id, records):
    query = """
        insert into staging.weather_raw (batch_id, raw_data)
        values (%s, %s)
      """

    values = []
    for record in records:
        element = (batch_id, Jsonb(record))
        values.append(element)

    with conn.cursor() as cur:
        cur.executemany(query, values)