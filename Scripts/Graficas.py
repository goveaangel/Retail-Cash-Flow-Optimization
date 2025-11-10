import pandas as pd
import matplotlib.pyplot as plt

# --- Cargar archivo Excel ---
file_path = "resumen_costos_semanales_V2.xlsx"  # Cambia ruta si está en otro directorio
df = pd.read_excel(file_path)

# --- Eliminar fila de totales si existe ---
df = df[df["tienda"] != "Costos_Columna"]

# --- Identificar columnas de costos de viaje ---
cols_costos_viaje = [col for col in df.columns if "costo_viaje_" in col]

# --- Sumar los costos por día ---
costos_por_dia = df[cols_costos_viaje].sum()

# --- Gráfico de barras ---
plt.figure(figsize=(10, 6))
costos_por_dia.plot(kind='bar', color='steelblue')
plt.title("Costo total de viaje por día")
plt.ylabel("Costo ($)")
plt.xlabel("Día de la semana")
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.show()        