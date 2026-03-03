import pandas as pd
from .limpieza import cargar_datos, limpiar_dataframe


def unificar():

    datos = cargar_datos()

    precios = []

    for ticker, df in datos.items():

        df = limpiar_dataframe(df)

        serie = df["Close"].rename(ticker)

        precios.append(serie)

    df_final = pd.concat(precios, axis=1)

    # ordenar fechas
    df_final = df_final.sort_index()

    # interpolar festivos
    df_final = df_final.interpolate()

    # guardar
    df_final.to_csv(
        "data/processed/precios_unificados.csv"
    )

    print("Dataset unificado creado")

    return df_final