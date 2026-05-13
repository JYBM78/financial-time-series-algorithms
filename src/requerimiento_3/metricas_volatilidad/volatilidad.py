import numpy as np
import pandas as pd

from ..deteccion_patrones.patrones import calcular_metricas_dispersion, clasificar_riesgo, detectar_todos_patrones

def analizar_activo_volatilidad(df, ticker, columna="Close"):
    sub = df[df["Ticker"] == ticker].sort_values("Date")
    precios = sub[columna].values
    metricas = calcular_metricas_dispersion(precios)
    riesgo = clasificar_riesgo(metricas["volatilidad_anualizada"])
    return {"ticker": ticker, **metricas, "clasificacion_riesgo": riesgo}

def comparar_volatilidades(df, columna="Close"):
    rows = []
    for ticker in sorted(df["Ticker"].unique()):
        r = analizar_activo_volatilidad(df, ticker, columna)
        rows.append(r)
    return pd.DataFrame(rows)
