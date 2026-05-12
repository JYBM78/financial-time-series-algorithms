"""Script principal para analisis de similitud entre series de tiempo financieras.

Permite al usuario:
    1. Seleccionar dos activos del dataset unificado.
    2. Visualizar sus series temporales (precios y retornos).
    3. Calcular los valores de similitud con 4 algoritmos.
    4. Ver explicaciones matematicas y analisis de complejidad.
"""
import os
import sys
import time
from typing import List, Tuple, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Agregar el directorio raiz del proyecto al path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np

from src.requerimiento_2.algoritmos_similitud.similitud import (
    euclidean_distance,
    euclidean_distance_normalized,
    euclidean_similarity_score,
    pearson_correlation,
    interpret_correlation,
    dynamic_time_warping,
    dynamic_time_warping_normalized,
    dtw_similarity_score,
    get_dtw_path,
    cosine_similarity,
    cosine_angle,
    interpret_cosine_similarity,
)

UNIFIED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "precios_unificados.csv")


# =========================================================
# Funciones de carga y procesamiento de datos
# =========================================================

def cargar_datos_unificados() -> pd.DataFrame:
    """Carga el dataset unificado de precios.

    Returns:
        DataFrame con columnas [Date, Ticker, Open, High, Low, Close, Volume].

    Raises:
        FileNotFoundError: Si no existe el archivo unificado.
    """
    if not os.path.exists(UNIFIED_DATA_PATH):
        raise FileNotFoundError(
            f"No se encontro el archivo unificado en: {UNIFIED_DATA_PATH}\n"
            "Ejecute primero la etapa de unificacion (main.py)."
        )

    df = pd.read_csv(UNIFIED_DATA_PATH, parse_dates=['Date'])
    return df


def obtener_tickers_disponibles(df: pd.DataFrame) -> List[str]:
    """Obtiene la lista de tickers disponibles en el dataset.

    Args:
        df: DataFrame unificado.

    Returns:
        Lista de tickers ordenados alfabeticamente.
    """
    return sorted(df['Ticker'].unique().tolist())


def extraer_serie_precios(df: pd.DataFrame, ticker: str) -> Tuple[pd.Series, pd.Series]:
    """Extrae la serie de precios de cierre para un ticker.

    Args:
        df: DataFrame unificado.
        ticker: Identificador del activo.

    Returns:
        Tupla (fechas, precios) donde ambas son series alineadas.
    """
    serie = df[df['Ticker'] == ticker].copy()
    serie = serie.sort_values('Date').reset_index(drop=True)
    return serie['Date'], serie['Close']


def calcular_retornos(precios: pd.Series) -> pd.Series:
    """Calcula los retornos diarios porcentuales de una serie de precios.

    Retorno = (P_t - P_{t-1}) / P_{t-1}

    Args:
        precios: Serie de precios de cierre.

    Returns:
        Serie de retornos diarios (primer valor es NaN).
    """
    return precios.pct_change()


def alinear_series(
    fechas_a: pd.Series, retornos_a: pd.Series,
    fechas_b: pd.Series, retornos_b: pd.Series
) -> Tuple[np.ndarray, np.ndarray]:
    """Alinea los retornos de dos activos por fecha comun.

    Solo considera las fechas donde ambos activos tienen datos.

    Args:
        fechas_a, retornos_a: Fechas y retornos del activo A.
        fechas_b, retornos_b: Fechas y retornos del activo B.

    Returns:
        Tupla (retornos_a_alineados, retornos_b_alineados) como arrays numpy.
    """
    df_a = pd.DataFrame({'fecha': fechas_a.values, 'ret_a': retornos_a.values})
    df_b = pd.DataFrame({'fecha': fechas_b.values, 'ret_b': retornos_b.values})

    df = df_a.merge(df_b, on='fecha', how='inner')
    df = df.dropna(subset=['ret_a', 'ret_b'])

    return df['ret_a'].values, df['ret_b'].values


# =========================================================
# Funciones de visualizacion
# =========================================================

def graficar_series(
    fechas_a: pd.Series, precios_a: pd.Series, ticker_a: str,
    fechas_b: pd.Series, precios_b: pd.Series, ticker_b: str,
    retornos_a: pd.Series, retornos_b: pd.Series,
    ruta_salida: str
) -> None:
    """Genera graficos comparativos de dos activos.

    Crea una figura con 3 subplots:
        1. Precios de cierre normalizados (base 100).
        2. Retornos diarios.
        3. Retornos acumulados.

    Args:
        fechas_a, precios_a: Fechas y precios del activo A.
        ticker_a: Nombre del activo A.
        fechas_b, precios_b: Fechas y precios del activo B.
        ticker_b: Nombre del activo B.
        retornos_a, retornos_b: Retornos diarios de cada activo.
        ruta_salida: Ruta donde se guarda la imagen PNG.
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    fig.suptitle(f'Analisis Comparativo: {ticker_a} vs {ticker_b}', fontsize=16, fontweight='bold')

    # --- Subplot 1: Precios normalizados (base 100) ---
    precios_a_norm = precios_a / precios_a.iloc[0] * 100
    precios_b_norm = precios_b / precios_b.iloc[0] * 100

    axes[0].plot(fechas_a, precios_a_norm, label=ticker_a, linewidth=1.5, alpha=0.8)
    axes[0].plot(fechas_b, precios_b_norm, label=ticker_b, linewidth=1.5, alpha=0.8)
    axes[0].set_ylabel('Precio Normalizado (Base 100)')
    axes[0].set_title('Evolucion de Precios Normalizados')
    axes[0].legend(loc='upper left')
    axes[0].grid(True, alpha=0.3)

    # --- Subplot 2: Retornos diarios ---
    retornos_a_clean = retornos_a.dropna()
    retornos_b_clean = retornos_b.dropna()
    fechas_ret_a = fechas_a.iloc[retornos_a_clean.index]
    fechas_ret_b = fechas_b.iloc[retornos_b_clean.index]

    axes[1].plot(fechas_ret_a, retornos_a_clean, label=ticker_a, linewidth=0.7, alpha=0.7)
    axes[1].plot(fechas_ret_b, retornos_b_clean, label=ticker_b, linewidth=0.7, alpha=0.7)
    axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[1].set_ylabel('Retorno Diario')
    axes[1].set_title('Retornos Diarios')
    axes[1].legend(loc='upper left')
    axes[1].grid(True, alpha=0.3)

    # --- Subplot 3: Retornos acumulados ---
    ret_acum_a = (1 + retornos_a_clean).cumprod() - 1
    ret_acum_b = (1 + retornos_b_clean).cumprod() - 1

    axes[2].plot(fechas_ret_a, ret_acum_a, label=ticker_a, linewidth=1.5, alpha=0.8)
    axes[2].plot(fechas_ret_b, ret_acum_b, label=ticker_b, linewidth=1.5, alpha=0.8)
    axes[2].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[2].set_ylabel('Retorno Acumulado')
    axes[2].set_title('Retornos Acumulados')
    axes[2].legend(loc='upper left')
    axes[2].grid(True, alpha=0.3)
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Grafico guardado en: {ruta_salida}")


def graficar_dtw_path(
    series_a: np.ndarray, series_b: np.ndarray,
    ticker_a: str, ticker_b: str, ruta_salida: str
) -> None:
    """Grafica el camino de warping optimo de DTW.

    Args:
        series_a, series_b: Series de retornos alineadas.
        ticker_a, ticker_b: Nombres de los activos.
        ruta_salida: Ruta donde se guarda la imagen PNG.
    """
    camino = get_dtw_path(series_a.tolist(), series_b.tolist())

    fig, ax = plt.subplots(figsize=(8, 8))
    camino_array = np.array(camino)

    ax.plot(camino_array[:, 0], camino_array[:, 1], 'b-', linewidth=0.5, alpha=0.5, label='Camino DTW')
    ax.scatter(camino_array[:, 0], camino_array[:, 1], c='red', s=10, alpha=0.6)

    ax.set_xlabel(f'Indice {ticker_a}')
    ax.set_ylabel(f'Indice {ticker_b}')
    ax.set_title(f'Camino de Warping Optimio - DTW\n{ticker_a} vs {ticker_b}')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Grafico DTW guardado en: {ruta_salida}")


# =========================================================
# Funciones de analisis de similitud
# =========================================================

def ejecutar_analisis_similitud(
    retornos_a: np.ndarray, retornos_b: np.ndarray,
    ticker_a: str, ticker_b: str
) -> dict:
    """Ejecuta los 4 algoritmos de similitud sobre dos series de retornos.

    Args:
        retornos_a: Retornos diarios del activo A.
        retornos_b: Retornos diarios del activo B.
        ticker_a: Nombre del activo A.
        ticker_b: Nombre del activo B.

    Returns:
        Diccionario con los resultados de cada algoritmo.
    """
    lista_a = retornos_a.tolist()
    lista_b = retornos_b.tolist()
    resultados = {}

    # --- 1. Distancia Euclidiana ---
    t0 = time.perf_counter()
    dist_euclid = euclidean_distance(lista_a, lista_b)
    dist_euclid_norm = euclidean_distance_normalized(lista_a, lista_b)
    sim_euclid = euclidean_similarity_score(lista_a, lista_b)
    t1 = time.perf_counter()

    resultados['Distancia Euclidiana'] = {
        'valor': sim_euclid,
        'distancia': dist_euclid,
        'distancia_normalizada': dist_euclid_norm,
        'tiempo': t1 - t0,
    }

    # --- 2. Correlacion de Pearson ---
    t0 = time.perf_counter()
    r = pearson_correlation(lista_a, lista_b)
    t1 = time.perf_counter()

    resultados['Correlacion de Pearson'] = {
        'valor': r,
        'interpretacion': interpret_correlation(r),
        'tiempo': t1 - t0,
    }

    # --- 3. Dynamic Time Warping ---
    t0 = time.perf_counter()
    dtw_dist = dynamic_time_warping(lista_a, lista_b)
    dtw_dist_norm = dynamic_time_warping_normalized(lista_a, lista_b)
    dtw_sim = dtw_similarity_score(lista_a, lista_b)
    t1 = time.perf_counter()

    resultados['Dynamic Time Warping'] = {
        'valor': dtw_sim,
        'distancia': dtw_dist,
        'distancia_normalizada': dtw_dist_norm,
        'tiempo': t1 - t0,
    }

    # --- 4. Similitud por Coseno ---
    t0 = time.perf_counter()
    cos_sim = cosine_similarity(lista_a, lista_b)
    angulo = cosine_angle(lista_a, lista_b)
    t1 = time.perf_counter()

    resultados['Similitud por Coseno'] = {
        'valor': cos_sim,
        'angulo_grados': angulo,
        'interpretacion': interpret_cosine_similarity(cos_sim),
        'tiempo': t1 - t0,
    }

    return resultados


# =========================================================
# Documentacion y explicaciones
# =========================================================

def mostrar_explicacion_euclidiana() -> None:
    """Imprime la explicacion completa del algoritmo de Distancia Euclidiana."""
    print("\n" + "=" * 80)
    print("1. DISTANCIA EUCLIDIANA")
    print("=" * 80)
    print("""
FUNDAMENTACION MATEMATICA:
    La distancia euclidiana entre dos vectores X = (x1, x2, ..., xn) y
    Y = (y1, y2, ..., yn) se define como:

        d(X, Y) = sqrt( sum( (xi - yi)^2 ) )  para i = 1, ..., n

    Es la extension natural del teorema de Pitagoras al espacio n-dimensional.
    Para series de tiempo financieras, se aplica sobre retornos diarios para
    evitar problemas de no estacionariedad de los precios.

DESCRIPCION ALGORITMICA:
    1. Verificar que ambas series tengan la misma longitud n.
    2. Inicializar acumulador 'suma_cuadrados' = 0.
    3. Para cada indice i de 0 a n-1:
        a. diff = series_a[i] - series_b[i]
        b. suma_cuadrados += diff * diff
    4. Retornar sqrt(suma_cuadrados).

ANALISIS DE COMPLEJIDAD:
    - Tiempo: O(n) - Un solo recorrido lineal con operaciones constantes.
    - Espacio: O(1) - Solo se usa un acumulador escalar.
    - Es el algoritmo mas eficiente de los cuatro implementados.
    - Cada iteracion realiza: 1 resta, 1 multiplicacion, 1 suma.
    - Total de operaciones: ~3n + 1 (incluyendo la raiz cuadrada final).

VENTAJAS:
    - Computacionalmente eficiente.
    - Facil de interpretar: distancia geometrica directa.

LIMITACIONES:
    - Sensible a diferencias de escala.
    - No maneja desfases temporales entre series.
    - Requiere series de igual longitud.
    - Penaliza fuertemente valores atipicos (outliers).
""")


def mostrar_explicacion_pearson() -> None:
    """Imprime la explicacion completa del algoritmo de Correlacion de Pearson."""
    print("\n" + "=" * 80)
    print("2. CORRELACION DE PEARSON")
    print("=" * 80)
    print("""
FUNDAMENTACION MATEMATICA:
    El coeficiente de correlacion de Pearson r se define como:

        r = Cov(X, Y) / (sigma_X * sigma_Y)

    Desarrollando:

        r = sum((xi - x_media)(yi - y_media)) /
            sqrt( sum((xi - x_media)^2) * sum((yi - y_media)^2) )

    donde x_media y y_media son las medias aritmeticas de cada serie.

    Propiedades:
        - r en [-1, 1]
        - r = 1: correlacion lineal positiva perfecta
        - r = -1: correlacion lineal negativa perfecta
        - r = 0: sin correlacion lineal

DESCRIPCION ALGORITMICA:
    1. Calcular media_a = sum(series_a) / n
    2. Calcular media_b = sum(series_b) / n
    3. En un solo recorrido:
        - suma_cov += (series_a[i] - media_a) * (series_b[i] - media_b)
        - suma_var_a += (series_a[i] - media_a)^2
        - suma_var_b += (series_b[i] - media_b)^2
    4. denominador = sqrt(suma_var_a * suma_var_b)
    5. Si denominador == 0, retornar 0.
    6. Retornar suma_cov / denominador.

ANALISIS DE COMPLEJIDAD:
    - Tiempo: O(n) - Dos pasadas: una para medias, otra para covarianzas.
    - Espacio: O(1) - Solo acumuladores escalares.
    - Cada iteracion del segundo recorrido: 2 restas, 2 multiplicaciones,
      1 producto cruzado, 3 sumas = ~8 operaciones por elemento.
    - Total estimado: ~8n + 2n + 1 = ~10n operaciones.

VENTAJAS:
    - Invariante a escala y traslacion lineal.
    - Interpretacion estadistica bien establecida.
    - Robusto frente a diferencias de magnitud.

LIMITACIONES:
    - Solo captura relaciones lineales.
    - Sensible a outliers.
    - Requiere series de igual longitud.
    - No captura relaciones no lineales.
""")


def mostrar_explicacion_dtw() -> None:
    """Imprime la explicacion completa del algoritmo Dynamic Time Warping."""
    print("\n" + "=" * 80)
    print("3. DYNAMIC TIME WARPING (DTW)")
    print("=" * 80)
    print("""
FUNDAMENTACION MATEMATICA:
    DTW encuentra el alineamiento optimo entre dos series de tiempo
    mediante programacion dinamica. Se construye una matriz de costos
    acumulados D de dimension (n+1) x (m+1):

        D[i, j] = |xi - yj| + min(D[i-1, j], D[i, j-1], D[i-1, j-1])

    Condiciones de frontera:
        D[0, 0] = 0
        D[i, 0] = infinito (i > 0)
        D[0, j] = infinito (j > 0)

    La distancia DTW = D[n, m].

    Restricciones del camino de warping:
        - Boundary: inicia en (1,1), termina en (n,m).
        - Continuity: cada paso avanza maximo 1 posicion.
        - Monotonicity: nunca retrocede en el tiempo.

DESCRIPCION ALGORITMICA:
    1. Obtener n = len(series_a), m = len(series_b).
    2. Crear matriz D[n+1][m+1] inicializada en infinito, D[0][0] = 0.
    3. Para i de 1 a n:
        Para j de 1 a m:
            a. cost = abs(series_a[i-1] - series_b[j-1])
            b. D[i][j] = cost + min(D[i-1][j], D[i][j-1], D[i-1][j-1])
    4. Retornar D[n][m].

    Para recuperar el camino optimo (backtracking):
    1. Iniciar en (n, m).
    2. Mientras (i, j) != (0, 0):
        Mover al predecesor con menor costo D.
    3. Invertir la secuencia obtenida.

ANALISIS DE COMPLEJIDAD:
    - Tiempo: O(n * m) - Se llena una matriz completa.
      Si n = m: O(n^2) - Complejidad cuadratica.
    - Espacio: O(n * m) para la matriz completa.
      Optimizable a O(min(n, m)) si solo se necesita la distancia.
    - Es el algoritmo mas costoso de los cuatro.
    - Para n = 1000: ~1,000,000 operaciones vs ~1000 de los algoritmos O(n).

VENTAJAS:
    - Maneja series de diferente longitud.
    - Captura similitudes con desfases temporales.
    - Sensible a la forma de la curva, no solo valores absolutos.

LIMITACIONES:
    - Computacionalmente costoso (cuadratico).
    - Puede producir warping excesivo sin restricciones adicionales.
    - No tiene interpretacion estadistica directa.
""")


def mostrar_explicacion_coseno() -> None:
    """Imprime la explicacion completa del algoritmo de Similitud por Coseno."""
    print("\n" + "=" * 80)
    print("4. SIMILITUD POR COSENO")
    print("=" * 80)
    print("""
FUNDAMENTACION MATEMATICA:
    La similitud por coseno mide el coseno del angulo theta entre dos
    vectores en el espacio n-dimensional:

        cos(theta) = (X . Y) / (||X|| * ||Y||)

    donde:
        X . Y = sum(xi * yi)          (producto punto)
        ||X|| = sqrt(sum(xi^2))       (norma euclidiana)
        ||Y|| = sqrt(sum(yi^2))

    Propiedades:
        - cos(theta) en [-1, 1]
        - cos(theta) = 1: misma direccion (angulo 0 grados)
        - cos(theta) = 0: ortogonales (angulo 90 grados)
        - cos(theta) = -1: direcciones opuestas (angulo 180 grados)

    Diferencia con Pearson:
        - Pearson centra los datos (resta la media).
        - Coseno opera sobre valores originales sin centrar.
        - Para retornos con media ~0, ambos producen resultados similares.

DESCRIPCION ALGORITMICA:
    1. Inicializar: producto_punto = 0, suma_cuad_a = 0, suma_cuad_b = 0.
    2. Para cada indice i de 0 a n-1:
        a. producto_punto += series_a[i] * series_b[i]
        b. suma_cuad_a += series_a[i] * series_a[i]
        c. suma_cuad_b += series_b[i] * series_b[i]
    3. norma_a = sqrt(suma_cuad_a)
    4. norma_b = sqrt(suma_cuad_b)
    5. Si norma_a == 0 o norma_b == 0, retornar 0.
    6. Retornar producto_punto / (norma_a * norma_b).

ANALISIS DE COMPLEJIDAD:
    - Tiempo: O(n) - Un solo recorrido lineal.
    - Espacio: O(1) - Solo acumuladores escalares.
    - Cada iteracion: 2 multiplicaciones de auto-producto, 1 producto cruzado,
      3 sumas = ~6 operaciones por elemento.
    - Total estimado: ~6n + 2 (raices cuadradas).

VENTAJAS:
    - Invariante a escala (magnitud del vector).
    - Captura similitud de patron/direccion.
    - Eficiente computacionalmente.
    - Util para detectar activos con movimientos similares.

LIMITACIONES:
    - Insensible a diferencias de magnitud.
    - No captura relaciones no lineales.
    - Requiere series de igual longitud.
    - Puede ser enganoso si los retornos tienen media muy distinta de cero.
""")


def mostrar_comparacion_complejidades(n: int) -> None:
    """Imprime una comparacion de complejidades entre los 4 algoritmos.

    Args:
        n: Longitud aproximada de las series de tiempo.
    """
    print("\n" + "=" * 80)
    print("COMPARACION DE COMPLEJIDAD ALGORITMICA")
    print("=" * 80)
    print(f"""
{'Algoritmo':<30} {'Tiempo':<20} {'Espacio':<20}
{'-'*70}
{'Distancia Euclidiana':<30} {'O(n)':<20} {'O(1)':<20}
{'Correlacion de Pearson':<30} {'O(n)':<20} {'O(1)':<20}
{'Similitud por Coseno':<30} {'O(n)':<20} {'O(1)':<20}
{'Dynamic Time Warping':<30} {'O(n^2)':<20} {'O(n^2)':<20}

Estimacion de operaciones para n = {n}:
    - Euclidiana:     ~{3*n + 1:>10,} operaciones
    - Pearson:        ~{10*n:>10,} operaciones
    - Coseno:         ~{6*n + 2:>10,} operaciones
    - DTW:            ~{n*n:>10,} operaciones

Observaciones:
    - Los algoritmos O(n) son apropiados para series largas (miles de puntos).
    - DTW es util cuando se necesita tolerancia a desfases temporales,
      pero su costo cuadratico lo limita a series cortas o medianas.
    - Para series de {n} puntos, DTW requiere aprox. {n*n:,} celdas de memoria.
""")


# =========================================================
# Funcion principal
# =========================================================

def mostrar_menu_tickers(tickers: List[str]) -> None:
    """Muestra el menu de seleccion de tickers.

    Args:
        tickers: Lista de tickers disponibles.
    """
    print("\n" + "=" * 80)
    print("ALGORITMOS DE SIMILITUD DE SERIES DE TIEMPO")
    print("=" * 80)
    print("\nActivos disponibles:")
    for i, ticker in enumerate(tickers, 1):
        print(f"  {i:2d}. {ticker}")


def seleccionar_ticker(prompt: str, tickers: List[str]) -> str:
    """Solicita al usuario que seleccione un ticker del menu.

    Args:
        prompt: Mensaje a mostrar.
        tickers: Lista de tickers disponibles.

    Returns:
        Ticker seleccionado.
    """
    while True:
        try:
            opcion = int(input(f"\n{prompt} (1-{len(tickers)}): "))
            if 1 <= opcion <= len(tickers):
                return tickers[opcion - 1]
            print(f"  Opcion invalida. Ingrese un numero entre 1 y {len(tickers)}.")
        except ValueError:
            print("  Entrada invalida. Ingrese un numero.")


def main():
    """Funcion principal del analisis de similitud."""
    # Cargar datos
    print("Cargando datos unificados...")
    try:
        df = cargar_datos_unificados()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    tickers = obtener_tickers_disponibles(df)
    mostrar_menu_tickers(tickers)

    # Seleccionar activos
    ticker_a = seleccionar_ticker("Seleccione el PRIMER activo", tickers)
    ticker_b = seleccionar_ticker("Seleccione el SEGUNDO activo", tickers)

    if ticker_a == ticker_b:
        print("Error: Los activos deben ser diferentes.")
        return

    print(f"\nAnalizando similitud entre: {ticker_a} y {ticker_b}")
    print("-" * 60)

    # Extraer series
    fechas_a, precios_a = extraer_serie_precios(df, ticker_a)
    fechas_b, precios_b = extraer_serie_precios(df, ticker_b)

    retornos_a_raw = calcular_retornos(precios_a)
    retornos_b_raw = calcular_retornos(precios_b)

    # Alinear retornos por fecha comun
    retornos_a, retornos_b = alinear_series(
        fechas_a, retornos_a_raw,
        fechas_b, retornos_b_raw
    )

    n_puntos = len(retornos_a)
    print(f"  Puntos de datos alineados: {n_puntos}")
    print(f"  Periodo: {min(fechas_a.min(), fechas_b.min()).strftime('%Y-%m-%d')} a "
          f"{max(fechas_a.max(), fechas_b.max()).strftime('%Y-%m-%d')}")

    # Crear directorio de resultados
    os.makedirs("results/similarity", exist_ok=True)
    ruta_grafico = f"results/similarity/comparativa_{ticker_a.replace('.', '_')}_{ticker_b.replace('.', '_')}.png"
    ruta_dtw = f"results/similarity/dtw_path_{ticker_a.replace('.', '_')}_{ticker_b.replace('.', '_')}.png"

    # Generar visualizaciones
    print("\nGenerando visualizaciones...")
    graficar_series(
        fechas_a, precios_a, ticker_a,
        fechas_b, precios_b, ticker_b,
        retornos_a_raw, retornos_b_raw,
        ruta_grafico
    )
    graficar_dtw_path(retornos_a, retornos_b, ticker_a, ticker_b, ruta_dtw)

    # Ejecutar analisis de similitud
    print("\nEjecutando algoritmos de similitud...")
    resultados = ejecutar_analisis_similitud(retornos_a, retornos_b, ticker_a, ticker_b)

    # Mostrar resultados
    print("\n" + "=" * 80)
    print("RESULTADOS DE SIMILITUD")
    print("=" * 80)

    for nombre, datos in resultados.items():
        print(f"\n--- {nombre} ---")
        print(f"  Valor de similitud: {datos['valor']:.6f}")
        if 'distancia' in datos:
            print(f"  Distancia raw:    {datos['distancia']:.6f}")
        if 'distancia_normalizada' in datos:
            print(f"  Distancia norm.:  {datos['distancia_normalizada']:.6f}")
        if 'interpretacion' in datos:
            print(f"  Interpretacion:   {datos['interpretacion']}")
        if 'angulo_grados' in datos:
            print(f"  Angulo:           {datos['angulo_grados']:.2f} grados")
        print(f"  Tiempo ejecucion: {datos['tiempo']*1000:.3f} ms")

    # Mostrar comparacion de tiempos
    print("\n" + "-" * 60)
    print("Comparacion de tiempos de ejecucion:")
    for nombre, datos in resultados.items():
        t_ms = datos['tiempo'] * 1000
        barra_len = max(1, int(t_ms / max(d['tiempo'] for d in resultados.values()) * 40))
        barra = "#" * barra_len
        print(f"  {nombre:<25} {t_ms:10.3f} ms  {barra}")

    # Mostrar explicaciones detalladas
    mostrar_explicacion_euclidiana()
    mostrar_explicacion_pearson()
    mostrar_explicacion_dtw()
    mostrar_explicacion_coseno()
    mostrar_comparacion_complejidades(n_puntos)

    print("=" * 80)
    print("Analisis completado. Resultados guardados en results/similarity/")
    print("=" * 80)


if __name__ == "__main__":
    main()
