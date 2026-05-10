"""
Script de prueba para las visualizaciones.

Este script prueba los gráficos de correlación, candlesticks y PDF.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.visualization import (
    generar_matriz_correlacion,
    graficar_mapa_calor,
    graficar_candlestick,
    calcular_media_movil,
    generar_todas_visualizaciones,
    generar_reporte_pdf
)


def cargar_datos():
    """Carga los datos unificados del proyecto."""
    data_path = project_root / "data" / "processed" / "precios_unificados.csv"
    
    if not data_path.exists():
        print(f"Error: No se encontró el archivo {data_path}")
        print("Por favor ejecuta primero: python main.py")
        return None
    
    df = pd.read_csv(data_path, parse_dates=['Date'])
    print(f"Datos cargados: {len(df)} registros")
    return df


def main():
    print("=" * 60)
    print("PRUEBA DE VISUALIZACIONES")
    print("Requerimiento 4")
    print("=" * 60)
    
    # Cargar datos
    df = cargar_datos()
    if df is None:
        return
    
    # Generar todas las visualizaciones
    resultados = generar_todas_visualizaciones(df)
    
    print("\n" + "=" * 60)
    print("RESUMEN DE ARCHIVOS GENERADOS")
    print("=" * 60)
    
    for tipo, ruta in resultados.items():
        print(f"   {tipo}: {ruta}")
    
    print("\n" + "=" * 60)
    print("✅ VISUALIZACIONES COMPLETADAS")
    print("=" * 60)


if __name__ == "__main__":
    main()