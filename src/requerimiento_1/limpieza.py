import pandas as pd
import glob

def cargar_datos():

    archivos = glob.glob("data/raw/*.csv")

    datos = {}

    for archivo in archivos:

        ticker = archivo.split("/")[-1].split("_")[0]

        df = pd.read_csv(
            archivo,
            sep=";",
            parse_dates=["Date"],
            index_col="Date"
        )

        datos[ticker] = df

    return datos


def limpiar_dataframe(df):

    df = df.sort_index()

    # eliminar duplicados
    df = df[~df.index.duplicated()]

    # interpolar valores faltantes
    df = df.interpolate(method="linear")

    return df