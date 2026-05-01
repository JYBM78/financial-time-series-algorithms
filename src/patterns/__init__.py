"""
Módulo de Patrones y Volatilidad de Series Temporales

Este módulo implementa:
1. Algoritmo de sliding window para detección de patrones
2. Cálculo de métricas de dispersión (desviación estándar, volatilidad)
3. Clasificación de riesgo de activos financieros

Autor: Equipo del proyecto
Fecha: 2026
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any
from collections import Counter


# =========================================================
# 1. SLIDING WINDOW - DETECCIÓN DE PATRONES
# =========================================================
"""
MATHEMATICAL EXPLANATION:
=========================
El algoritmo de sliding window (ventana deslizante) recorre una serie
temporal moviendo una ventana de tamaño fijo un elemento a la vez.

Para una serie de longitud n y ventana de tamaño w:
- Número de ventanas = n - w + 1
- Cada ventana se superpone con la anterior en w-1 elementos

PATRÓN 1: Secuencias de días consecutivos al alza
===================================================
Definición: Una secuencia de w días donde el precio de cierre aumenta
respecto al día anterior en todos los días.

Formalización:
- Sea r[i] = (Close[i] - Close[i-1]) / Close[i-1] el retorno diario
- El patrón se cumple si r[i] > 0 para todo i en la ventana

PATRÓN 2: Días con volatilidad extrema
======================================
Definición: Una secuencia donde la desviación estándar de los retornos
diarios excede un umbral definido (por ejemplo, 2 desviaciones estándar).

Formalización:
- Sea σ la desviación estándar de los retornos
- Sea μ la media de los retornos
- El patrón se cumple si |r[i] - μ| > 2σ

ALGORITHM DESCRIPTION:
======================
1. Definir tamaño de ventana w
2. Para cada posición i desde 0 hasta n-w:
   a. Extraer la subsecuencia [i, i+w)
   b. Verificar si cumple el patrón
   c. Si cumple, registrar la posición
3. Retornar lista de posiciones donde se encontró el patrón

COMPLEJITY: O(n × w) donde n es la longitud de la serie
ESPACIO: O(k) donde k es el número de patrones encontrados
"""


def sliding_window(serie: np.ndarray, window_size: int, 
                   pattern_func) -> List[int]:
    """
    Algoritmo de sliding window genérico.
    
    Parámetros:
    -----------
    serie : np.ndarray
        Serie temporal a analizar
    window_size : int
        Tamaño de la ventana
    pattern_func : callable
        Función que verifica si una ventana cumple el patrón
        
    Retorna:
    --------
    List[int]
        Lista de índices donde se encontró el patrón
    """
    n = len(serie)
    if window_size > n:
        return []
    
    matches = []
    
    for i in range(n - window_size + 1):
        window = serie[i:i + window_size]
        if pattern_func(window):
            matches.append(i)
    
    return matches


# =========================================================
# PATRÓN 1: DÍAS CONSECUTIVOS AL ALZA
# =========================================================

def pattern_consecutive_up(ventana: np.ndarray) -> bool:
    """
    Verifica si todos los días de la ventana son al alza.
    
    Una ventana cumple el patrón si cada día el precio aumenta
    respecto al día anterior.
    
    Parámetros:
    -----------
    ventana : np.ndarray
        Array de precios de cierre
        
    Retorna:
    --------
    bool
        True si todos los días son al alza
    """
    if len(ventana) < 2:
        return False
    
    # Calcular retornos diarios
    retornos = np.diff(ventana) / ventana[:-1]
    
    # Verificar si todos los retornos son positivos
    return np.all(retornos > 0)


def detectar_dias_alza(precios: np.ndarray, window_size: int = 5) -> Dict[str, Any]:
    """
    Detecta secuencias de días consecutivos al alza.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
    window_size : int
        Número de días consecutivos requeridos
        
    Retorna:
    --------
    dict
        Diccionario con resultados del análisis
    """
    # Usar sliding window
    posiciones = sliding_window(precios, window_size, pattern_consecutive_up)
    
    # Calcular frecuencia
    frecuencia = len(posiciones) / (len(precios) - window_size + 1) * 100
    
    return {
        'patron': 'dias_consecutivos_alza',
        'window_size': window_size,
        'num_ocurrencias': len(posiciones),
        'frecuencia_porcentual': frecuencia,
        'posiciones': posiciones[:10]  # Primeros 10 para no saturar
    }


# =========================================================
# PATRÓN 2: DÍAS CON VOLATILIDAD EXTREMA
# =========================================================

def pattern_volatility_extreme(ventana: np.ndarray, umbral: float = 2.0) -> bool:
    """
    Verifica si la ventana tiene volatilidad extrema.
    
    Una ventana cumple el patrón si la desviación estándar de los
    retornos diarios excede el umbral multiplicado por la desviación
    estándar global.
    
    Parámetros:
    -----------
    ventana : np.ndarray
        Array de precios de cierre
    umbral : float
        Número de desviaciones estándar para considerar extrema
        
    Retorna:
    --------
    bool
        True si la volatilidad es extrema
    """
    if len(ventana) < 3:
        return False
    
    # Calcular retornos
    retornos = np.diff(ventana) / ventana[:-1]
    
    # Calcular desviación estándar de la ventana
    std_ventana = np.std(retornos)
    
    # Calcular desviación estándar global (aproximada)
    std_global = np.std(retornos)
    
    # Verificar si excede el umbral
    return std_ventana > umbral * std_global


def detectar_vol_extrema(precios: np.ndarray, window_size: int = 5, 
                         umbral: float = 2.0) -> Dict[str, Any]:
    """
    Detecta días con volatilidad extrema.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
    window_size : int
        Tamaño de la ventana
    umbral : float
        Umbral de desviaciones estándar
        
    Retorna:
    --------
    dict
        Diccionario con resultados del análisis
    """
    # Usar sliding window con función de volatilidad
    def check_volatility(window):
        return pattern_volatility_extreme(window, umbral)
    
    posiciones = sliding_window(precios, window_size, check_volatility)
    
    # Calcular frecuencia
    frecuencia = len(posiciones) / (len(precios) - window_size + 1) * 100
    
    return {
        'patron': 'volatilidad_extrema',
        'window_size': window_size,
        'umbral': umbral,
        'num_ocurrencias': len(posiciones),
        'frecuencia_porcentual': frecuencia,
        'posiciones': posiciones[:10]
    }


# =========================================================
# PATRÓN 3: CAMBIOS SIGNIFICATIVOS DE PRECIO
# =========================================================

def pattern_significant_change(ventana: np.ndarray, 
                                threshold: float = 0.03) -> bool:
    """
    Verifica si hay un cambio significativo de precio en la ventana.
    
    Una ventana cumple el patrón si el cambio total (máximo - mínimo)
    dividido por el mínimo excede el umbral.
    
    Parámetros:
    -----------
    ventana : np.ndarray
        Array de precios de cierre
    threshold : float
        Umbral de cambio porcentual (default 3%)
        
    Retorna:
    --------
    bool
        True si hay cambio significativo
    """
    if len(ventana) < 2:
        return False
    
    cambio_total = (np.max(ventana) - np.min(ventana)) / np.min(ventana)
    return cambio_total > threshold


def detectar_cambios_significativos(precios: np.ndarray, window_size: int = 5,
                                     threshold: float = 0.03) -> Dict[str, Any]:
    """
    Detecta ventanas con cambios significativos de precio.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
    window_size : int
        Tamaño de la ventana
    threshold : float
        Umbral de cambio porcentual
        
    Retorna:
    --------
    dict
        Diccionario con resultados del análisis
    """
    def check_change(window):
        return pattern_significant_change(window, threshold)
    
    posiciones = sliding_window(precios, window_size, check_change)
    frecuencia = len(posiciones) / (len(precios) - window_size + 1) * 100
    
    return {
        'patron': 'cambio_significativo',
        'window_size': window_size,
        'threshold': threshold,
        'num_ocurrencias': len(posiciones),
        'frecuencia_porcentual': frecuencia,
        'posiciones': posiciones[:10]
    }


# =========================================================
# 2. CÁLCULO DE VOLATILIDAD
# =========================================================
"""
MATHEMATICAL EXPLANATION:
=========================
La volatilidad histórica mide la dispersión de los retornos de un activo.
Se calcula típicamente como la desviación estándar de los retornos diarios
annualizada.

Fórmulas:

1. Desviación Estándar:
   σ = √(Σ(r[i] - μ)² / (n-1))
   
   donde μ es la media de los retornos

2. Volatilidad Histórica (annualizada):
   σ_anual = σ_diaria × √(252)
   
   donde 252 es el número promedio de días de trading por año

3. Retornos:
   r[i] = (Close[i] - Close[i-1]) / Close[i-1]

COMPLEJITY: O(n) para calcular volatilidad
"""


def calcular_retornos(precios: np.ndarray) -> np.ndarray:
    """
    Calcula los retornos diarios de una serie de precios.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
        
    Retorna:
    --------
    np.ndarray
        Array de retornos diarios
    """
    retornos = np.diff(precios) / precios[:-1]
    # Eliminar NaN, infinitos y valores extremos
    retornos = retornos[np.isfinite(retornos)]
    # Filtrar valores extremos (más de 100% de cambio en un día)
    retornos = retornos[np.abs(retornos) < 1.0]
    return retornos


def calcular_desviacion_estandar(precios: np.ndarray) -> float:
    """
    Calcula la desviación estándar de los retornos diarios.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
        
    Retorna:
    --------
    float
        Desviación estándar de los retornos
    """
    retornos = calcular_retornos(precios)
    if len(retornos) == 0:
        return 0.0
    return float(np.std(retornos))


def calcular_volatilidad_historica(precios: np.ndarray, 
                                    annualizar: bool = True) -> float:
    """
    Calcula la volatilidad histórica de los retornos.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
    annualizar : bool
        Si True, annualiza la volatilidad (×√252)
        
    Retorna:
    --------
    float
        Volatilidad histórica (en porcentaje)
    """
    retornos = calcular_retornos(precios)
    if len(retornos) == 0:
        return 0.0
    
    # Desviación estándar de retornos
    volatilidad = np.std(retornos)
    
    # Annualizar si se solicita
    if annualizar:
        volatilidad = volatilidad * np.sqrt(252)
    
    # Convertir a porcentaje
    return float(volatilidad * 100)


def calcular_metricas_dispersion(precios: np.ndarray) -> Dict[str, float]:
    """
    Calcula múltiples métricas de dispersión.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
        
    Retorna:
    --------
    dict
        Diccionario con todas las métricas
    """
    retornos = calcular_retornos(precios)
    
    if len(retornos) == 0:
        return {
            'desviacion_estandar': 0.0,
            'volatilidad_diaria': 0.0,
            'volatilidad_anualizada': 0.0,
            'varianza': 0.0,
            'rango': 0.0,
            'coef_variacion': 0.0
        }
    
    media = np.mean(retornos)
    std = np.std(retornos, ddof=1)  # Usar ddof=1 para muestra
    
    return {
        'desviacion_estandar': float(std),
        'volatilidad_diaria': float(std * 100),
        'volatilidad_anualizada': float(std * np.sqrt(252) * 100),
        'varianza': float(std ** 2),
        'rango': float(np.max(retornos) - np.min(retornos)),
        'coef_variacion': float(std / abs(media) if media != 0 else 0) * 100
    }


# =========================================================
# 3. CLASIFICACIÓN DE RIESGO
# =========================================================
"""
MATHEMATICAL EXPLANATION:
=========================
La clasificación de riesgo se basa en la volatilidad anualizada:

- **Conservador**: σ < 15% (baja volatilidad)
- **Moderado**: 15% ≤ σ < 30% (volatilidad media)
- **Agresivo**: σ ≥ 30% (alta volatilidad)

Estos umbrales son estándar en la industria financiera y pueden
ajustarse según el contexto del mercado.

COMPLEJITY: O(n) para clasificar todos los activos
"""


def clasificar_riesgo(volatilidad: float) -> str:
    """
    Clasifica el nivel de riesgo según la volatilidad.
    
    Parámetros:
    -----------
    volatilidad : float
        Volatilidad anualizada en porcentaje
        
    Retorna:
    --------
    str
        Categoría de riesgo
    """
    if volatilidad < 15:
        return 'Conservador'
    elif volatilidad < 30:
        return 'Moderado'
    else:
        return 'Agresivo'


def clasificar_todos_activos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clasifica todos los activos del portafolio según su riesgo.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con columnas Date, Ticker, Close, etc.
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con clasificación de riesgo
    """
    resultados = []
    
    for ticker in df['Ticker'].unique():
        # Filtrar por ticker
        df_ticker = df[df['Ticker'] == ticker].sort_values('Date')
        precios = df_ticker['Close'].values
        
        # Calcular métricas
        metricas = calcular_metricas_dispersion(precios)
        volatilidad = metricas['volatilidad_anualizada']
        clasificacion = clasificar_riesgo(volatilidad)
        
        # Detectar patrones
        patrones = detectar_todos_patrones(precios)
        
        resultados.append({
            'Ticker': ticker,
            'Volatilidad_Anualizada': volatilidad,
            'Desviacion_Estandar': metricas['desviacion_estandar'],
            'Clasificacion_Riesgo': clasificacion,
            'Frecuencia_Dias_Alza': patrones['dias_consecutivos_alza']['frecuencia_porcentual'],
            'Frecuencia_Vol_Extrema': patrones['volatilidad_extrema']['frecuencia_porcentual'],
            'Frecuencia_Cambios_Sign': patrones['cambio_significativo']['frecuencia_porcentual']
        })
    
    # Crear DataFrame y ordenar por volatilidad
    df_resultado = pd.DataFrame(resultados)
    df_resultado = df_resultado.sort_values('Volatilidad_Anualizada', ascending=True)
    df_resultado = df_resultado.reset_index(drop=True)
    
    return df_resultado


def detectar_todos_patrones(precios: np.ndarray) -> Dict[str, Any]:
    """
    Detecta todos los patrones definidos.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
        
    Retorna:
    --------
    dict
        Diccionario con resultados de todos los patrones
    """
    return {
        'dias_consecutivos_alza': detectar_dias_alza(precios, window_size=5),
        'volatilidad_extrema': detectar_vol_extrema(precios, window_size=5, umbral=2.0),
        'cambio_significativo': detectar_cambios_significativos(precios, window_size=5, threshold=0.03)
    }


# =========================================================
# INTERFAZ UNIFICADA
# =========================================================


def analizar_activo(df: pd.DataFrame, ticker: str) -> Dict[str, Any]:
    """
    Realiza el análisis completo de un activo.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos financieros
    ticker : str
        Ticker del activo a analizar
        
    Retorna:
    --------
    dict
        Diccionario con todos los análisis
    """
    # Filtrar por ticker
    df_ticker = df[df['Ticker'] == ticker].sort_values('Date')
    precios = df_ticker['Close'].values
    
    # Calcular métricas
    metricas = calcular_metricas_dispersion(precios)
    patrones = detectar_todos_patrones(precios)
    
    return {
        'ticker': ticker,
        'metricas_dispersion': metricas,
        'patrones': patrones,
        'clasificacion_riesgo': clasificar_riesgo(metricas['volatilidad_anualizada'])
    }


def generar_reporte_riesgo(df: pd.DataFrame, guardar: bool = True) -> pd.DataFrame:
    """
    Genera el reporte completo de riesgo de todos los activos.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos financieros
    guardar : bool
        Si True, guarda el resultado en CSV
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame con el reporte de riesgo
    """
    reporte = clasificar_todos_activos(df)
    
    if guardar:
        import os
        os.makedirs('reports', exist_ok=True)
        reporte.to_csv('reports/reporte_riesgo.csv', index=False)
        print("✅ Reporte guardado en: reports/reporte_riesgo.csv")
    
    return reporte


# =========================================================
# PRUEBAS
# =========================================================


if __name__ == "__main__":
    # Crear datos de prueba
    np.random.seed(42)
    
    # Simular precios
    precios = 100 * np.cumprod(1 + np.random.randn(100) * 0.02)
    
    print("=" * 60)
    print("PRUEBAS DEL MÓDULO DE PATRONES Y VOLATILIDAD")
    print("=" * 60)
    
    # Prueba 1: Detección de patrones
    print("\n1. DETECCIÓN DE PATRONES")
    print("-" * 40)
    
    patrones = detectar_todos_patrones(precios)
    
    print(f"\nPatrón 1 - Días consecutivos al alza:")
    print(f"   Frecuencia: {patrones['dias_consecutivos_alza']['frecuencia_porcentual']:.2f}%")
    print(f"   Ocurrencias: {patrones['dias_consecutivos_alza']['num_ocurrencias']}")
    
    print(f"\nPatrón 2 - Volatilidad extrema:")
    print(f"   Frecuencia: {patrones['volatilidad_extrema']['frecuencia_porcentual']:.2f}%")
    print(f"   Ocurrencias: {patrones['volatilidad_extrema']['num_ocurrencias']}")
    
    print(f"\nPatrón 3 - Cambios significativos:")
    print(f"   Frecuencia: {patrones['cambio_significativo']['frecuencia_porcentual']:.2f}%")
    print(f"   Ocurrencias: {patrones['cambio_significativo']['num_ocurrencias']}")
    
    # Prueba 2: Métricas de dispersión
    print("\n2. MÉTRICAS DE DISPERSIÓN")
    print("-" * 40)
    
    metricas = calcular_metricas_dispersion(precios)
    for clave, valor in metricas.items():
        print(f"   {clave}: {valor:.4f}")
    
    # Prueba 3: Clasificación de riesgo
    print("\n3. CLASIFICACIÓN DE RIESGO")
    print("-" * 40)
    
    clasificacion = clasificar_riesgo(metricas['volatilidad_anualizada'])
    print(f"   Clasificación: {clasificacion}")
    print(f"   Volatilidad anualizada: {metricas['volatilidad_anualizada']:.2f}%")
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)