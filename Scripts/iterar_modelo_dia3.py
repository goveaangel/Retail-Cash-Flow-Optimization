import pandas as pd
from modelo_dia import ejecutar_modelo_dia  # Esta función debe devolver: costo_total, viajes_realizados, dinero_final (como pd.Series)

# Cargar datos
flujo = pd.read_csv("/Users/angelgovea/Library/CloudStorage/OneDrive-InstitutoTecnologicoydeEstudiosSuperioresdeMonterrey/4to Semestre/Optimizacion Determinista/Coppel/Data/flujo_efectivo_semanal.csv")
resumen_lunes = pd.read_csv("/Users/angelgovea/Library/CloudStorage/OneDrive-InstitutoTecnologicoydeEstudiosSuperioresdeMonterrey/4to Semestre/Optimizacion Determinista/Coppel/Data/resumen_tiendas_lunes.csv")

# Aseguramos que tienda sea el índice
flujo.set_index("tienda", inplace=True)
resumen_lunes.set_index("tienda", inplace=True)

dias = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

# Inicializar con el dinero del lunes
dinero_final = resumen_lunes["dinero_inicial"].copy()

# Mínimo operativo
MINIMO_OPERACION = 8800

for dia in dias:
    print("👉 Dinero final del domingo:")
    print(dinero_final.sort_values(ascending=False))

    # Calcular la suma exacta usada:
    dinero_inicial = (dinero_final * 0.7) + flujo[f"entrada_{dia}"] - flujo[f"salida_{dia}"]
    print(f"✔️ Suma exacta (como en script): ${dinero_inicial.sum():,.2f}")
    entrada_col = f"entrada_{dia}"
    salida_col = f"salida_{dia}"

    # Definir entradas y salidas del día actual
    entradas = flujo[entrada_col]
    salidas = flujo[salida_col]

    # Si dinero_final no es un Series, convertirlo
    if not isinstance(dinero_final, pd.Series):
        dinero_final = pd.Series(dinero_final, index=flujo.index)

    # Aplicar 30% de transferencia electrónica
    dinero_inicial = (dinero_final * 0.7) + entradas - salidas
    dinero_inicial = dinero_inicial.clip(lower=0)  # No permitir negativos

    print("👉 Dinero final del domingo:")
    print(dinero_final.sort_values(ascending=False))

    # Calcular la suma exacta usada:
    dinero_inicial = (dinero_final * 0.7) + flujo[f"entrada_{dia}"] - flujo[f"salida_{dia}"]
    print(f"✔️ Suma exacta (como en script): ${dinero_inicial.sum():,.2f}")
    # Mostrar total de efectivo en circulación
    total_efectivo = dinero_inicial.sum()
    print(f"💰 Total efectivo circulando al inicio del día {dia.capitalize()}: ${total_efectivo:,.2f}")

    print(f"\n🗓️ Día: {dia.capitalize()}")
    for tienda, valor in dinero_inicial.items():
        if valor < MINIMO_OPERACION:
            print(f"⚠️  Tienda {tienda} tiene solo ${round(valor, 2)} (por debajo del mínimo operativo)")

    # Crear resumen diario
    resumen_dia = pd.DataFrame({
        "tienda": dinero_inicial.index,
        "dinero_inicial": dinero_inicial.values,
        "rop": resumen_lunes["rop"],
        "po": resumen_lunes["po"]
    })

    resumen_dia.to_csv("resumen_tiendas_dia.csv", index=False)

    try:
        costo_total, viajes_realizados, dinero_final = ejecutar_modelo_dia("resumen_tiendas_dia.csv")
        print(f"💸 Costo total: ${round(costo_total, 2)}")
        """print(f"📦 Viajes realizados: {viajes_realizados}")"""
    except Exception as e:
        print(f"❌ Error en {dia.capitalize()}: {e}")
        break