"""Distancia Euclidiana aplicada a series de tiempo financieras.

Mide la distancia directa entre dos series de tiempo punto a punto.
Es la métrica de similitud más simple y computacionalmente eficiente.
"""
import math
from typing import List, Tuple


def euclidean_distance(series_a: List[float], series_b: List[float]) -> float:
    """Calcula la distancia euclidiana entre dos series de tiempo.

    Fundamentacion matematica:
        La distancia euclidiana entre dos vectores X = (x1, x2, ..., xn) y
        Y = (y1, y2, ..., yn) se define como:

            d(X, Y) = sqrt(sum((xi - yi)^2) for i in 1..n)

        Es una extension de la formula de Pitagoras al espacio n-dimensional.

    Descripcion algoritmica:
        1. Verificar que ambas series tengan la misma longitud n.
        2. Inicializar acumulador 'suma_cuadrados' en 0.
        3. Para cada indice i de 0 a n-1:
            a. Calcular la diferencia: diff = series_a[i] - series_b[i]
            b. Elevar al cuadrado: diff^2
            c. Acumular: suma_cuadrados += diff^2
        4. Calcular la raiz cuadrada del acumulador: sqrt(suma_cuadrados)
        5. Retornar el resultado.

    Analisis de complejidad:
        - Tiempo: O(n) donde n es la longitud de las series.
          Se realiza un solo recorrido con operaciones constantes por elemento.
        - Espacio: O(1) adicional, solo se usa el acumulador.
        - Es el algoritmo mas eficiente de todos los implementados.

    Args:
        series_a: Primera serie de tiempo (precios o retornos).
        series_b: Segunda serie de tiempo (precios o retornos).

    Returns:
        Distancia euclidiana entre las dos series.

    Raises:
        ValueError: Si las series tienen longitudes diferentes o estan vacias.
    """
    if len(series_a) != len(series_b):
        raise ValueError(
            f"Las series deben tener la misma longitud. "
            f"Recibidas: {len(series_a)} y {len(series_b)}"
        )

    n = len(series_a)
    if n == 0:
        raise ValueError("Las series no pueden estar vacias")

    suma_cuadrados = 0.0
    for i in range(n):
        diferencia = series_a[i] - series_b[i]
        suma_cuadrados += diferencia * diferencia

    return math.sqrt(suma_cuadrados)


def euclidean_distance_normalized(series_a: List[float], series_b: List[float]) -> float:
    """Calcula la distancia euclidiana normalizada entre dos series.

    La normalizacion se realiza dividiendo por la longitud de las series
    y aplicando raiz cuadrada, obteniendo una distancia promedio por punto.

        d_norm(X, Y) = sqrt(sum((xi - yi)^2) / n)

    Args:
        series_a: Primera serie de tiempo.
        series_b: Segunda serie de tiempo.

    Returns:
        Distancia euclidiana normalizada (RMSD - Root Mean Square Deviation).
    """
    if len(series_a) != len(series_b):
        raise ValueError(
            f"Las series deben tener la misma longitud. "
            f"Recibidas: {len(series_a)} y {len(series_b)}"
        )

    n = len(series_a)
    if n == 0:
        raise ValueError("Las series no pueden estar vacias")

    suma_cuadrados = 0.0
    for i in range(n):
        diferencia = series_a[i] - series_b[i]
        suma_cuadrados += diferencia * diferencia

    return math.sqrt(suma_cuadrados / n)


def euclidean_similarity_score(series_a: List[float], series_b: List[float]) -> float:
    """Calcula un puntaje de similitud basado en distancia euclidiana.

    Convierte la distancia en un puntaje de similitud en el rango [0, 1]
    usando la formula:

        sim(X, Y) = 1 / (1 + d(X, Y))

    donde d(X, Y) es la distancia euclidiana normalizada.

    Args:
        series_a: Primera serie de tiempo.
        series_b: Segunda serie de tiempo.

    Returns:
        Puntaje de similitud en [0, 1], donde 1 indica identidad perfecta.
    """
    dist = euclidean_distance_normalized(series_a, series_b)
    return 1.0 / (1.0 + dist)
