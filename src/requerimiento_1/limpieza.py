import pandas as pd
import glob
import os

def cargar_datos():

    archivos = glob.glob("data/raw/*.csv")

    datos = {}

    for archivo in archivos:

        # Usar basename para compatibilidad en Windows y Unix
        nombre = os.path.basename(archivo)
        ticker = nombre.split("_")[0]

        # Leer CSV con manejo de errores: primero intentar parsear columna 'Date',
        # si falla, intentar leer index desde la primera columna.
        try:
            df = pd.read_csv(
                archivo,
                sep=";",
                parse_dates=["Date"],
                index_col="Date"
            )
        except Exception:
            try:
                df = pd.read_csv(
                    archivo,
                    sep=";",
                    index_col=0,
                    parse_dates=True
                )
            except Exception as e:
                print(f"Advertencia: no se pudo leer {archivo}: {e}")
                continue

        datos[ticker] = df

    return datos


def limpiar_dataframe(df):

    df = df.sort_index()

    # eliminar duplicados
    df = df[~df.index.duplicated()]

    # interpolar valores faltantes
    df = df.interpolate(method="linear")

    return df