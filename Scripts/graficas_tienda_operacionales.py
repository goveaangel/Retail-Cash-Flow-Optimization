import pandas as pd
import matplotlib.pyplot as plt

# --- Cargar el archivo Excel ---
file_path = "resumen_costos_semanales_V2.xlsx"  # Asegúrate de que esté en el mismo directorio
df = pd.read_excel(file_path)

# --- Eliminar fila de totales si existe ---
df = df[df["tienda"] != "Costos_Columna"]
df.reset_index(drop=True, inplace=True)

# --- Seleccionar columnas de cobros operacionales ---
cols_operacionales = [col for col in df.columns if "cobros_operaciones_" in col]

# --- Calcular costo operacional total por tienda ---
df["costo_total_operacional"] = df[cols_operacionales].sum(axis=1)

# --- Graficar ---
plt.figure(figsize=(14, 6))
plt.bar(df["tienda"].astype(str), df["costo_total_operacional"], color='mediumseagreen')
plt.title("Costo total operacional semanal por tienda")
plt.xlabel("Tienda")
plt.ylabel("Costo total ($)")
plt.xticks(rotation=90)
plt.tight_layout()
plt.grid(axis='y')
plt.show()
