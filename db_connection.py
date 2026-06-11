import psycopg2

def get_connection():

    conn = psycopg2.connect(
        host="localhost",
        database="my_data_base",
        user="postgres",
        password="1127"
    )

    return conn