import sqlite3
import pandas as pd

conn = sqlite3.connect(r"data/semaforos.db")

"""
# ---manejo con for---
#distribucion de la tabla
cursor = conn.cursor()
cursor.execute("PRAGMA  table_info(semaforos);")
 
columnas = cursor.fetchall()
for col in columnas:
    print(col)

conn.close()
"""

#manejom con pandas 
query = "PRAGMA table_info(semaforos);"

df_esquema = pd.read_sql_query(query,conn)

print(df_esquema.to_string())

conn.close()


