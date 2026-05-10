"""
Script de prueba para los algoritmos de Patrones y Volatilidad.

Este script prueba los algoritmos con los datos reales del proyecto.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.requerimiento_3.deteccion_patrones.patrones import (
    detectar_todos_patrones,
    calcular_metricas_dispersion,
    clasificar_riesgo,
    clasificar_todos_activos,
    analizar_activo,
    generar_reporte_riesgo
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
    print("PRUEBA DE PATRONES Y VOLATILIDAD")
    print("Requerimiento 3")
    print("=" * 60)
    
    # Cargar datos
    df = cargar_datos()
    if df is None:
        return
    
    # Análisis de un activo específico
    print("\n" + "=" * 60)
    print("ANÁLISIS DE UN ACTIVO: ECOPETROL")
    print("=" * 60)
    
    resultado = analizar_activo(df, 'ECOPETROL')
    
    print(f"\n📊 Clasificación de Riesgo: {resultado['clasificacion_riesgo']}")
    
    print("\n📈 Métricas de Dispersión:")
    for clave, valor in resultado['metricas_dispersion'].items():
        print(f"   {clave}: {valor:.4f}")
    
    print("\n🔍 Patrones Detectados:")
    for patron, datos in resultado['patrones'].items():
        print(f"\n   {patron}:")
        print(f"      Frecuencia: {datos['frecuencia_porcentual']:.2f}%")
        print(f"      Ocurrencias: {datos['num_ocurrencias']}")
    
    # Análisis de todos los activos
    print("\n" + "=" * 60)
    print("CLASIFICACIÓN DE RIESGO DE TODOS LOS ACTIVOS")
    print("=" * 60)
    
    reporte = generar_reporte_riesgo(df, guardar=True)
    
    print("\n📋 Reporte de Riesgo (ordenado por volatilidad):")
    print("-" * 80)
    print(f"{'Ticker':<15} {'Volatilidad':<15} {'Clasificación':<15} {'Días Alza %':<15}")
    print("-" * 80)
    
    for _, row in reporte.iterrows():
        print(f"{row['Ticker']:<15} {row['Volatilidad_Anualizada']:.2f}%{'':<8} {row['Clasificacion_Riesgo']:<15} {row['Frecuencia_Dias_Alza']:.2f}%")
    
    # Resumen de clasificaciones
    print("\n" + "=" * 60)
    print("RESUMEN DE CLASIFICACIONES")
    print("=" * 60)
    
    conteo = reporte['Clasificacion_Riesgo'].value_counts()
    for clasificacion, cantidad in conteo.items():
        print(f"   {clasificacion}: {cantidad} activos")
    
    print("\n" + "=" * 60)
    print("ANÁLISIS DE COMPLEJIDAD")
    print("=" * 60)
    print("""
ALGORITMO                    COMPLEJIDAD    ESPACIO
-------------------------------------------------------
Sliding Window               O(n × w)       O(k)
Detección de Patrones       O(n × w)       O(k)
Cálculo de Volatilidad      O(n)           O(n)
Clasificación de Riesgo     O(n)           O(1)
-------------------------------------------------------
donde: n = longitud de serie, w = tamaño ventana, k = patrones encontrados
""")
    
    print("✅ Pruebas completadas exitosamente!")


if __name__ == "__main__":
    main()