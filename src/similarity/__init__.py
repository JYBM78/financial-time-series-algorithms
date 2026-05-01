"""
Módulo de Similitud de Series de Tiempo

Este módulo implementa cuatro algoritmos de similitud para comparar
series temporales financieras. Cada algoritmo incluye:
- Explicación matemática
- Descripción algorítmica
- Análisis de complejidad computacional

Autor: Equipo del proyecto
Fecha: 2026
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any
import math


# =========================================================
# 1. DISTANCIA EUCLIDIANA
# =========================================================
"""
MATHEMATICAL EXPLANATION:
=========================
La distancia euclidiana entre dos vectores n-dimensionales x e y se define como:

    d(x, y) = √(Σ(xi - yi)²) para i = 1 hasta n

En el contexto de series temporales, comparamos los precios o retornos
de dos activos en los mismos puntos temporales.

Para normalizar y hacer la métrica independiente de la escala, se puede
utilizar la distancia euclidiana normalizada:

    d_norm(x, y) = √(Σ((xi - yi) / σi)²)

donde σi es la desviación estándar de la diferencia en la dimensión i.

ALGORITHM DESCRIPTION:
======================
1. Alinear las dos series por fecha (mismo índice temporal)
2. Calcular la diferencia elemento a elemento
3. Elevar cada diferencia al cuadrado
4. Sumar todas las diferencias al cuadrado
5. Extraer la raíz cuadrada

COMPLEJITY: O(n) donde n es la longitud de la serie
ESPACIO: O(n) para almacenar las series
"""


def distancia_euclidiana(serie1: np.ndarray, serie2: np.ndarray) -> float:
    """
    Calcula la distancia euclidiana entre dos series temporales.
    
    Parámetros:
    -----------
    serie1 : np.ndarray
        Primera serie temporal (precios o retornos)
    serie2 : np.ndarray
        Segunda serie temporal
        
    Retorna:
    --------
    float
        Distancia euclidiana entre las dos series
    """
    # Verificar que las series tengan la misma longitud
    if len(serie1) != len(serie2):
        raise ValueError("Las series deben tener la misma longitud")
    
    # Calcular diferencias elemento a elemento
    diferencias = serie1 - serie2
    
    # Elevar al cuadrado y sumar
    suma_cuadrados = np.sum(diferencias ** 2)
    
    # Extraer raíz cuadrada
    distancia = np.sqrt(suma_cuadrados)
    
    return float(distancia)


def distancia_euclidiana_normalizada(serie1: np.ndarray, serie2: np.ndarray) -> float:
    """
    Calcula la distancia euclidiana normalizada entre dos series.
    
    La normalización divide cada diferencia por la desviación estándar
    correspondiente para hacer la métrica independiente de la escala.
    """
    if len(serie1) != len(serie2):
        raise ValueError("Las series deben tener la misma longitud")
    
    diferencias = serie1 - serie2
    desviacion = np.std(diferencias)
    
    if desviacion == 0:
        return 0.0
    
    distancia_normalizada = np.sqrt(np.sum((diferencias / desviacion) ** 2))
    
    return float(distancia_normalizada)


# =========================================================
# 2. CORRELACIÓN DE PEARSON
# =========================================================
"""
MATHEMATICAL EXPLANATION:
=========================
El coeficiente de correlación de Pearson mide la relación lineal
entre dos variables aleatorias. Se define como:

    r = Σ(xi - x̄)(yi - ȳ) / √(Σ(xi - x̄)² * Σ(yi - ȳ)²)

donde:
- x̄, ȳ son las medias de las series
- El numerador es la covarianza
- El denominador es el producto de las desviaciones estándar

Interpretación:
- r = 1: Correlación lineal positiva perfecta
- r = -1: Correlación lineal negativa perfecta
- r = 0: No hay correlación lineal
- |r| > 0.7: Correlación fuerte
- 0.3 < |r| < 0.7: Correlación moderada
- |r| < 0.3: Correlación débil

ALGORITHM DESCRIPTION:
=====================
1. Calcular la media de cada serie
2. Calcular las desviaciones de cada elemento respecto a su media
3. Multiplicar las desviaciones de ambas series y sumar (covarianza)
4. Calcular el producto de las sumas de cuadrados de las desviaciones
5. Dividir la covarianza por el producto de las desviaciones estándar

COMPLEJITY: O(n) donde n es la longitud de la serie
ESPACIO: O(n) para almacenar las series
"""


def correlacion_pearson(serie1: np.ndarray, serie2: np.ndarray) -> float:
    """
    Calcula el coeficiente de correlación de Pearson entre dos series.
    
    Parámetros:
    -----------
    serie1 : np.ndarray
        Primera serie temporal
    serie2 : np.ndarray
        Segunda serie temporal
        
    Retorna:
    --------
    float
        Coeficiente de correlación (-1 a 1)
    """
    if len(serie1) != len(serie2):
        raise ValueError("Las series deben tener la misma longitud")
    
    n = len(serie1)
    
    # Calcular medias
    media1 = np.mean(serie1)
    media2 = np.mean(serie2)
    
    # Calcular desviaciones respecto a la media
    desv1 = serie1 - media1
    desv2 = serie2 - media2
    
    # Calcular covarianza (numerador)
    covarianza = np.sum(desv1 * desv2)
    
    # Calcular producto de sumas de cuadrados (denominador)
    suma_cuadrados1 = np.sum(desv1 ** 2)
    suma_cuadrados2 = np.sum(desv2 ** 2)
    
    # Evitar división por cero
    if suma_cuadrados1 == 0 or suma_cuadrados2 == 0:
        return 0.0
    
    # Calcular correlación
    correlacion = covarianza / np.sqrt(suma_cuadrados1 * suma_cuadrados2)
    
    return float(correlacion)


def matriz_correlacion(series_dict: Dict[str, np.ndarray]) -> pd.DataFrame:
    """
    Calcula la matriz de correlación para un diccionario de series.
    
    Parámetros:
    -----------
    series_dict : dict
        Diccionario con {ticker: serie_temporal}
        
    Retorna:
    --------
    pd.DataFrame
        Matriz de correlación
    """
    tickers = list(series_dict.keys())
    n = len(tickers)
    matriz = np.zeros((n, n))
    
    for i, ticker1 in enumerate(tickers):
        for j, ticker2 in enumerate(tickers):
            if i == j:
                matriz[i, j] = 1.0
            elif i < j:
                corr = correlacion_pearson(series_dict[ticker1], series_dict[ticker2])
                matriz[i, j] = corr
                matriz[j, i] = corr
    
    return pd.DataFrame(matriz, index=tickers, columns=tickers)


# =========================================================
# 3. DYNAMIC TIME WARPING (DTW)
# =========================================================
"""
MATHEMATICAL EXPLANATION:
=========================
DTW es un algoritmo que encuentra el alineamiento óptimo entre dos
secuencias que pueden variar en velocidad o fase. Utiliza programación
dinámica para encontrar la ruta de deformación mínima.

La distancia DTW se define como:
    
    DTW(i, j) = d(i, j) + min(DTW(i-1, j), DTW(i, j-1), DTW(i-1, j-1))

donde d(i, j) es la distancia local (euclidiana) entre los puntos i y j.

La ruta de alineamiento debe cumplir:
- Monotonicidad: no puede ir hacia atrás en el tiempo
- Continuidad: no puede saltar elementos
- Boundary: debe empezar en (0,0) y terminar en (n,m)

ALGORITHM DESCRIPTION:
=====================
1. Crear una matriz de costos n×m donde cada celda (i,j) representa
   la distancia entre el punto i de la serie1 y el punto j de la serie2
2. Inicializar la primera fila y columna con sumas acumuladas
3. Para cada celda (i,j), calcular el costo mínimo de las celdas
   adyacentes más la distancia local
4. La distancia DTW es el valor en la celda (n,m)
5. Reconstruir la ruta de alineamiento

COMPLEJITY: O(n × m) donde n y m son las longitudes de las series
ESPACIO: O(n × m) para la matriz de costos
"""


def dynamic_time_warping(serie1: np.ndarray, serie2: np.ndarray) -> Tuple[float, List]:
    """
    Calcula la distancia DTW y la ruta de alineamiento entre dos series.
    
    Parámetros:
    -----------
    serie1 : np.ndarray
        Primera serie temporal
    serie2 : np.ndarray
        Segunda serie temporal
        
    Retorna:
    --------
    tuple
        (distancia_dtw, ruta_de_alineamiento)
    """
    n = len(serie1)
    m = len(serie2)
    
    # Crear matriz de costos (n+1) x (m+1) inicializada con infinito
    dtw_matrix = np.full((n + 1, m + 1), np.inf)
    dtw_matrix[0, 0] = 0
    
    # Rellenar la matriz de costos
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Distancia euclidiana entre los puntos
            costo = (serie1[i - 1] - serie2[j - 1]) ** 2
            
            # Tomar el mínimo de las celdas adyacentes
            dtw_matrix[i, j] = costo + min(
                dtw_matrix[i - 1, j],      # inserción
                dtw_matrix[i, j - 1],      # eliminación
                dtw_matrix[i - 1, j - 1]   # match
            )
    
    # La distancia DTW es la raíz cuadrada del costo total
    distancia = np.sqrt(dtw_matrix[n, m])
    
    # Reconstruir la ruta de alineamiento
    ruta = []
    i, j = n, m
    while i > 0 or j > 0:
        ruta.append((i - 1, j - 1))
        
        if i == 0:
            j -= 1
        elif j == 0:
            i -= 1
        else:
            # Moverse a la celda con el menor valor
            opciones = [
                dtw_matrix[i - 1, j - 1],
                dtw_matrix[i - 1, j],
                dtw_matrix[i, j - 1]
            ]
            min_idx = np.argmin(opciones)
            
            if min_idx == 0:
                i -= 1
                j -= 1
            elif min_idx == 1:
                i -= 1
            else:
                j -= 1
    
    ruta.reverse()
    
    return float(distancia), ruta


def dtw_rapida(serie1: np.ndarray, serie2: np.ndarray, 
               window_size: int = None) -> float:
    """
    Versión optimizada de DTW con ventana de restricción.
    
    Parámetros:
    -----------
    serie1 : np.ndarray
        Primera serie temporal
    serie2 : np.ndarray
        Segunda serie temporal
    window_size : int, opcional
        Tamaño de la ventana de restricción (reduce complejidad)
        
    Retorna:
    --------
    float
        Distancia DTW
    """
    n = len(serie1)
    m = len(serie2)
    
    if window_size is None:
        window_size = max(n, m)
    
    # Usar solo dos filas para reducir espacio O(n×m) → O(n)
    prev_row = np.full(m + 1, np.inf)
    curr_row = np.full(m + 1, np.inf)
    prev_row[0] = 0
    
    for i in range(1, n + 1):
        curr_row[0] = np.inf
        
        # Limitar el rango de j para la ventana
        j_start = max(1, i - window_size)
        j_end = min(m, i + window_size)
        
        for j in range(j_start, j_end + 1):
            costo = (serie1[i - 1] - serie2[j - 1]) ** 2
            curr_row[j] = costo + min(
                prev_row[j] if j < len(prev_row) else np.inf,
                curr_row[j - 1],
                prev_row[j - 1] if j > 0 else np.inf
            )
        
        prev_row, curr_row = curr_row, prev_row
    
    return float(np.sqrt(prev_row[m]))


# =========================================================
# 4. SIMILITUD POR COSENO
# =========================================================
"""
MATHEMATICAL EXPLANATION:
=========================
La similitud por coseno mide el ángulo entre dos vectores en un
espacio n-dimensional. Se define como:

    cos(θ) = (A · B) / (||A|| × ||B||)

donde:
- A · B es el producto punto (AᵀB)
- ||A|| y ||B|| son las normas euclidianas de los vectores

El valor está en el rango [-1, 1]:
- 1: Vectores idénticos (ángulo 0°)
- 0: Vectores ortogonales (ángulo 90°)
- -1: Vectores opuestos (ángulo 180°)

Para convertir a distancia (donde 0 es más similar):
    distancia_coseno = 1 - similitud_coseno

ALGORITHM DESCRIPTION:
=====================
1. Calcular el producto punto de los dos vectores
2. Calcular la norma (magnitud) de cada vector
3. Dividir el producto punto por el producto de las normas
4. Convertir a distancia si es necesario

COMPLEJITY: O(n) donde n es la dimensión de los vectores
ESPACIO: O(1) adicional (solo variables escalares)
"""


def similitud_coseno(serie1: np.ndarray, serie2: np.ndarray) -> float:
    """
    Calcula la similitud por coseno entre dos series temporales.
    
    Parámetros:
    -----------
    serie1 : np.ndarray
        Primera serie temporal
    serie2 : np.ndarray
        Segunda serie temporal
        
    Retorna:
    --------
    float
        Similitud por coseno (-1 a 1)
    """
    if len(serie1) != len(serie2):
        raise ValueError("Las series deben tener la misma longitud")
    
    # Calcular producto punto
    producto_punto = np.dot(serie1, serie2)
    
    # Calcular normas
    norma1 = np.linalg.norm(serie1)
    norma2 = np.linalg.norm(serie2)
    
    # Evitar división por cero
    if norma1 == 0 or norma2 == 0:
        return 0.0
    
    # Calcular similitud por coseno
    similitud = producto_punto / (norma1 * norma2)
    
    return float(similitud)


def distancia_coseno(serie1: np.ndarray, serie2: np.ndarray) -> float:
    """
    Calcula la distancia por coseno (1 - similitud).
    
    Parámetros:
    -----------
    serie1 : np.ndarray
        Primera serie temporal
    serie2 : np.ndarray
        Segunda serie temporal
        
    Retorna:
    --------
    float
        Distancia por coseno (0 a 2, donde 0 es más similar)
    """
    similitud = similitud_coseno(serie1, serie2)
    return float(1 - similitud)


# =========================================================
# INTERFAZ UNIFICADA
# =========================================================


def calcular_todas_similitudes(serie1: np.ndarray, serie2: np.ndarray) -> Dict[str, Any]:
    """
    Calcula todas las métricas de similitud entre dos series.
    
    Parámetros:
    -----------
    serie1 : np.ndarray
        Primera serie temporal
    serie2 : np.ndarray
        Segunda serie temporal
        
    Retorna:
    --------
    dict
        Diccionario con todas las métricas de similitud
    """
    return {
        'distancia_euclidiana': distancia_euclidiana(serie1, serie2),
        'distancia_euclidiana_normalizada': distancia_euclidiana_normalizada(serie1, serie2),
        'correlacion_pearson': correlacion_pearson(serie1, serie2),
        'dtw': dynamic_time_warping(serie1, serie2)[0],
        'similitud_coseno': similitud_coseno(serie1, serie2),
        'distancia_coseno': distancia_coseno(serie1, serie2)
    }


def comparar_activos(df: pd.DataFrame, ticker1: str, ticker2: str, 
                     columna: str = 'Close') -> Dict[str, Any]:
    """
    Compara dos activos del dataset y retorna todas las métricas de similitud.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con columnas Date, Ticker, Open, High, Low, Close, Volume
    ticker1 : str
        Primer ticker a comparar
    ticker2 : str
        Segundo ticker a comparar
    columna : str
        Columna a utilizar para la comparación
        
    Retorna:
    --------
    dict
        Diccionario con todas las métricas de similitud
    """
    # Filtrar por tickers
    df1 = df[df['Ticker'] == ticker1].sort_values('Date').reset_index(drop=True)
    df2 = df[df['Ticker'] == ticker2].sort_values('Date').reset_index(drop=True)
    
    # Obtener las series
    serie1 = df1[columna].values
    serie2 = df2[columna].values
    
    # Calcular retornos diarios para mejor comparación
    retornos1 = np.diff(serie1) / serie1[:-1]
    retornos2 = np.diff(serie2) / serie2[:-1]
    
    # Usar la longitud mínima
    n = min(len(retornos1), len(retornos2))
    retornos1 = retornos1[:n]
    retornos2 = retornos2[:n]
    
    # Calcular todas las métricas usando retornos
    resultados = calcular_todas_similitudes(retornos1, retornos2)
    resultados['ticker1'] = ticker1
    resultados['ticker2'] = ticker2
    resultados['tipo_datos'] = 'retornos_diarios'
    
    return resultados


# =========================================================
# PRUEBAS
# =========================================================


if __name__ == "__main__":
    # Crear datos de prueba
    np.random.seed(42)
    
    # Series de ejemplo
    serie_a = np.array([100, 102, 101, 105, 108, 107, 110, 112, 111, 115])
    serie_b = np.array([98, 101, 100, 104, 107, 106, 109, 111, 110, 114])
    serie_c = np.array([50, 51, 52, 53, 54, 55, 56, 57, 58, 59])  # Similar a A pero escalada
    
    print("=" * 60)
    print("PRUEBAS DE ALGORITMOS DE SIMILITUD")
    print("=" * 60)
    
    # Prueba 1: Distancia Euclidiana
    print("\n1. DISTANCIA EUCLIDIANA")
    print("-" * 40)
    dist_eucl = distancia_euclidiana(serie_a, serie_b)
    print(f"   Serie A vs Serie B: {dist_eucl:.4f}")
    dist_eucl_norm = distancia_euclidiana_normalizada(serie_a, serie_b)
    print(f"   Serie A vs Serie B (normalizada): {dist_eucl_norm:.4f}")
    
    # Prueba 2: Correlación de Pearson
    print("\n2. CORRELACIÓN DE PEARSON")
    print("-" * 40)
    corr = correlacion_pearson(serie_a, serie_b)
    print(f"   Serie A vs Serie B: {corr:.4f}")
    corr_c = correlacion_pearson(serie_a, serie_c)
    print(f"   Serie A vs Serie C: {corr_c:.4f}")
    
    # Prueba 3: DTW
    print("\n3. DYNAMIC TIME WARPING")
    print("-" * 40)
    dtw_dist, ruta = dynamic_time_warping(serie_a, serie_b)
    print(f"   Serie A vs Serie B: {dtw_dist:.4f}")
    print(f"   Longitud de ruta: {len(ruta)}")
    
    # Prueba 4: Similitud por Coseno
    print("\n4. SIMILITUD POR COSENO")
    print("-" * 40)
    sim_cos = similitud_coseno(serie_a, serie_b)
    print(f"   Serie A vs Serie B: {sim_cos:.4f}")
    dist_cos = distancia_coseno(serie_a, serie_b)
    print(f"   Distancia coseno (A vs B): {dist_cos:.4f}")
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)