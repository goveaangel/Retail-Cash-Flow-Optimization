import pandas as pd
import numpy as np
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpBinary, LpStatus, PULP_CBC_CMD

def ejecutar_modelo_dia(path="/Users/angelgovea/Library/CloudStorage/OneDrive-InstitutoTecnologicoydeEstudiosSuperioresdeMonterrey/4to Semestre/Optimizacion Determinista/Coppel/Data/resumen_tiendas_lunes.csv"):
        

    # =====================
    # Cargar datos
    # =====================
    resumen = pd.read_csv(path)
    tiendas_unicas = resumen["tienda"].tolist()
    tienda_to_idx = {tienda: idx for idx, tienda in enumerate(tiendas_unicas)}
    idx_to_tienda = {idx: tienda for tienda, idx in tienda_to_idx.items()}
    n_tiendas = len(tiendas_unicas)

    D0 = resumen["dinero_inicial"].values
    ROP = resumen["rop"].values
    PO = resumen["po"].values
    MINIMO_OPERACION = 8800
    margen_exceso = 10000  # tolerancia permitida por encima del PO sin penalizar

    # =====================
    # Modelo
    # =====================
    model = LpProblem("Minimizar_Costo_Transporte", LpMinimize)

    # Distancias reales desde CSV
    df_distancias = pd.read_csv("/Users/angelgovea/Library/CloudStorage/OneDrive-InstitutoTecnologicoydeEstudiosSuperioresdeMonterrey/4to Semestre/Optimizacion Determinista/Coppel/Data/distancias_tiendas_completas.csv")

    # Inicializar matriz con infinito para detectar errores fácilmente
    distancia = np.full((n_tiendas, n_tiendas), np.inf)

    # Llenar la matriz con las distancias reales
    for _, row in df_distancias.iterrows():
        origen = row["origen"]
        destino = row["destino"]
        if origen in tienda_to_idx and destino in tienda_to_idx:
            i = tienda_to_idx[origen]
            j = tienda_to_idx[destino]
            distancia[i][j] = row["distancia_km"]

    # Validación opcional (puedes comentar si no lo necesitas)
    if np.any(np.isinf(distancia)):
        print("⚠️ Hay pares de tiendas sin distancia registrada.")

    # Distancias ficticias
    #np.random.seed(0)
    #distancia = np.random.randint(1, 30, size=(n_tiendas, n_tiendas))
    #np.fill_diagonal(distancia, 0)

    # Variables
    MAX_ENVIO = 100000
    x = [[LpVariable(f"x_{i}_{j}", lowBound=0) for j in range(n_tiendas)] for i in range(n_tiendas)]
    y = [[LpVariable(f"y_{i}_{j}", cat=LpBinary) for j in range(n_tiendas)] for i in range(n_tiendas)]
    D = [LpVariable(f"D_{i}", lowBound=0) for i in range(n_tiendas)]
    e = [LpVariable(f"exceso_{i}", lowBound=0) for i in range(n_tiendas)]
    f = [LpVariable(f"falta_{i}", lowBound=0) for i in range(n_tiendas)]

    # ---------------------
    # Función objetivo
    # ---------------------
    model += (
        lpSum((0.003 * x[i][j] / 1000) + (25 * distancia[i][j] * y[i][j])
            for i in range(n_tiendas) for j in range(n_tiendas) if i != j) +
        lpSum(0.00001 * e[i] for i in range(n_tiendas)) +
        lpSum(1 * f[i] for i in range(n_tiendas))
    )

    # ---------------------
    # Restricciones
    # ---------------------
    for i in range(n_tiendas):
        model += D[i] == D0[i] - lpSum(x[i][j] for j in range(n_tiendas) if j != i) + \
                            lpSum(x[j][i] for j in range(n_tiendas) if j != i)
        model += D[i] >= MINIMO_OPERACION
        model += D[i] <= 250000
        model += D[i] + f[i] >= PO[i]  # penalización si no se alcanza PO
        model += e[i] >= D[i] - PO[i] - margen_exceso  # penalizar solo si sobrepasa PO + margen
        model += e[i] >= 0

    # Activación de viajes
    for i in range(n_tiendas):
        for j in range(n_tiendas):
            if i != j:
                model += x[i][j] <= MAX_ENVIO * y[i][j]

    # =====================
    # Resolver
    # =====================
    model.solve(PULP_CBC_CMD(msg=False))
    print("Estado del modelo:", LpStatus[model.status])
    print(f"Costo total del modelo: ${round(model.objective.value(), 2)}")

    # =====================
    # Resultados de viajes
    # =====================
    viajes = []
    for i in range(n_tiendas):
        for j in range(n_tiendas):
            if i != j and x[i][j].varValue and x[i][j].varValue > 0:
                costo_envio = 0.003 * (x[i][j].varValue / 1000)
                costo_base = 25 * distancia[i][j] if y[i][j].varValue == 1 else 0
                costo_total = round(costo_envio + costo_base, 2)

                viajes.append({
                    "Desde": idx_to_tienda[i],
                    "Hacia": idx_to_tienda[j],
                    "Cantidad transferida": x[i][j].varValue,
                    "Distancia (km)": distancia[i][j],
                    "Costo del viaje": costo_total
                })

    viajes_df = pd.DataFrame(viajes)
    viajes_df.to_csv("viajes_penalizados.csv", index=False)

    """print("\n===== VIAJES =====")
    for v in viajes:
        print(f"📦 Viaje de tienda {v['Desde']} a tienda {v['Hacia']} | Transferido = {round(v['Cantidad transferida'], 2)}")"""

    # =====================
    # Resultados por tienda
    # =====================
    balance = []
    for i in range(n_tiendas):
        final = D[i].varValue if D[i].varValue is not None else 0
        po = PO[i]
        diff = final - po
        balance.append({
            "Tienda": idx_to_tienda[i],
            "Dinero Final": round(final, 2),
            "Punto Óptimo (PO)": round(po, 2),
            "Diferencia": round(diff, 2)
        })

    balance_df = pd.DataFrame(balance)
    balance_df.to_csv("balance_penalizado.csv", index=False)

    print("\n===== ANÁLISIS =====")
    print("\nTiendas que apenas cumplieron el PO:")
    print(balance_df[balance_df["Diferencia"] < 1e-2])

    """print("\nTiendas con exceso mayor a $10,000:")
    print(balance_df[balance_df["Diferencia"] > 10000])"""

    print("\nNúmero de tiendas que NO recibieron ningún viaje:")
    print(sum(balance_df["Diferencia"] == 0))

    costo_transporte = sum(
        (0.003 * x[i][j].varValue / 1000 + 25 * distancia[i][j] * y[i][j].varValue)
        for i in range(n_tiendas) for j in range(n_tiendas) if i != j
    )

    costo_exceso = sum(e[i].varValue for i in range(n_tiendas))
    costo_falta = sum(f[i].varValue for i in range(n_tiendas))

    print(f"\nCosto transporte: ${round(costo_transporte, 2)}")
    print(f"Costo exceso:     ${round(costo_exceso, 2)}")
    print(f"Costo por falta:  ${round(costo_falta, 2)}")
    print(f"Total modelo:     ${round(model.objective.value(), 2)}")
    dinero_final_series = pd.Series(
    {idx_to_tienda[i]: D[i].varValue for i in range(n_tiendas)},
    name="dinero_final"
    )

    return model.objective.value(), len(viajes), dinero_final_series 