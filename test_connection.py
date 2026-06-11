from db_connection import get_connection

conn = get_connection()

print("DATABASE CONNECTED SUCCESSFULLY")

conn.close()

