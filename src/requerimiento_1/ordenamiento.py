"""Utilidades para el Requerimiento 2.

Contiene:
- ordenar_registros: ordena el CSV unificado por fecha asc y, en empate, por el precio de cierre
- top_15_volumen_por_activo: calcula los 15 días con mayor volumen por ticker a partir de los CSV en data/raw

Se puede ejecutar como script desde la raíz del proyecto poniendo el root en PYTHONPATH:
  $env:PYTHONPATH = "."; python src\requerimiento_1\ordenamiento.py
"""
from pathlib import Path
import os
import glob
import pandas as pd
from typing import Optional


def ordenar_registros(input_csv: str = "data/processed/precios_unificados.csv",
                      output_csv: str = "data/processed/precios_unificados_sorted.csv",
                      ticker_for_tie: Optional[str] = None):
    """Ordena el dataset unificado por fecha ascendente.

    Cuando hay registros con la misma fecha, usa la columna del ticker indicado
    como criterio secundario (precio de cierre). Si no se indica ticker, usa la
    primera columna disponible.
    """
    input_path = Path(input_csv)
    if not input_path.exists():
        print(f"Archivo no encontrado: {input_csv}")
        return

    df = pd.read_csv(input_path, index_col=0, parse_dates=True, sep=';')

    if df.empty:
        print("El dataset unificado está vacío.")
        return

    # Elegir columna para tie-breaker: preferimos una columna de cierre
    close_cols = [c for c in df.columns if str(c).endswith('_Close')]

    if ticker_for_tie is None:
        if close_cols:
            ticker_for_tie = close_cols[0]
        else:
            ticker_for_tie = df.columns[0]
    else:
        # si el usuario pasó un ticker sin sufijo, buscar columna TICKER_Close
        if ticker_for_tie not in df.columns:
            candidate = f"{ticker_for_tie}_Close"
            if candidate in df.columns:
                ticker_for_tie = candidate
            else:
                # intentar usar primera columna de Close
                if close_cols:
                    print(f"Ticker para tie-breaker '{ticker_for_tie}' no encontrado; usando {close_cols[0]} en su lugar.")
                    ticker_for_tie = close_cols[0]
                else:
                    print(f"Ticker para tie-breaker '{ticker_for_tie}' no encontrado en columnas; usando la primera columna.")
                    ticker_for_tie = df.columns[0]


    # Reset index para tener 'Date' como columna
    df_reset = df.reset_index().rename(columns={'index': 'Date'})

    # Ordenar por Date (datetime) asc y luego por ticker_for_tie asc
    try:
        df_sorted = df_reset.sort_values(['Date', ticker_for_tie], ascending=[True, True])
    except Exception as e:
        print(f"Error al ordenar: {e}")
        return

    # Guardar con separador ';'
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_sorted.to_csv(out_path, index=False, sep=';')
    print(f"Archivo ordenado guardado en: {out_path}")
    return out_path


def top_15_volumen_por_activo(raw_folder: str = "data/raw", output_dir: str = "results/top15"):
    """Calcula los 15 días con mayor volumen para cada ticker leyendo los CSV en `raw_folder`.

    Guarda un CSV por ticker en `output_dir` con las 15 filas ordenadas ascendentemente
    (según lo pide el enunciado).
    """
    raw_path = Path(raw_folder)
    files = glob.glob(str(raw_path / "*.csv"))
    if not files:
        print(f"No se encontraron CSV en {raw_folder}")
        return

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    combined = []

    for file in files:
        name = os.path.basename(file)
        ticker = name.split("_")[0]
        try:
            df = pd.read_csv(file, sep=';', parse_dates=['Date'], index_col='Date')
        except Exception as e:
            print(f"Advertencia: no se pudo leer {file}: {e}")
            continue

        vol_col = None
        for candidate in ['Volume', 'volume', 'VOL', 'Volumen']:
            if candidate in df.columns:
                vol_col = candidate
                break

        if vol_col is None:
            print(f"Advertencia: columna de volumen no encontrada en {file}; omitiendo {ticker}.")
            continue

        s = df[vol_col].dropna()
        if s.empty:
            print(f"Advertencia: no hay datos de volumen para {ticker}.")
            continue

        top15 = s.sort_values(ascending=False).head(15)
        # ordenar ascendente como pide el enunciado
        top15_sorted = top15.sort_values(ascending=True)

        out_file = out_dir / f"top15_vol_{ticker}.csv"
        # Guardar con separador ';' y poner Date como columna
        top15_sorted.to_csv(out_file, sep=';')
        print(f"Top 15 volumen guardado para {ticker} en {out_file}")

        # añadir al combinado
        df_out = top15_sorted.reset_index().rename(columns={vol_col: 'Volume'})
        df_out.insert(0, 'Ticker', ticker)
        combined.append(df_out)

    if combined:
        combined_df = pd.concat(combined, ignore_index=True)
        combined_file = out_dir / 'top15_vol_all.csv'
        combined_df.to_csv(combined_file, sep=';', index=False)
        print(f"Archivo combinado con todos los top15 guardado en {combined_file}")
        return combined_file
    else:
        print("No se generaron archivos de top15.")
        return None


if __name__ == '__main__':
    # Ejecución simple: ejecutar ambas tareas
    print("Ordenando registros del dataset unificado...")
    ordenar_registros()
    print("Calculando top 15 de volumen por activo...")
    top_15_volumen_por_activo()
