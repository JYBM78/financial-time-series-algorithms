"""
Script de prueba para los algoritmos de similitud.

Este script prueba los 4 algoritmos de similitud con los datos reales
del proyecto y muestra los resultados de manera formateada.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Agregar el directorio src al path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.requerimiento_2.algoritmos_similitud.similitud import (
    distancia_euclidiana,
    distancia_euclidiana_normalizada,
    correlacion_pearson,
    dynamic_time_warping,
    similitud_coseno,
    distancia_coseno,
    calcular_todas_similitudes,
    comparar_activos
)


def cargar_datos():
    """Carga los datos unificados del proyecto."""
    data_path = project_root / "data" / "processed" / "precios_unificados.csv"
    
    if not data_path.exists():
        print(f"Error: No se encontró el archivo {data_path}")
        print("Por favor ejecuta primero el ETL (main.py)")
        return None
    
    df = pd.read_csv(data_path, parse_dates=['Date'])
    print(f"Datos cargados: {len(df)} registros")
    print(f"Activos disponibles: {df['Ticker'].unique()}")
    
    return df


def obtener_serie(df, ticker, columna='Close'):
    """Obtiene una serie temporal para un ticker específico."""
    df_ticker = df[df['Ticker'] == ticker].sort_values('Date').reset_index(drop=True)
    return df_ticker[columna].values


def obtener_retornos(serie):
    """Calcula los retornos diarios de una serie de precios."""
    retornos = np.diff(serie) / serie[:-1]
    # Eliminar NaN e infinitos
    retornos = retornos[np.isfinite(retornos)]
    return retornos


def formatear_resultado(resultado):
    """Formatea los resultados de similitud para mostrar."""
    print("\n" + "=" * 60)
    print(f"COMPARACIÓN: {resultado['ticker1']} vs {resultado['ticker2']}")
    print("=" * 60)
    print(f"\nTipo de datos: {resultado['tipo_datos']}")
    print("\n--- MÉTRICAS DE SIMILITUD ---")
    print(f"  Distancia Euclidiana:           {resultado['distancia_euclidiana']:.6f}")
    print(f"  Distancia Euclidiana Normalizada: {resultado['distancia_euclidiana_normalizada']:.6f}")
    print(f"  Correlación de Pearson:         {resultado['correlacion_pearson']:.6f}")
    print(f"  Distancia DTW:                  {resultado['dtw']:.6f}")
    print(f"  Similitud por Coseno:           {resultado['similitud_coseno']:.6f}")
    print(f"  Distancia por Coseno:           {resultado['distancia_coseno']:.6f}")
    print()


def main():
    print("=" * 60)
    print("PRUEBA DE ALGORITMOS DE SIMILITUD")
    print("Requerimiento 2")
    print("=" * 60)
    
    # Cargar datos
    df = cargar_datos()
    if df is None:
        return
    
    # Seleccionar algunos activos para comparar
    tickers_disponibles = df['Ticker'].unique().tolist()
    print(f"\nTickers disponibles: {tickers_disponibles}")
    
    # Comparaciones de ejemplo (sin sufijos .CL)
    comparaciones = [
        ('ECOPETROL', 'ISA'),
        ('GRUPOARGOS', 'GRUPOSURA'),
        ('ECOPETROL', 'GEB'),
    ]
    
    print("\n" + "=" * 60)
    print("RESULTADOS DE COMPARACIONES")
    print("=" * 60)
    
    for ticker1, ticker2 in comparaciones:
        if ticker1 in tickers_disponibles and ticker2 in tickers_disponibles:
            try:
                resultado = comparar_activos(df, ticker1, ticker2)
                formatear_resultado(resultado)
            except Exception as e:
                print(f"Error al comparar {ticker1} vs {ticker2}: {e}")
        else:
            print(f"\nAdvertencia: Uno de los tickers no está disponible")
            print(f"  {ticker1}: {'✓' if ticker1 in tickers_disponibles else '✗'}")
            print(f"  {ticker2}: {'✓' if ticker2 in tickers_disponibles else '✗'}")
    
    # Ejemplo con datos sintéticos para mostrar todos los algoritmos
    print("\n" + "=" * 60)
    print("EJEMPLO CON DATOS SINTÉTICOS")
    print("=" * 60)
    
    np.random.seed(42)
    serie1 = np.array([100, 102, 101, 105, 108, 107, 110, 112, 111, 115])
    serie2 = np.array([98, 101, 100, 104, 107, 106, 109, 111, 110, 114])
    serie3 = np.array([50, 51, 52, 53, 54, 55, 56, 57, 58, 59])
    
    print("\nSerie 1:", serie1)
    print("Serie 2:", serie2)
    print("Serie 3:", serie3)
    
    resultados = calcular_todas_similitudes(serie1, serie2)
    print("\n--- Serie 1 vs Serie 2 ---")
    for clave, valor in resultados.items():
        if clave not in ['ticker1', 'ticker2', 'tipo_datos']:
            print(f"  {clave}: {valor:.6f}")
    
    resultados = calcular_todas_similitudes(serie1, serie3)
    print("\n--- Serie 1 vs Serie 3 (escalada) ---")
    for clave, valor in resultados.items():
        if clave not in ['ticker1', 'ticker2', 'tipo_datos']:
            print(f"  {clave}: {valor:.6f}")
    
    print("\n" + "=" * 60)
    print("ANÁLISIS DE COMPLEJIDAD")
    print("=" * 60)
    print("""
ALGORITMO                    COMPLEJIDAD    ESPACIO
-------------------------------------------------------
Distancia Euclidiana          O(n)           O(n)
Correlación de Pearson        O(n)           O(n)
Dynamic Time Warping          O(n×m)         O(n×m)
Similitud por Coseno          O(n)           O(1)
""")
    
    print("Pruebas completadas exitosamente!")


if __name__ == "__main__":
    main()