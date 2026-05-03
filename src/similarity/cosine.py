"""Similitud por coseno aplicada a vectores de rendimientos diarios.

Mide el angulo entre dos vectores de rendimientos. Es independiente de
la magnitud y solo captura la similitud en la direccion/patron de los
movimientos del activo.
"""
import math
from typing import List, Tuple


def cosine_similarity(series_a: List[float], series_b: List[float]) -> float:
    """Calcula la similitud por coseno entre dos series de tiempo.

    Fundamentacion matematica:
        La similitud por coseno entre dos vectores X = (x1, x2, ..., xn) y
        Y = (y1, y2, ..., yn) se define como el coseno del angulo theta
        entre ellos en el espacio n-dimensional:

            cos(theta) = (X . Y) / (||X|| * ||Y||)

        donde:
            X . Y = sum(xi * yi)        (producto punto)
            ||X|| = sqrt(sum(xi^2))     (norma euclidiana de X)
            ||Y|| = sqrt(sum(yi^2))     (norma euclidiana de Y)

        Propiedades:
            - cos(theta) esta en el rango [-1, 1]
            - cos(theta) = 1: los vectores apuntan en la misma direccion (angulo 0)
            - cos(theta) = 0: los vectores son ortogonales (angulo 90 grados)
            - cos(theta) = -1: los vectores apuntan en direcciones opuestas (angulo 180)

        Diferencia clave con la correlacion de Pearson:
            - Pearson centra los datos restando la media antes de calcular.
            - Coseno opera sobre los valores originales sin centrar.
            - Pearson mide relacion lineal; coseno mide similitud de patron/direccion.
            - Para retornos financieros con media cercana a 0, ambos son similares.

    Descripcion algoritmica:
        1. Verificar que ambas series tengan la misma longitud n > 0.
        2. Calcular en un solo recorrido:
            a. producto_punto = sum(series_a[i] * series_b[i] for i in 0..n-1)
            b. norma_a = sqrt(sum(series_a[i]^2 for i in 0..n-1))
            c. norma_b = sqrt(sum(series_b[i]^2 for i in 0..n-1))
        3. Si norma_a == 0 o norma_b == 0, retornar 0 (vector nulo).
        4. Retornar cos = producto_punto / (norma_a * norma_b).

    Analisis de complejidad:
        - Tiempo: O(n) donde n es la longitud de las series.
          Un solo recorrido para calcular producto punto y ambas normas.
        - Espacio: O(1) adicional, solo acumuladores escalares.
        - Misma complejidad asintotica que Euclidiana y Pearson.

    Uso en finanzas:
        - Se aplica sobre vectores de RETORNOS diarios, no sobre precios.
        - Captura si dos activos tienden a moverse en la misma direccion.
        - Util en identificacion de activos con patrones de movimiento similares.
        - Insensible a diferencias de escala: un activo con retornos de 0.01
          y otro con 0.10 pueden tener coseno = 1 si sus patrones son identicos.

    Args:
        series_a: Primera serie de tiempo (preferiblemente retornos).
        series_b: Segunda serie de tiempo (preferiblemente retornos).

    Returns:
        Similitud por coseno en el rango [-1, 1].

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

    # Calcular producto punto y normas en un solo recorrido
    producto_punto = 0.0
    suma_cuad_a = 0.0
    suma_cuad_b = 0.0

    for i in range(n):
        producto_punto += series_a[i] * series_b[i]
        suma_cuad_a += series_a[i] * series_a[i]
        suma_cuad_b += series_b[i] * series_b[i]

    norma_a = math.sqrt(suma_cuad_a)
    norma_b = math.sqrt(suma_cuad_b)

    if norma_a == 0.0 or norma_b == 0.0:
        return 0.0

    return producto_punto / (norma_a * norma_b)


def cosine_angle(series_a: List[float], series_b: List[float]) -> float:
    """Calcula el angulo en grados entre dos series de tiempo.

    Convierte la similitud por coseno al angulo correspondiente en grados.

    Args:
        series_a: Primera serie de tiempo.
        series_b: Segunda serie de tiempo.

    Returns:
        Angulo en grados entre 0 y 180.
    """
    cos_sim = cosine_similarity(series_a, series_b)
    # Clamp para evitar errores de precision en acos
    cos_sim = max(-1.0, min(1.0, cos_sim))
    angulo_rad = math.acos(cos_sim)
    return math.degrees(angulo_rad)


def interpret_cosine_similarity(cos: float) -> str:
    """Interpreta el valor de similitud por coseno.

    Args:
        cos: Similitud por coseno.

    Returns:
        Descripcion textual de la interpretacion.
    """
    if cos >= 0.9:
        nivel = "Muy similar"
    elif cos >= 0.7:
        nivel = "Similar"
    elif cos >= 0.5:
        nivel = "Moderadamente similar"
    elif cos >= 0.3:
        nivel = "Poco similar"
    else:
        nivel = "Dissimilar"

    angulo = math.degrees(math.acos(max(-1.0, min(1.0, cos))))
    return f"{nivel}: cos(theta) = {cos:.4f}, angulo = {angulo:.2f} grados"
