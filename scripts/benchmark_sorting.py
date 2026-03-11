"""Script de benchmarking para los algoritmos de ordenamiento.

Genera una tabla CSV con tiempos medios por algoritmo y tamaño, y guarda gráficos
de barras ascendentes para el mayor tamaño probado.
"""
import os
import time
import statistics
import random
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from src.algorithms.sorting import ALGORITHMS


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
    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        print(f"Archivo unificado no encontrado en {data_path}. Ejecuta el ETL primero.")
        return

    print(f"Cargando datos desde {data_path} ...")
    # El CSV unificado se guardó con separador ';'
    df = pd.read_csv(data_path, index_col=0, parse_dates=True, sep=';')

    if df.empty:
        print("El dataset unificado está vacío.")
        return

    # Construir arreglo base de enteros a partir del primer ticker Close (en centavos)
    first_col = df.columns[0]
    series = df[first_col].dropna()
    if series.empty:
        print(f"La columna {first_col} no contiene datos.")
        return

    # Convertir precios a enteros (centavos) para benchmarking
    try:
        arr_base = (series.values.astype(float) * 100).astype(int).tolist()
    except Exception:
        arr_base = [int(x) for x in series.values]

    max_len = len(arr_base)
    print(f"Longitud de la serie base: {max_len}")

    # Tamaños a probar (ajustar según disponibilidad)
    candidate_sizes = [100, 1000, 5000, 10000]
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
            avg, std = measure_time(func, arr, repeats=3)
            records.append({
                'algorithm': name,
                'size': size,
                'avg_time_sec': avg,
                'std_time_sec': std,
            })

    # Guardar CSV con resultados
    results_df = pd.DataFrame.from_records(records)
    csv_path = results_dir / 'sorting_benchmark.csv'
    results_df.to_csv(csv_path, index=False)
    print(f"Resultados guardados en {csv_path}")

    # Generar gráfico para el mayor tamaño probado
    max_size = max(results_df['size'].unique())
    df_max = results_df[results_df['size'] == max_size].copy()
    df_max = df_max.sort_values('avg_time_sec')

    plt.figure(figsize=(10, 6))
    plt.bar(df_max['algorithm'], df_max['avg_time_sec'])
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Tiempo medio (s)')
    plt.title(f'Comparación de tiempos de ordenamiento (n={max_size})')
    plt.tight_layout()
    png_path = results_dir / f'sorting_benchmark_n{max_size}.png'
    plt.savefig(png_path)
    print(f"Gráfico guardado en {png_path}")


if __name__ == '__main__':
    main()
