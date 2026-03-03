from src.requerimiento_1.descarga import descargar_todos
from src.requerimiento_1.unificacion import unificar


def main():

    print("ETAPA 1: DESCARGA")
    descargar_todos()

    print("ETAPA 2: UNIFICACION")
    df = unificar()

    print(df.head())


if __name__ == "__main__":
    main()