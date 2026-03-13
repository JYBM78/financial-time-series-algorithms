"""
Script para realizar análisis puntuales sobre el dataset unificado.

Funcionalidades:
1. Ordena el dataset completo por fecha y luego por precio de cierre.
2. Encuentra los 15 días con mayor volumen de negociación.
"""
import pandas as pd
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "processed" / "precios_unificados.csv"
    reports_dir = project_root / "reports"
    reports_dir.mkdir(exist_ok=True)

    # --- Cargar Datos ---
    print(f'Cargando datos desde {data_path}...')
    if not data_path.exists():
        print(f'Error: El archivo {data_path} no existe. Ejecuta el ETL primero.')
        return

    try:
        df = pd.read_csv(data_path, parse_dates=['Date'])
    except Exception as e:
        print(f'Error al leer el archivo CSV: {e}')
        return

    print('Datos cargados exitosamente.')

    # --- Tarea 1: Ordenar por Fecha y Cierre ---
    print('\n--- Tarea 1: Ordenando por Fecha y Precio de Cierre ---')
    df_sorted_by_date = df.sort_values(by=['Date', 'Close'], ascending=[True, True])
    
    # Guardar el resultado
    sorted_by_date_path = reports_dir / "precios_ordenados_por_fecha.csv"
    df_sorted_by_date.to_csv(sorted_by_date_path, index=False)
    
    print(f'Dataset ordenado por fecha y cierre guardado en: {sorted_by_date_path}')
    print('Mostrando las primeras 5 filas del resultado:')
    print(df_sorted_by_date.head())

    # --- Tarea 2: Top 15 Días por Volumen ---
    print('\n--- Tarea 2: Encontrando los 15 días con mayor volumen de negociación ---')
    df_top_15_volume = df.sort_values(by='Volume', ascending=False).head(15)

    # Guardar el resultado
    top_15_volume_path = reports_dir / "top_15_dias_por_volumen.csv"
    df_top_15_volume.to_csv(top_15_volume_path, index=False)

    print(f'Top 15 días por volumen guardado en: {top_15_volume_path}')
    print('Mostrando los 15 días con mayor volumen:')
    print(df_top_15_volume)

if __name__ == "__main__":
    main()
