import sqlite3
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

#conección de datos 
conn = sqlite3.connect(r"data\semaforos.db")
cols = ['OPERACIONACTUAL', 'FUNCIONAMIENTO', 'IMPLEMENTACION', 'UBICACIONEQUIPO']
df = pd.read_sql_query("SELECT OPERACIONACTUAL, X, Y FROM semaforos", conn)
df_2 = pd.read_sql_query(f"SELECT {', '.join(cols)} FROM semaforos;", conn)
df_tiempo = pd.read_sql_query("SELECT X, Y, FECHAINSTALACION FROM semaforos", conn)
conn.close()

#1ra analisis: estado

total = len(df)
total_2 = len(df_2)


print(f" \n --- Total de semaforos = {total_2}u ---")


conteo = df['OPERACIONACTUAL'].value_counts(dropna = False)

df_resumen = pd.DataFrame({
    '(Cantidad)': conteo,
    'porcentual': (conteo/total *100).round(3)
})
print(df_resumen)
print("--------------------------------------------------------")


#2. consolidar porcentajes de categorias. 

#paso de columnas a filas (melt)
df_largo = df_2.melt(var_name = 'variable', value_name = 'categoria')

#agrupo y cuento (groupby)
df_conteo = df_largo.groupby(['variable', 'categoria']).size().reset_index(name = 'cantidad')

# % 
df_conteo['porcentual'] = (df_conteo['cantidad']/ total_2 *100).round(3)



print(df_conteo.to_string(index = False))

print("--------------------------------------------------------")



#--- 3.Distancias ---

#forma global 
df_geo = df.dropna(subset = ['X', 'Y'])
lat = np.radians(df_geo['Y'].values)
lon = np.radians(df_geo['X'].values)

    #se necesita hacer un broadcasting para hacer mach entre las matrices 
dlat = lat[:, None] - lat
dlon = lon[:, None] - lon 

    #Al ser puntos en un circulo (Nos movemos por radios) aplico fórmula de semiverseno (Haversine)

a = np.sin(dlat/2)**2 + np.cos(lat[:, None]) * np.cos(lat) * np.sin(dlon/2)**2
dis_matrix = 6371000  * 2 * np.arcsin(np.sqrt(a)) #cte radio de la tierra

    #triangulo superor (evitar duplicados y ceros)
i, j = np.triu_indices_from(dis_matrix, k = 1)
distancias = dis_matrix[i, j]

#vecinos mas cercanos
n= len(lat)
infitno= np.eye(n)* 1e9

vecinos_cercanos = np.min(dis_matrix + infitno, axis = 1 )

print(f"" )



print(
    f"""
 Distancia promedio al semaforo más cercano por vecinos: {vecinos_cercanos.mean():.3f}m ó {vecinos_cercanos.mean()/1000:.3f}km \n    
 Distancia media entre semáforos: {distancias.mean():.3f}m ó {distancias.mean()/1000 :.3f}km  \n
 Promedio de distancia entre más cercanos: {distancias.min():.3f}m  ó {distancias.min()/1000:.3f}km \n
 Promedio de distancia entre más lejanos: {distancias.max():.3f}m ó {distancias.max() / 1000 :.3f}km 
 --------------------------------------------------------
""")


ruta_carpeta = Path("data/process")
ruta_carpeta.mkdir(parents = True, exist_ok = True)

#4 antiguedad 

df_tiempo['antiguedad'] = pd.to_datetime(df_tiempo['FECHAINSTALACION'], errors = 'coerce').dt.year
df_tiempo = df_tiempo.dropna(subset =['antiguedad', 'X', 'Y'])




# VISUALIZACIÓN

# 2. Crear el gráfico
plt.figure(figsize=(10, 6))
plt.hist(vecinos_cercanos, bins=50, color='skyblue', edgecolor='black')
plt.title('Distribución de distancia al semáforo más cercano (vecinos) (Bogotá D.C)')
plt.xlabel('Distancia (m)')
plt.ylabel('Frecuencia (cantidad de semáforos)')
plt.grid(axis='y', alpha=0.75)
ruta_imagen = ruta_carpeta / "histograma_distancias.png"
plt.savefig(ruta_imagen, dpi=300, bbox_inches='tight')
plt.show()

# DataFrame auxiliar solo para el mapa, uniendo X, Y y UBICACIONEQUIPO
df_mapa = df.copy()
df_mapa['UBICACIONEQUIPO'] = df_2['UBICACIONEQUIPO']

plt.figure(figsize=(10, 10))

df_si = df_mapa[df_mapa['UBICACIONEQUIPO'] == 'SI']
df_no = df_mapa[df_mapa['UBICACIONEQUIPO'] == 'NO']

plt.scatter(df_si['X'], df_si['Y'], c='#4C72B0', label='SI (En la intersección)', 
            s=15, alpha=0.7, edgecolors='none')
plt.scatter(df_no['X'], df_no['Y'], c='#DD8452', label='NO (Fuera de la intersección)', 
            s=15, alpha=0.9, edgecolors='none')

plt.title('Ubicación Geográfica de los Equipos Semafóricos (Bogotá D.C.)', fontsize=14, pad=15)
plt.xlabel('Longitud (X)', fontsize=12)
plt.ylabel('Latitud (Y)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3)

plt.legend(loc='best', markerscale=2, frameon=True, fontsize=11)
ruta_mapa_ubicacion = ruta_carpeta / "mapa_ubicacion_equipo.png"
plt.savefig(ruta_mapa_ubicacion, dpi=300, bbox_inches='tight')
print(f" Mapa de ubicación guardado en: {ruta_mapa_ubicacion}")
plt.show()

# RADIENTE DE DISTANCIAS
plt.figure(figsize=(10, 10))

scatter_dist = plt.scatter(df_geo['X'], df_geo['Y'], c=vecinos_cercanos, 
                           cmap='plasma', s=15, alpha=0.8, edgecolors='none')

# Barra de color
cbar = plt.colorbar(scatter_dist)
cbar.set_label('Distancia al semáforo más cercano (m)', fontsize=12)

plt.title('Gradiente de Distancia al Semáforo Más Cercano (Bogotá D.C.)', fontsize=14, pad=15)
plt.xlabel('Longitud (X)', fontsize=12)
plt.ylabel('Latitud (Y)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3)

ruta_gradiente = ruta_carpeta / "mapa_gradiente_distancias.png"
plt.savefig(ruta_gradiente, dpi=300, bbox_inches='tight')
print(f" Mapa de gradiente guardado en: {ruta_gradiente}")
plt.show()


# VISUALIZACIÓN: MAPA DE OPERACIÓN ACTUAL

plt.figure(figsize=(10, 10))

# Filtramos usando las variables que ya existentes
df_normal = df[df['OPERACIONACTUAL'] == 'NORMAL']
df_pmt = df[df['OPERACIONACTUAL'] == 'PMT']
df_desvio = df[df['OPERACIONACTUAL'] == 'Desvío - PMT']

plt.scatter(df_normal['X'], df_normal['Y'], c='#55A868', label='NORMAL', 
            s=15, alpha=0.7, edgecolors='none')
plt.scatter(df_pmt['X'], df_pmt['Y'], c='#DD8452', label='PMT', 
            s=15, alpha=0.9, edgecolors='none')
plt.scatter(df_desvio['X'], df_desvio['Y'], c='#C44E52', label='Desvío - PMT', 
            s=15, alpha=0.9, edgecolors='none')

plt.title('Mapa de Operación Actual de los Semáforos (Bogotá D.C.)', fontsize=14, pad=15)
plt.xlabel('Longitud (X)', fontsize=12)
plt.ylabel('Latitud (Y)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3)

plt.legend(loc='best', markerscale=2, frameon=True, fontsize=11)

ruta_operacion = ruta_carpeta / "mapa_operacion_actual.png"
plt.savefig(ruta_operacion, dpi=300, bbox_inches='tight')
print(f" Mapa de operación guardado en: {ruta_operacion}")
plt.show()

# Graficamos el gradiente antuguedad
plt.figure(figsize=(10, 10))

scatter_tiempo = plt.scatter(df_tiempo['X'], df_tiempo['Y'], c=df_tiempo['antiguedad'], 
                             cmap='viridis', s=15, alpha=0.8, edgecolors='none')

cbar = plt.colorbar(scatter_tiempo)
cbar.set_label('Año de Instalación (Antigüedad)', fontsize=12)

plt.title('Gradiente de Antigüedad de los Semáforos (Bogotá D.C.)', fontsize=14, pad=15)
plt.xlabel('Longitud (X)', fontsize=12)
plt.ylabel('Latitud (Y)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3)

ruta_antiguedad = ruta_carpeta / "mapa_gradiente_antiguedad.png"
plt.savefig(ruta_antiguedad, dpi=300, bbox_inches='tight')
print(f" Mapa de antigüedad guardado en: {ruta_antiguedad}")
plt.show()

#torta
plt.figure(figsize=(8, 8))
labels = df_resumen.index
sizes = df_resumen['(Cantidad)']
colores_torta = ['#55A868', '#DD8452', '#C44E52']

# Graficamos la torta
plt.pie(sizes, 
        labels=labels, 
        colors=colores_torta,
        autopct='%1.2f%%', # Muestra el porcentaje con dos decimales
        startangle=90,     # Inicia el gráfico desde arriba
        wedgeprops={'edgecolor': 'black', 'linewidth': 1}) # Borde negro para separar porciones

plt.title('Distribución de Operación Actual de los Semáforos (Bogotá D.C.)', fontsize=14, pad=20)

ruta_torta = ruta_carpeta / "grafico_torta_operacion.png"
plt.savefig(ruta_torta, dpi=300, bbox_inches='tight')
print(f" Gráfico de torta guardado en: {ruta_torta}")
plt.show()

# GUARDAR EN TXT
ruta_txt = ruta_carpeta / "resultados_terminal.txt"

with open(ruta_txt, "w", encoding="utf-8") as f:
    f.write(f"--- Total de semaforos = {total_2}u ---\n\n")
    f.write(df_resumen.to_string() + "\n")
    f.write("--------------------------------------------------------\n")
    
    f.write(df_conteo.to_string(index=False) + "\n")
    f.write("--------------------------------------------------------\n")
    
    f.write(f"Distancia promedio al semaforo más cercano por vecinos: {vecinos_cercanos.mean():.3f}m\n")
    f.write(f"Distancia media entre semáforos: {distancias.mean():.3f}m ó {distancias.mean()/1000 :.3f}km\n")
    f.write(f"Promedio de distancia entre más cercanos: {distancias.min():.3f}m ó {distancias.min()/1000:.3f}km\n")
    f.write(f"Promedio de distancia entre más lejanos: {distancias.max():.3f}m ó {distancias.max() / 1000 :.3f}km\n")
