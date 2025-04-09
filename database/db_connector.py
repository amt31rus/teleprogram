import psycopg2

def connect_to_database():
    conn = psycopg2.connect(
        dbname="tvguide",
        user='postgres',
        password="postgres",
        host="localhost",
        port="5432"
    )
    return conn

def create_program_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS oldtvprogram (
            id SERIAL PRIMARY KEY,
            current_program VARCHAR(255),
            program_datetime TIMESTAMP,
            program_description TEXT
        )
    """)
    conn.commit()
    cur.close()
