import psycopg2

from settings import Credentials


def db_connection():
    conn = psycopg2.connect(
        host=Credentials.host,
        user=Credentials.username,
        password=Credentials.password,
        database=Credentials.database
    )
    return conn
