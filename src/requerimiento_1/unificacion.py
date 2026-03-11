import pandas as pd
import os
from .limpieza import cargar_datos, limpiar_dataframe


def unificar():

    datos = cargar_datos()

    tablas = []

    # columnas que queremos unificar por ticker
    wanted = ['Open', 'High', 'Low', 'Close', 'Volume']

    for ticker, df in datos.items():
        df = limpiar_dataframe(df)

        # crear un dataframe con columnas renombradas como TICKER_Col
        cols = {}
        for col in wanted:
            if col in df.columns:
                cols[col] = f"{ticker}_{col}"
            else:
                # columna ausente -> crear columna NaN
                df[col] = pd.NA
                cols[col] = f"{ticker}_{col}"

        df_ticker = df[wanted].copy()
        df_ticker = df_ticker.rename(columns=cols)

        tablas.append(df_ticker)

    # concatenar por columnas, alineando por índice de fecha
    if tablas:
        df_final = pd.concat(tablas, axis=1)
    else:
        df_final = pd.DataFrame()

    # ordenar fechas
    df_final = df_final.sort_index()

    # interpolar festivos (aplicar por columnas)
    df_final = df_final.sort_index()
    df_final = df_final.interpolate()

    # guardar: asegurarse de que la carpeta existe
    os.makedirs("data/processed", exist_ok=True)
    df_final.to_csv(
        "data/processed/precios_unificados.csv",
        sep=';'
    )

    print("Dataset unificado creado")

    return df_final