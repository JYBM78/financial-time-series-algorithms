"""
Aplicación Interactiva de Similitud de Series Temporales
=========================================================

Este script permite al usuario:
1. Seleccionar dos activos del portafolio
2. Visualizar sus series temporales
3. Ver los valores de similitud calculados por cada algoritmo
4. Leer la explicación matemática y algorítmica de cada método
5. Analizar la complejidad computacional

Ejecutar con: python scripts/app_similarity.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

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
    comparar_activos
)


# =========================================================
# EXPLICACIONES MATEMÁTICAS Y ALGORÍTMICAS
# =========================================================

EXPLICACIONES = {
    'distancia_euclidiana': {
        'nombre': 'Distancia Euclidiana',
        'formula': 'd(x, y) = √(Σ(xi - yi)²)',
        'descripcion': '''
La distancia euclidiana mide la distancia geométrica directa entre dos 
puntos en el espacio n-dimensional. En series temporales, compara 
cada punto correspondiente de las dos secuencias.

PASOS DEL ALGORITMO:
1. Alinear las series por índice temporal
2. Calcular diferencia elemento a elemento: di = xi - yi
3. Elevar cada diferencia al cuadrado: di²
4. Sumar todas las diferencias al cuadrado: Σdi²
5. Extraer raíz cuadrada: √(Σdi²)
''',
        'complejidad': 'O(n) - Lineal',
        'espacio': 'O(n) - Necesita almacenar las series',
        'ventajas': [
            'Simple de implementar',
            'Intuitiva y fácil de interpretar',
            'Computacionalmente eficiente'
        ],
        'desventajas': [
            'Sensible a outliers',
            'No considera la escala de los datos',
            'No captura relaciones no lineales'
        ]
    },
    
    'correlacion_pearson': {
        'nombre': 'Correlación de Pearson',
        'formula': 'r = Σ(xi - x̄)(yi - ȳ) / √(Σ(xi - x̄)² × Σ(yi - ȳ)²)',
        'descripcion': '''
El coeficiente de correlación de Pearson mide la relación lineal entre 
dos variables. Valores cercanos a 1 indican correlación positiva, 
valores cercanos a -1 indican correlación negativa.

PASOS DEL ALGORITMO:
1. Calcular la media de cada serie: x̄, ȳ
2. Calcular desviaciones: d1i = xi - x̄, d2i = yi - ȳ
3. Calcular covarianza: Σ(d1i × d2i)
4. Calcular producto de varianzas: √(Σd1i² × Σd2i²)
5. Dividir covarianza por producto de varianzas
''',
        'complejidad': 'O(n) - Lineal',
        'espacio': 'O(n) - Necesita almacenar las series',
        'ventajas': [
            'Normalizada entre -1 y 1',
            'Captura relaciones lineales',
            'Invariante a cambios de escala'
        ],
        'desventajas': [
            'Solo detecta relaciones lineales',
            'Sensible a outliers',
            'No captura relaciones no lineales'
        ]
    },
    
    'dtw': {
        'nombre': 'Dynamic Time Warping (DTW)',
        'formula': 'DTW(i,j) = d(i,j) + min(DTW(i-1,j), DTW(i,j-1), DTW(i-1,j-1))',
        'descripcion': '''
DTW es un algoritmo de programación dinámica que encuentra el 
alineamiento óptimo entre dos secuencias que pueden diferir en 
velocidad o fase. Permite comparar series con desfases temporales.

PASOS DEL ALGORITMO:
1. Crear matriz de costos n×m
2. Inicializar primera fila y columna
3. Para cada celda (i,j):
   - Calcular costo local: (xi - yj)²
   - Agregar el mínimo de las celdas adyacentes
4. La distancia DTW está en la celda (n,m)
5. Reconstruir ruta de alineamiento (opcional)
''',
        'complejidad': 'O(n × m) - Cuadrática',
        'espacio': 'O(n × m) - Matriz de costos',
        'ventajas': [
            'Maneja series de diferente longitud',
            'Tolera desfases temporales',
            'Captura patrones similares aunque estén desfasados'
        ],
        'desventajas': [
            'Alta complejidad computacional',
            'Mayor consumo de memoria',
            'Puede generar alineamientos no deseados'
        ]
    },
    
    'similitud_coseno': {
        'nombre': 'Similitud por Coseno',
        'formula': 'cos(θ) = (A · B) / (||A|| × ||B||)',
        'descripcion': '''
La similitud por coseno mide el ángulo entre dos vectores en el 
espacio n-dimensional. Es especialmente útil para comparar 
direcciones o patrones, ignorando la magnitud.

PASOS DEL ALGORITMO:
1. Calcular producto punto: A · B = Σ(xi × yi)
2. Calcular norma de cada vector: ||A|| = √(Σxi²)
3. Dividir producto punto por producto de normas
4. Convertir a distancia: distancia = 1 - similitud
''',
        'complejidad': 'O(n) - Lineal',
        'espacio': 'O(1) - Solo variables escalares',
        'ventajas': [
            'Muy eficiente computacionalmente',
            'Invariante a la magnitud',
            'Funciona bien con vectores dispersos'
        ],
        'desventajas': [
            'No considera el origen de las series',
            'Asume relaciones lineales',
            'Puede ser sensible a la dimensionalidad'
        ]
    }
}


def cargar_datos():
    """Carga los datos unificados del proyecto."""
    data_path = project_root / "data" / "processed" / "precios_unificados.csv"
    
    if not data_path.exists():
        print("❌ Error: No se encontró el archivo de datos")
        print("   Por favor ejecuta primero: python main.py")
        return None
    
    df = pd.read_csv(data_path, parse_dates=['Date'])
    return df


def mostrar_menu_activos(df):
    """Muestra el menú de activos disponibles."""
    tickers = sorted(df['Ticker'].unique().tolist())
    
    print("\n" + "=" * 60)
    print("ACTIVOS DISPONIBLES")
    print("=" * 60)
    
    # Mostrar en columnas
    for i in range(0, len(tickers), 4):
        fila = tickers[i:i+4]
        print("  " + "  ".join(f"{t:15}" for t in fila))
    
    return tickers


def seleccionar_activo(tickers, num):
    """Permite seleccionar un activo."""
    while True:
        try:
            seleccion = input(f"\n👉 Selecciona el activo #{num} (escribe el nombre): ").strip().upper()
            
            if seleccion in tickers:
                return seleccion
            
            # Buscar coincidencia parcial
            coincidencias = [t for t in tickers if seleccion in t]
            if len(coincidencias) == 1:
                print(f"   ¿Querías decir {coincidencias[0]}? Usándolo...")
                return coincidencias[0]
            elif len(coincidencias) > 0:
                print(f"   Coincidencias: {coincidencias}")
                print("   Por favor sé más específico.")
            else:
                print(f"   ❌ '{seleccion}' no encontrado. Intenta de nuevo.")
                print(f"   Activos disponibles: {tickers}")
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            sys.exit(0)


def mostrar_resultados(resultado):
    """Muestra los resultados de similitud de forma formateada."""
    print("\n" + "=" * 60)
    print(f"📊 RESULTADOS: {resultado['ticker1']} vs {resultado['ticker2']}")
    print("=" * 60)
    
    print("\n📈 MÉTRICAS DE SIMILITUD:")
    print("-" * 40)
    print(f"  Distancia Euclidiana:           {resultado['distancia_euclidiana']:.6f}")
    print(f"  Distancia Euclidiana Normalizada: {resultado['distancia_euclidiana_normalizada']:.6f}")
    print(f"  Correlación de Pearson:          {resultado['correlacion_pearson']:.6f}")
    print(f"  Distancia DTW:                  {resultado['dtw']:.6f}")
    print(f"  Similitud por Coseno:            {resultado['similitud_coseno']:.6f}")
    print(f"  Distancia por Coseno:            {resultado['distancia_coseno']:.6f}")


def mostrar_explicacion(metodo):
    """Muestra la explicación detallada de un algoritmo."""
    info = EXPLICACIONES.get(metodo)
    if not info:
        return
    
    print("\n" + "=" * 60)
    print(f"📚 EXPLICACIÓN: {info['nombre']}")
    print("=" * 60)
    
    print(f"\n📐 FÓRMULA:")
    print(f"   {info['formula']}")
    
    print(f"\n📝 DESCRIPCIÓN ALGORÍTMICA:{info['descripcion']}")
    
    print(f"\n⏱️  COMPLEJIDAD COMPUTACIONAL:")
    print(f"   Tiempo: {info['complejidad']}")
    print(f"   Espacio: {info['espacio']}")
    
    print(f"\n✅ VENTAJAS:")
    for v in info['ventajas']:
        print(f"   • {v}")
    
    print(f"\n⚠️  DESVENTAJAS:")
    for d in info['desventajas']:
        print(f"   • {d}")


def mostrar_todas_explicaciones():
    """Muestra las explicaciones de todos los algoritmos."""
    for metodo in EXPLICACIONES.keys():
        mostrar_explicacion(metodo)
        input("\n   Presiona Enter para continuar...")
    

def comparar_activos_interactivo(df):
    """Función principal interactiva."""
    print("\n" + "=" * 60)
    print("🔍 COMPARADOR DE ACTIVOS FINANCIEROS")
    print("   Algoritmos de Similitud de Series Temporales")
    print("=" * 60)
    
    # Cargar activos
    tickers = mostrar_menu_activos(df)
    
    # Seleccionar activos
    print("\n" + "-" * 40)
    ticker1 = seleccionar_activo(tickers, 1)
    ticker2 = seleccionar_activo(tickers, 2)
    
    if ticker1 == ticker2:
        print("\n⚠️  ¡Seleccionaste el mismo activo! Usando otro diferente...")
        ticker2 = [t for t in tickers if t != ticker1][0]
    
    # Calcular similitud
    print(f"\n🔄 Calculando similitud entre {ticker1} y {ticker2}...")
    resultado = comparar_activos(df, ticker1, ticker2)
    
    # Mostrar resultados
    mostrar_resultados(resultado)
    
    # Preguntar si quiere ver explicaciones
    print("\n" + "-" * 40)
    print("📚 OPCIONES:")
    print("   1. Ver explicación de un algoritmo específico")
    print("   2. Ver todas las explicaciones")
    print("   3. Comparar otros activos")
    print("   4. Salir")
    
    while True:
        try:
            opcion = input("\n👉 Selecciona una opción (1-4): ").strip()
            
            if opcion == '1':
                print("\n📋 ALGORITMOS DISPONIBLES:")
                print("   1. Distancia Euclidiana")
                print("   2. Correlación de Pearson")
                print("   3. Dynamic Time Warping")
                print("   4. Similitud por Coseno")
                
                alg_opcion = input("\n👉 Selecciona algoritmo (1-4): ").strip()
                algoritmos = ['distancia_euclidiana', 'correlacion_pearson', 'dtw', 'similitud_coseno']
                if alg_opcion in ['1', '2', '3', '4']:
                    mostrar_explicacion(algoritmos[int(alg_opcion) - 1])
            
            elif opcion == '2':
                mostrar_todas_explicaciones()
            
            elif opcion == '3':
                return True  # Continuar con nueva comparación
            
            elif opcion == '4':
                print("\n👋 ¡Hasta luego!")
                return False
            
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            return False


def main():
    """Función principal."""
    # Banner
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🔍 ANÁLISIS DE SIMILITUD DE SERIES TEMPORALES              ║
║                                                              ║
║   Requerimiento 2 - Algoritmos de Similitud                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Cargar datos
    df = cargar_datos()
    if df is None:
        return
    
    print(f"\n✅ Datos cargados: {len(df)} registros de {df['Ticker'].nunique()} activos")
    
    # Loop principal
    continuar = True
    while continuar:
        continuar = comparar_activos_interactivo(df)


if __name__ == "__main__":
    main()