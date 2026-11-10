#rectificar el pk = 0

import sqlite3
import pandas as pd

conn = sqlite3.connect(r"data\semaforos.db")


print("--1ro Visto por pandas (PRAGMA)")
query_pragma = "PRAGMA table_info(semaforos);"
df_esquema = pd.read_sql_query(query_pragma, conn)
print(df_esquema[['name', 'pk']].to_string())


print("--2do con SQL (SQLITE_MASTER)--")
query_master = "SELECT sql FROM sqlite_master WHERE type ='table' AND name = 'semaforos'"
df_master = pd.read_sql_query(query_master, conn)
print(df_master['sql'].iloc[0])

print("--3er visto con indices (PRAGMA INDEX_LIST)")
query_indices = "PRAGMA index_list(semaforos)"
df_indices = pd.read_sql_query(query_indices, conn)
if df_indices.empty:
    print("no hay pk en la tabla")
else:
    print(df_indices.to_string())

conn.close()




