from pulp import LpProblem, LpVariable, LpMinimize, lpSum, value
import pandas as pd

# --- PARÁMETROS GLOBALES ---
COSTO_POR_KM = 25
SEGURO_POR_1000 = 3
MAXIMO_POR_VIAJE = 100_000
COSTO_RECOLECCION = 0.005
COSTO_ABONOS = 0.005
COSTO_TRANSFERENCIA = 0.001
VENTA_ELECTRONICA = 0.30
LIMITE_EFECTIVO_TIENDA = 250_000

# --- CARGA DE DATOS ---
distancias_df = pd.read_csv("distanciasCoppel.csv")
entradas_df = pd.read_csv("entradas_salidas_Coppel.csv")
tiendas_df = pd.read_csv("tiendasCoppel.csv")

entradas_df["tienda"] = entradas_df["num_tie"].astype(str)
distancias_df["origen"] = distancias_df["origen"].astype(str)
distancias_df["destino"] = distancias_df["destino"].astype(str)
tiendas_df["tienda"] = tiendas_df["TiendaCodigo"].astype(str)

# Inicializamos el dinero inicial con 0 para todas las tiendas
dinero_inicial_df = pd.DataFrame({
    "tienda": entradas_df["tienda"],
    "dinero_inicial": [0] * len(entradas_df)
})

# --- FUNCION PRINCIPAL ---
def funcion_min(dia, df, distancias_df, dinero_inicial_df):
    col_abonos = f"{dia}_abonos"
    col_ventas = f"{dia}_venta_efectivo"
    col_salidas = f"{dia}_salidas"

    df = df.merge(dinero_inicial_df, on="tienda", how="left").fillna(0)
    df["cobros_operaciones"] = 0.0
    df["efectivo_en_tienda"] = 0.0
    df["necesita_reposicion"] = False
    df["rop"] = df.get("rop", 0)

    for i, row in df.iterrows():
        ventas = row[col_ventas]
        abonos = row[col_abonos]
        salidas = row[col_salidas]
        efectivo_previo = row["dinero_inicial"]
        rop = row["rop"]

        transferencia = ventas * VENTA_ELECTRONICA
        comision_transferencia = transferencia * COSTO_TRANSFERENCIA
        comision_abonos = abonos * COSTO_ABONOS

        efectivo_actual = efectivo_previo + abonos + (ventas*0.7) - salidas
        margen_inferior = 0
        margen_superior = rop + 10000
        necesita = margen_inferior <= efectivo_actual <= margen_superior

        df.at[i, "cobros_operaciones"] = comision_transferencia + comision_abonos
        df.at[i, "efectivo_en_tienda"] = efectivo_actual
        df.at[i, "necesita_reposicion"] = necesita

    receptoras = df[df["necesita_reposicion"]]
    donadoras = df[df["efectivo_en_tienda"] > LIMITE_EFECTIVO_TIENDA]

    if not receptoras.empty and not donadoras.empty:
        prob = LpProblem("MinCostoReposicion", LpMinimize)
        decisiones = {}

        for _, rec in receptoras.iterrows():
            for _, don in donadoras.iterrows():
                key = (don["tienda"], rec["tienda"])
                if not distancias_df[(distancias_df["origen"] == key[0]) & (distancias_df["destino"] == key[1])].empty:
                    decisiones[key] = LpVariable(f"x_{key[0]}_{key[1]}", lowBound=0)

        prob += lpSum([
            (distancias_df[(distancias_df["origen"] == don) & (distancias_df["destino"] == rec)]["distancia_km"].values[0] * COSTO_POR_KM +
             COSTO_TRANSFERENCIA * decisiones[(don, rec)]) * decisiones[(don, rec)]
            for (don, rec) in decisiones
        ])

        for _, rec in receptoras.iterrows():
            requerido = rec["rop"] - rec["efectivo_en_tienda"]
            prob += lpSum([decisiones[(don["tienda"], rec["tienda"])] for _, don in donadoras.iterrows() if (don["tienda"], rec["tienda"]) in decisiones]) == requerido

        for _, don in donadoras.iterrows():
            excedente = don["efectivo_en_tienda"] - LIMITE_EFECTIVO_TIENDA
            prob += lpSum([decisiones[(don["tienda"], rec["tienda"])] for _, rec in receptoras.iterrows() if (don["tienda"], rec["tienda"]) in decisiones]) <= excedente

        prob.solve()

        for (don, rec), var in decisiones.items():
            cantidad = value(var)
            if cantidad and cantidad > 0:
                df.loc[df["tienda"] == don, f"transfiere_a_{rec}"] = cantidad
                df.loc[df["tienda"] == rec, f"recibe_de_{don}"] = cantidad

    return df

# --- FUNCION PARA MANEJAR EXCEDENTES ---
def manejar_excedentes(resultado_df, distancias_df, tiendas_df, dia):
    from pulp import LpProblem, LpVariable, LpMinimize, lpSum, value
    from math import ceil
    import pandas as pd

    df = resultado_df.merge(tiendas_df[["tienda", "TipoTienda"]], on="tienda", how="left")
    df["excedente"] = df["efectivo_en_tienda"] - LIMITE_EFECTIVO_TIENDA
    df["excedente"] = df["excedente"].apply(lambda x: x if x > 0 else 0)
    costos_transportes = []

    # Tiendas Coppel transfieren directamente
    for i, row in df[df["TipoTienda"] == "coppel"].iterrows():
        excedente = row["excedente"]
        if excedente > 0:
            costo_transferencia = excedente * COSTO_TRANSFERENCIA
            df.at[i, "cobros_operaciones"] += costo_transferencia
            df.at[i, "efectivo_en_tienda"] -= excedente

    donadoras = df[(df["TipoTienda"] == "no_coppel") & (df["excedente"] > 0)]
    receptoras = df[df["TipoTienda"] == "coppel"]

    if not donadoras.empty and not receptoras.empty:
        prob = LpProblem("Minimizar_Excedentes", LpMinimize)
        decisiones = {}

        for _, don in donadoras.iterrows():
            origen = don["tienda"]
            max_envio = don["excedente"]
            num_viajes = ceil(max_envio / MAXIMO_POR_VIAJE)

            for _, rec in receptoras.iterrows():
                destino = rec["tienda"]
                dist_row = distancias_df[(distancias_df["origen"] == origen) & (distancias_df["destino"] == destino)]

                if not dist_row.empty:
                    distancia = dist_row["distancia_km"].values[0]

                    for v in range(num_viajes):
                        var_name = f"x_{origen}_{destino}_v{v}"
                        var = LpVariable(var_name, lowBound=0, upBound=MAXIMO_POR_VIAJE)
                        decisiones[(origen, destino, v)] = (var, distancia)

        prob += lpSum([
            distancia * COSTO_POR_KM * var + (var / 1000) * SEGURO_POR_1000 
            for (o, d, v), (var, distancia) in decisiones.items()
            if (o, d, v) in decisiones
        ])

        for _, don in donadoras.iterrows():
            origen = don["tienda"]
            max_envio = don["excedente"]
            prob += lpSum([
                var for (o, _, _), (var, _) in decisiones.items() if o == origen
            ]) == max_envio

        prob.solve()

        for (o, d, v), (var, distancia) in decisiones.items():
            monto = value(var)
            if monto and monto > 0:
                costo = distancia * COSTO_POR_KM + ((monto / 1000) * SEGURO_POR_1000) + (monto * COSTO_RECOLECCION)
                df.loc[df["tienda"] == o, "efectivo_en_tienda"] -= monto

                costos_transportes.append({
                    "dia": dia,
                    "origen": o,
                    "destino": d,
                    "viaje": v + 1,
                    "monto_transportado": monto,
                    "costo_viaje": costo,
                    "distancia_recorrida": distancia
                })

    # Guardar costos de transporte para este día
    if costos_transportes:
        pd.DataFrame(costos_transportes).to_csv(f"costos_transporte_{dia.lower()}.csv", index=False)
    return df.drop(columns=["TipoTienda", "excedente"])

# --- DÍAS DE LA SEMANA A PROCESAR ---
dias_semana = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- ITERACIÓN POR CADA DÍA ---
for i, dia in enumerate(dias_semana):
    print(f"\nProcesando día: {dia}")
    
    # Ejecutamos la función principal para el día actual
    resultado_dia = funcion_min(dia, entradas_df, distancias_df, dinero_inicial_df)
    
    # Manejo de excedentes
    resultado_dia = manejar_excedentes(resultado_dia, distancias_df, tiendas_df, dia)
    
    # Seleccionamos columnas útiles para el resultado
    columnas_utiles = ["tienda", "efectivo_en_tienda", "cobros_operaciones", "necesita_reposicion", "rop", "punto_optimo"]
    columnas_utiles += [col for col in resultado_dia.columns if col.startswith("transfiere_a_") or col.startswith("recibe_de_")]
    resultado_dia = resultado_dia[columnas_utiles]
    
    # Guardamos el resultado del día
    nombre_archivo = f"resultado_{dia.lower()}.csv"
    resultado_dia.to_csv(nombre_archivo, index=False)
    print(f"Resultado guardado en: {nombre_archivo}")
    
    # Actualizamos el dinero inicial para el próximo día
    dinero_inicial_df = resultado_dia[["tienda", "efectivo_en_tienda"]].rename(columns={"efectivo_en_tienda": "dinero_inicial"})
    
    # Si es el último día, no necesitamos preparar para el siguiente
    if i < len(dias_semana) - 1:
        print(f"Preparando dinero inicial para el día {dias_semana[i+1]}...")

print("\nProceso completado para todos los días de la semana.")