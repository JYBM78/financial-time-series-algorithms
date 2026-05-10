import numpy as np
import pandas as pd

def detectar_rachas_consecutivas(precios, umbral=0.0):
    retornos = np.diff(precios) / precios[:-1]
    rachas = {"alza": [], "baja": []}
    racha_actual = 1
    tipo_actual = None
    for r in retornos:
        if r > umbral:
            if tipo_actual == "alza":
                racha_actual += 1
            else:
                if tipo_actual == "baja" and racha_actual > 1:
                    rachas["baja"].append(racha_actual)
                racha_actual = 1
                tipo_actual = "alza"
        elif r < -umbral:
            if tipo_actual == "baja":
                racha_actual += 1
            else:
                if tipo_actual == "alza" and racha_actual > 1:
                    rachas["alza"].append(racha_actual)
                racha_actual = 1
                tipo_actual = "baja"
        else:
            if tipo_actual is not None and racha_actual > 1:
                if tipo_actual == "alza":
                    rachas["alza"].append(racha_actual)
                else:
                    rachas["baja"].append(racha_actual)
            racha_actual = 1
            tipo_actual = None
    if tipo_actual is not None and racha_actual > 1:
        if tipo_actual == "alza":
            rachas["alza"].append(racha_actual)
        else:
            rachas["baja"].append(racha_actual)
    return rachas

def detectar_volatilidad_extrema(retornos, factor=2.5):
    if len(retornos) == 0:
        return []
    std = np.std(retornos)
    media = np.mean(retornos)
    return [i for i, r in enumerate(retornos) if abs(r - media) > factor * std]

def detectar_cambio_significativo(precios, umbral_pct=0.03):
    retornos = np.diff(precios) / precios[:-1]
    return [i for i, r in enumerate(retornos) if abs(r) > umbral_pct]

def detectar_reversion_v(precios, ventana=5):
    retornos = np.diff(precios) / precios[:-1]
    indices = []
    for i in range(ventana, len(retornos) - ventana):
        ventana_retornos = retornos[i - ventana:i + 1]
        if len(ventana_retornos) < 2:
            continue
        if ventana_retornos[0] < -0.02 and ventana_retornos[-1] > 0.01:
            indices.append(i)
    return indices

def detectar_todos_patrones(precios):
    retornos = np.diff(precios) / precios[:-1]
    rachas = detectar_rachas_consecutivas(precios)
    vol_extrema = detectar_volatilidad_extrema(retornos)
    cambio_sig = detectar_cambio_significativo(precios)
    reversion_v = detectar_reversion_v(precios)
    n = len(retornos)
    return {
        "dias_consecutivos_alza": {
            "frecuencia_porcentual": round(len(rachas["alza"]) / max(n, 1) * 100, 2),
            "num_ocurrencias": len(rachas["alza"]),
            "rachas": rachas["alza"][:10],
        },
        "dias_consecutivos_baja": {
            "frecuencia_porcentual": round(len(rachas["baja"]) / max(n, 1) * 100, 2),
            "num_ocurrencias": len(rachas["baja"]),
            "rachas": rachas["baja"][:10],
        },
        "volatilidad_extrema": {
            "frecuencia_porcentual": round(len(vol_extrema) / max(n, 1) * 100, 2),
            "num_ocurrencias": len(vol_extrema),
        },
        "cambio_significativo": {
            "frecuencia_porcentual": round(len(cambio_sig) / max(n, 1) * 100, 2),
            "num_ocurrencias": len(cambio_sig),
        },
        "reversion_v": {
            "frecuencia_porcentual": round(len(reversion_v) / max(n, 1) * 100, 2),
            "num_ocurrencias": len(reversion_v),
        },
    }

def calcular_metricas_dispersion(precios):
    retornos = np.diff(precios) / precios[:-1]
    retornos = retornos[np.isfinite(retornos)]
    if len(retornos) == 0:
        return {"desviacion_estandar": 0.0, "volatilidad_diaria": 0.0, "volatilidad_anualizada": 0.0}
    std = np.std(retornos, ddof=1)
    return {
        "desviacion_estandar": round(std, 6),
        "volatilidad_diaria": round(std * 100, 2),
        "volatilidad_anualizada": round(std * np.sqrt(252) * 100, 2),
    }

def clasificar_riesgo(vol_anualizada):
    if vol_anualizada < 15:
        return "Bajo"
    elif vol_anualizada < 30:
        return "Medio"
    elif vol_anualizada < 50:
        return "Alto"
    else:
        return "Muy Alto"

def analizar_activo(df, ticker, columna="Close"):
    sub = df[df["Ticker"] == ticker].sort_values("Date")
    precios = sub[columna].values
    metricas = calcular_metricas_dispersion(precios)
    patrones = detectar_todos_patrones(precios)
    clasificacion = clasificar_riesgo(metricas["volatilidad_anualizada"])
    return {
        "metricas_dispersion": metricas,
        "patrones": patrones,
        "clasificacion_riesgo": clasificacion,
    }

def clasificar_todos_activos(df, columna="Close"):
    rows = []
    for ticker in sorted(df["Ticker"].unique()):
        sub = df[df["Ticker"] == ticker].sort_values("Date")
        precios = sub[columna].values
        metricas = calcular_metricas_dispersion(precios)
        patrones = detectar_todos_patrones(precios)
        riesgo = clasificar_riesgo(metricas["volatilidad_anualizada"])
        rows.append({
            "Ticker": ticker,
            "Volatilidad_Anualizada": metricas["volatilidad_anualizada"],
            "Volatilidad_Diaria": metricas["volatilidad_diaria"],
            "Desviacion_Estandar": metricas["desviacion_estandar"],
            "Clasificacion_Riesgo": riesgo,
            "Frecuencia_Dias_Alza": patrones["dias_consecutivos_alza"]["frecuencia_porcentual"],
            "Frecuencia_Volatilidad_Extrema": patrones["volatilidad_extrema"]["frecuencia_porcentual"],
            "Frecuencia_Cambio_Significativo": patrones["cambio_significativo"]["frecuencia_porcentual"],
        })
    return pd.DataFrame(rows)

def generar_reporte_riesgo(df, guardar=False, columna="Close"):
    reporte = clasificar_todos_activos(df, columna)
    if guardar:
        from pathlib import Path
        ruta = Path(__file__).resolve().parents[3] / "reports" / "reporte_riesgo.csv"
        ruta.parent.mkdir(exist_ok=True)
        reporte.to_csv(ruta, index=False)
    return reporte
