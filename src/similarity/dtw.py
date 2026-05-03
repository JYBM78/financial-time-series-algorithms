"""Dynamic Time Warping (DTW) para series de tiempo financieras.

Permite comparar secuencias que pueden diferir en velocidad o fase,
encontrando el alineamiento optimo entre dos series temporales.
Es mas flexible que la distancia euclidiana pero mas costoso computacionalmente.
"""
import math
from typing import List, Tuple


def dynamic_time_warping(series_a: List[float], series_b: List[float]) -> float:
    """Calcula la distancia DTW entre dos series de tiempo.

    Fundamentacion matematica:
        DTW encuentra el camino de warping W = (w1, w2, ..., wk) que minimiza
        la distancia acumulada entre dos series X = (x1, ..., xn) y Y = (y1, ..., ym).

        Se construye una matriz de costos acumulados D de dimension (n+1) x (m+1):

            D[i, j] = dist(xi, yj) + min(D[i-1, j], D[i, j-1], D[i-1, j-1])

        donde dist(xi, yj) = |xi - yj| es la distancia punto a punto.

        Condiciones de frontera:
            D[0, 0] = 0
            D[i, 0] = infinito para i > 0
            D[0, j] = infinito para j > 0

        La distancia DTW es: DTW(X, Y) = D[n, m]

        Para comparabilidad entre series de distinto tamano, se puede normalizar:
            DTW_norm(X, Y) = D[n, m] / (n + m)

    Descripcion algoritmica:
        1. Obtener longitudes n = len(series_a), m = len(series_b).
        2. Crear matriz D de dimension (n+1) x (m+1) inicializada con infinito,
           excepto D[0][0] = 0.
        3. Para cada fila i de 1 a n:
            Para cada columna j de 1 a m:
                a. Calcular costo local: cost = |series_a[i-1] - series_b[j-1]|
                b. DTW(i, j) = cost + min(D[i-1][j], D[i][j-1], D[i-1][j-1])
                c. Almacenar en D[i][j]
        4. Retornar D[n][m] como distancia DTW.

    Restricciones del warping path:
        - Boundary: El camino inicia en (1,1) y termina en (n,m).
        - Continuity: Cada paso mueve como maximo 1 posicion en cada dimension.
        - Monotonicity: El camino nunca retrocede en el tiempo.

    Analisis de complejidad:
        - Tiempo: O(n * m) donde n y m son las longitudes de las series.
          Se llena una matriz completa con operaciones constantes por celda.
          Si n = m, la complejidad es O(n^2).
        - Espacio: O(n * m) para la matriz de costos acumulados.
          Se puede optimizar a O(min(n, m)) si solo se necesita la distancia
          (no el camino optimo), pero esta implementacion conserva la matriz
          completa para permitir la recuperacion del camino.
        - Es el algoritmo mas costoso de los cuatro implementados.

    Ventajas sobre distancia euclidiana:
        - Permite comparar series de diferente longitud.
        - Maneja desfases temporales (una serie puede estar "adelantada").
        - Captura similitudes en la forma de la curva, no solo en valores absolutos.

    Args:
        series_a: Primera serie de tiempo.
        series_b: Segunda serie de tiempo.

    Returns:
        Distancia DTW entre las dos series.

    Raises:
        ValueError: Si alguna serie esta vacia.
    """
    n = len(series_a)
    m = len(series_b)

    if n == 0 or m == 0:
        raise ValueError("Las series no pueden estar vacias")

    # Crear matriz de costos acumulados
    infinito = float('inf')
    D = [[infinito for _ in range(m + 1)] for _ in range(n + 1)]
    D[0][0] = 0.0

    # Llenar la matriz de costos acumulados
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            costo = abs(series_a[i - 1] - series_b[j - 1])
            D[i][j] = costo + min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1])

    return D[n][m]


def dynamic_time_warping_normalized(series_a: List[float], series_b: List[float]) -> float:
    """Calcula la distancia DTW normalizada por la longitud del camino.

    La normalizacion permite comparar DTW entre pares de series de
    diferentes longitudes:

        DTW_norm = DTW(X, Y) / (n + m)

    Args:
        series_a: Primera serie de tiempo.
        series_b: Segunda serie de tiempo.

    Returns:
        Distancia DTW normalizada.
    """
    n = len(series_a)
    m = len(series_b)
    dtw = dynamic_time_warping(series_a, series_b)
    return dtw / (n + m)


def get_dtw_path(series_a: List[float], series_b: List[float]) -> List[Tuple[int, int]]:
    """Obtiene el camino de warping optimo entre dos series.

    Recupera la secuencia de pares de indices que conforman el
    alineamiento optimo encontrado por DTW mediante backtracking.

    Descripcion algoritmica:
        1. Calcular la matriz de costos acumulados D (como en dynamic_time_warping).
        2. Iniciar desde (n, m).
        3. Mientras (i, j) != (0, 0):
            a. Encontrar cual de los tres predecesores tiene el menor costo:
               D[i-1][j], D[i][j-1], D[i-1][j-1]
            b. Mover al predecesor con menor costo.
            c. Agregar (i-1, j-1) al camino (indices de las series originales).
        4. Invertir el camino para obtener orden cronologico.

    Args:
        series_a: Primera serie de tiempo.
        series_b: Segunda serie de tiempo.

    Returns:
        Lista de tuplas (i, j) representando el camino de warping optimo.
    """
    n = len(series_a)
    m = len(series_b)

    if n == 0 or m == 0:
        raise ValueError("Las series no pueden estar vacias")

    # Crear matriz de costos acumulados
    infinito = float('inf')
    D = [[infinito for _ in range(m + 1)] for _ in range(n + 1)]
    D[0][0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            costo = abs(series_a[i - 1] - series_b[j - 1])
            D[i][j] = costo + min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1])

    # Backtracking para recuperar el camino
    camino = []
    i, j = n, m
    while i > 0 and j > 0:
        camino.append((i - 1, j - 1))
        minimo = min(D[i - 1][j - 1], D[i - 1][j], D[i][j - 1])
        if minimo == D[i - 1][j - 1]:
            i -= 1
            j -= 1
        elif minimo == D[i - 1][j]:
            i -= 1
        else:
            j -= 1

    camino.reverse()
    return camino


def dtw_similarity_score(series_a: List[float], series_b: List[float]) -> float:
    """Calcula un puntaje de similitud basado en DTW.

    Convierte la distancia DTW normalizada en un puntaje en [0, 1]:

        sim = 1 / (1 + DTW_norm)

    Args:
        series_a: Primera serie de tiempo.
        series_b: Segunda serie de tiempo.

    Returns:
        Puntaje de similitud en [0, 1], donde 1 indica identidad perfecta.
    """
    dist = dynamic_time_warping_normalized(series_a, series_b)
    return 1.0 / (1.0 + dist)
