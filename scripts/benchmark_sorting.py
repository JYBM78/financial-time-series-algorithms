"""Script de benchmarking para los algoritmos de ordenamiento.

Genera una tabla CSV con tiempos medios por algoritmo y tamaño, y guarda gráficos
de barras ascendentes para el mayor tamaño probado.
"""
from src.algorithms.sorting import ALGORITHMS
import os
import sys
import time
import statistics
import random
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# --- INICIO DE LA CORRECCIÓN DE IMPORTACIÓN ---
# Añadir el directorio raíz del proyecto a sys.path para encontrar 'src'
project_root_for_import = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root_for_import))
# --- FIN DE LA CORRECCIÓN DE IMPORTACIÓN ---


def measure_time(func, arr, repeats=3):
    times = []
    for _ in range(repeats):
        a_copy = list(arr)
        t0 = time.perf_counter()
        func(a_copy)
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return statistics.mean(times), statistics.stdev(times) if len(times) > 1 else 0.0


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "processed" / "precios_unificados.csv"
    # Corrección: Usar el directorio 'reports' que ya existe en el proyecto
    results_dir = project_root / "reports"
    results_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        print(
            f"Archivo unificado no encontrado en {data_path}. Ejecuta el ETL primero.")
        return

    print(f"Cargando datos desde {data_path} ...")
    # Corrección: El CSV unificado se guarda con separador ',' y sin índice
    df = pd.read_csv(data_path, parse_dates=['Date'], sep=',')

    if df.empty:
        print("El dataset unificado está vacío.")
        return

    # Corrección: Usar la columna 'Close' explícitamente para el benchmark
    series = df['Close'].dropna()
    if series.empty:
        print("La columna 'Close' no contiene datos o está vacía después de eliminar NaNs.")
        return

    # Convertir precios a enteros (centavos) para benchmarking
    try:
        arr_base = (series.values.astype(float) * 100).astype(int).tolist()
    except Exception:
        arr_base = [int(x) for x in series.values]

    max_len = len(arr_base)
    print(f"Longitud de la serie base: {max_len}")

    # Tamaños a probar (ajustar según disponibilidad)
    candidate_sizes = [100, 1000, 5000, 10000, 20000]
    sizes = [s for s in candidate_sizes if s <= max_len]
    if not sizes:
        sizes = [max_len]
    print(f"Tamaños a probar: {sizes}")

    records = []

    for size in sizes:
        print(f"Preparando arrays de tamaño {size} ...")
        if size <= max_len:
            arr = arr_base[:size]
        else:
            # muestreo con reemplazo si necesitamos más
            arr = random.choices(arr_base, k=size)

        for name, func in ALGORITHMS.items():
            print(f"Midiendo {name} (n={size}) ...")
            try:
                avg, std = measure_time(func, arr, repeats=3)
                records.append({
                    'algorithm': name,
                    'size': size,
                    'avg_time_sec': avg,
                    'std_time_sec': std,
                })
            except Exception as e:
                print(f"  -> ERROR al ejecutar {name}: {e}")

    # Guardar CSV con resultados
    results_df = pd.DataFrame.from_records(records)
    csv_path = results_dir / 'sorting_benchmark.csv'
    results_df.to_csv(csv_path, index=False)
    print(f"Resultados guardados en {csv_path}")

    # Generar gráfico para el mayor tamaño probado
    if 'size' in results_df and not results_df.empty:
        max_size = max(results_df['size'].unique())
        df_max = results_df[results_df['size'] == max_size].copy()
        df_max = df_max.sort_values('avg_time_sec')

        plt.figure(figsize=(10, 6))
        plt.figure(figsize=(10, 6))

        bars = plt.bar(df_max['algorithm'], df_max['avg_time_sec'])

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height:.2e}",
                ha='center',
                va='bottom'
            )

        plt.yscale('log')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Tiempo medio (s)')
        plt.title(f'Comparación de tiempos de ordenamiento (n={max_size})')

        plt.yscale('log')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Tiempo medio (s)')
        plt.title(f'Comparación de tiempos de ordenamiento (n={max_size})')
        plt.tight_layout()
        png_path = results_dir / f'sorting_benchmark_n{max_size}.png'
        plt.savefig(png_path)
        print(f"Gráfico guardado en {png_path}")
    else:
        print("No se generaron resultados de benchmark, no se puede crear el gráfico.")


if __name__ == '__main__':
    main()
