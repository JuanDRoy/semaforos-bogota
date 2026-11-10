import pandas as pd
import sqlite3
from pathlib import Path

# 1. Definir rutas
RUTA_CSV = r"data\raw\Red_Semafórica._SDM._Bogotá_D.C..csv"
RUTA_DB = r"data\semaforos.db"

# 2. Leer el archivo CSV
# Ajusta el separador si tu CSV usa punto y coma (sep=';')
df = pd.read_csv(RUTA_CSV)

# 3. Mostrar las columnas para identificar los campos de interés
print("Columnas del dataset:", df.columns.tolist())
print("\nPrimeras filas:")
print(df.head())

# 4. Crear la conexión a SQLite (el archivo .db se crea si no existe)
conn = sqlite3.connect(RUTA_DB)

# 5. Cargar el DataFrame a una tabla llamada 'semaforos'
# 'if_exists="replace"' reemplaza la tabla si ya existe (útil para pruebas)
df.to_sql("semaforos", conn, if_exists="replace", index=False)

#chequeo de integidad en la información
filas_originales = len(df)

cursor = conn.cursor()
cursor.execute("SELECT COUNT (*) FROM semaforos")
filas_db = cursor.fetchone()[0]

if filas_originales == filas_db:
    print(f"no hay perdida \n filas en CSV ={filas_originales} | filas en db {filas_db} ")
else:
    print(f"filas en CSV = {filas_originales} | filas en db= {filas_db}")

conn.close()
print(f"\n Datos cargados en la base de datos: {RUTA_DB}")