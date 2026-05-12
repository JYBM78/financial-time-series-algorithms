import pandas as pd
import os
from .limpieza import cargar_datos, limpiar_dataframe


def unificar():
    """
    Carga datos de activos individuales, los limpia y los consolida en un
    único DataFrame en formato 'largo' (long format). El resultado se
    guarda en un archivo CSV.

    El formato largo tiene columnas: [Date, Ticker, Open, High, Low, Close, Volume]

    Returns:
        pd.DataFrame: El DataFrame unificado y limpiado.
    """
    datos = cargar_datos()

    list_of_dfs = []

    for ticker, df in datos.items():
        # 1. Limpiar el dataframe individual
        df_limpio = limpiar_dataframe(df)

        # 2. Asegurar que las columnas requeridas existan
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col not in df_limpio.columns:
                df_limpio[col] = pd.NA

        # 3. Añadir la columna del Ticker
        df_limpio['Ticker'] = ticker

        # 4. Mover el índice 'Date' a una columna
        df_limpio = df_limpio.reset_index()

        list_of_dfs.append(df_limpio)

    # Concatenar todos los dataframes en uno solo
    if not list_of_dfs:
        print("Advertencia: No se encontraron datos para unificar.")
        return pd.DataFrame()

    df_final = pd.concat(list_of_dfs, ignore_index=True)

    # Ordenar las columnas para mayor claridad
    column_order = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
    df_final = df_final[column_order]

    # Ordenar el dataframe final por fecha y ticker
    df_final = df_final.sort_values(by=['Date', 'Ticker']).reset_index(drop=True)

    # Interpolar valores faltantes que puedan existir después de la unión
    df_final[['Open', 'High', 'Low', 'Close', 'Volume']] = df_final.groupby('Ticker')[['Open', 'High', 'Low', 'Close', 'Volume']].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both')
    )

    # Guardar el archivo unificado
    os.makedirs("data/processed", exist_ok=True)
    df_final.to_csv(
        "data/processed/precios_unificados.csv",
        sep=',',
        index=False  # No guardar el índice de pandas en el CSV
    )

    print("Dataset unificado creado en formato 'largo'.")

    return df_final