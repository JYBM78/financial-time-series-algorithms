"""Correlacion de Pearson para series de tiempo financieras.

Mide la relacion lineal entre dos activos. Valores cercanos a 1 indican
correlacion positiva fuerte, cercanos a -1 correlacion negativa fuerte,
y cercanos a 0 ausencia de relacion lineal.
"""
import math
from typing import List, Tuple


def pearson_correlation(series_a: List[float], series_b: List[float]) -> float:
    """Calcula el coeficiente de correlacion de Pearson entre dos series.

    Fundamentacion matematica:
        El coeficiente de correlacion de Pearson r entre dos variables
        X = (x1, x2, ..., xn) y Y = (y1, y2, ..., yn) se define como:

            r = sum((xi - x_media)(yi - y_media)) / sqrt(sum((xi - x_media)^2) * sum((yi - y_media)^2))

        Equivalentemente:
            r = Cov(X, Y) / (sigma_X * sigma_Y)

        donde:
            x_media = sum(xi) / n
            y_media = sum(yi) / n
            Cov(X, Y) = sum((xi - x_media)(yi - y_media)) / n
            sigma_X = sqrt(sum((xi - x_media)^2) / n)
            sigma_Y = sqrt(sum((yi - y_media)^2) / n)

        Propiedades:
            - r esta en el rango [-1, 1]
            - r = 1: correlacion lineal positiva perfecta
            - r = -1: correlacion lineal negativa perfecta
            - r = 0: sin correlacion lineal

    Descripcion algoritmica:
        1. Verificar que ambas series tengan la misma longitud n >= 2.
        2. Calcular la media de cada serie:
            a. suma_a = sum(series_a[i] for i in 0..n-1)
            b. suma_b = sum(series_b[i] for i in 0..n-1)
            c. media_a = suma_a / n
            d. media_b = suma_b / n
        3. Calcular en un solo recorrido:
            a. suma_cov = sum((series_a[i] - media_a) * (series_b[i] - media_b))
            b. suma_var_a = sum((series_a[i] - media_a)^2)
            c. suma_var_b = sum((series_b[i] - media_b)^2)
        4. Calcular el denominador: denominador = sqrt(suma_var_a * suma_var_b)
        5. Si denominador es 0, retornar 0 (varianza nula en alguna serie).
        6. Retornar r = suma_cov / denominador.

    Analisis de complejidad:
        - Tiempo: O(n) donde n es la longitud de las series.
          Se realizan dos recorridos: uno para medias, otro para covarianzas.
          Ambas pasadas son O(n), por lo que el total es O(n).
        - Espacio: O(1) adicional, solo acumuladores escalares.
        - Misma complejidad que Euclidiana pero con mas operaciones por elemento.

    Interpretacion financiera:
        - Para analisis de series de tiempo financieras, se recomienda aplicar
          sobre RETORNOS en lugar de precios absolutos, ya que los precios
          suelen ser no estacionarios y producen correlaciones espurias.

    Args:
        series_a: Primera serie de tiempo (preferiblemente retornos).
        series_b: Segunda serie de tiempo (preferiblemente retornos).

    Returns:
        Coeficiente de correlacion de Pearson en el rango [-1, 1].

    Raises:
        ValueError: Si las series tienen longitudes diferentes o n < 2.
    """
    if len(series_a) != len(series_b):
        raise ValueError(
            f"Las series deben tener la misma longitud. "
            f"Recibidas: {len(series_a)} y {len(series_b)}"
        )

    n = len(series_a)
    if n < 2:
        raise ValueError("Se requieren al menos 2 puntos para calcular la correlacion")

    # Paso 2: Calcular medias
    suma_a = 0.0
    suma_b = 0.0
    for i in range(n):
        suma_a += series_a[i]
        suma_b += series_b[i]

    media_a = suma_a / n
    media_b = suma_b / n

    # Paso 3: Calcular covarianza y varianzas en un solo recorrido
    suma_cov = 0.0
    suma_var_a = 0.0
    suma_var_b = 0.0
    for i in range(n):
        diff_a = series_a[i] - media_a
        diff_b = series_b[i] - media_b
        suma_cov += diff_a * diff_b
        suma_var_a += diff_a * diff_a
        suma_var_b += diff_b * diff_b

    # Paso 4-6: Calcular correlacion
    denominador = math.sqrt(suma_var_a * suma_var_b)

    if denominador == 0.0:
        return 0.0

    return suma_cov / denominador


def interpret_correlation(r: float) -> str:
    """Interpreta el valor de correlacion de Pearson en terminos financieros.

    Args:
        r: Coeficiente de correlacion de Pearson.

    Returns:
        Descripcion textual de la interpretacion.
    """
    abs_r = abs(r)
    if abs_r >= 0.9:
        nivel = "Muy fuerte"
    elif abs_r >= 0.7:
        nivel = "Fuerte"
    elif abs_r >= 0.5:
        nivel = "Moderada"
    elif abs_r >= 0.3:
        nivel = "Debil"
    else:
        nivel = "Muy debil o inexistente"

    if r > 0:
        direccion = "positiva"
    elif r < 0:
        direccion = "negativa"
    else:
        direccion = "nula"

    return f"Correlacion {nivel} ({direccion}): r = {r:.4f}"
