"""
Módulo de Visualización de Series Temporales Financieras

Este módulo implementa:
1. Mapa de calor de correlación
2. Gráficos candlestick con medias móviles
3. Exportación a PDF

Autor: Equipo del proyecto
Fecha: 2026
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
from typing import List, Dict, Tuple, Any
import os
from datetime import datetime

# Importar función de correlación del módulo similarity
from src.similarity import correlacion_pearson

# Configuración de estilo
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


# =========================================================
# 1. MEDIA MÓVIL SIMPLE (SMA) - ALGORÍTMICA
# =========================================================
"""
MATHEMATICAL EXPLANATION:
=========================
La Media Móvil Simple (SMA) es un promedio móvil que suaviza las
fluctuaciones de precio a lo largo de un período determinado.

Fórmula:
SMA(n) = (P[t] + P[t-1] + ... + P[t-n+1]) / n

donde:
- n = período de la media móvil
- P[t] = precio en el momento t

ALGORITHM DESCRIPTION:
=====================
1. Definir tamaño de ventana n
2. Para cada posición i desde n-1 hasta len(precios):
   a. Calcular promedio de los n elementos anteriores
   b. Asignar al resultado
3. Rellenar los primeros n-1 valores con NaN

COMPLEJITY: O(n × m) donde n = período, m = longitud
OPTIMIZACIÓN: O(m) usando suma acumulativa
"""


def calcular_media_movil(precios: np.ndarray, periodo: int) -> np.ndarray:
    """
    Calcula la Media Móvil Simple (SMA) de forma algorítmica.
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
    periodo : int
        Período para la media móvil
        
    Retorna:
    --------
    np.ndarray
        Serie con la media móvil calculada
    """
    n = len(precios)
    if periodo > n:
        return np.full(n, np.nan)
    
    # Usar suma acumulativa para optimizar
    # SMA[i] = (sum(precios[i:i+periodo])) / periodo
    suma_acumulativa = np.cumsum(precios)
    
    # Calcular SMA
    sma = np.full(n, np.nan)
    for i in range(periodo - 1, n):
        if i - periodo + 1 >= 0:
            suma = suma_acumulativa[i] - (suma_acumulativa[i - periodo] if i >= periodo else 0)
            sma[i] = suma / periodo
    
    return sma


def calcular_multiples_sma(precios: np.ndarray) -> Dict[int, np.ndarray]:
    """
    Calcula múltiples medias móviles (corto, medio, largo plazo).
    
    Parámetros:
    -----------
    precios : np.ndarray
        Serie de precios de cierre
        
    Retorna:
    --------
    dict
        Diccionario con {periodo: SMA}
    """
    return {
        20: calcular_media_movil(precios, 20),  # Corto plazo
        50: calcular_media_movil(precios, 50),  # Medio plazo
        200: calcular_media_movil(precios, 200) # Largo plazo
    }


# =========================================================
# 2. MAPA DE CALOR DE CORRELACIÓN
# =========================================================

def generar_matriz_correlacion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la matriz de correlación entre todos los activos.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con columnas Date, Ticker, Close
        
    Retorna:
    --------
    pd.DataFrame
        Matriz de correlación
    """
    # Pivotar para tener tickers como columnas
    precios_pivot = df.pivot(index='Date', columns='Ticker', values='Close')
    
    # Calcular retornos MANUALMENTE (sin usar pct_change)
    # retornos[t] = (precio[t] - precio[t-1]) / precio[t-1]
    retornos_dict = {}
    for ticker in precios_pivot.columns:
        precios = precios_pivot[ticker].values
        # Calcular retornos diarios manualmente
        retornos = np.diff(precios) / precios[:-1]
        # Filtrar NaN, infinitos y valores extremos
        retornos = retornos[np.isfinite(retornos)]
        retornos = retornos[np.abs(retornos) < 1.0]
        retornos_dict[ticker] = retornos
    
    # Encontrar la longitud mínima para alinear todas las series
    min_length = min(len(r) for r in retornos_dict.values())
    
    # Calcular matriz de correlación usando correlacion_pearson
    tickers = list(retornos_dict.keys())
    n = len(tickers)
    matriz_corr = np.zeros((n, n))
    
    for i, ticker1 in enumerate(tickers):
        for j, ticker2 in enumerate(tickers):
            if i == j:
                matriz_corr[i, j] = 1.0
            elif i < j:
                # Usar los primeros min_length elementos para cada serie
                retornos1 = retornos_dict[ticker1][:min_length]
                retornos2 = retornos_dict[ticker2][:min_length]
                corr = correlacion_pearson(retornos1, retornos2)
                matriz_corr[i, j] = corr
                matriz_corr[j, i] = corr
    
    # Convertir a DataFrame
    correlacion = pd.DataFrame(matriz_corr, index=tickers, columns=tickers)
    
    return correlacion


def graficar_mapa_calor(correlacion: pd.DataFrame, guardar: bool = True) -> plt.Figure:
    """
    Genera el mapa de calor de correlación.
    
    Parámetros:
    -----------
    correlacion : pd.DataFrame
        Matriz de correlación
    guardar : bool
        Si True, guarda la imagen
        
    Retorna:
    --------
    plt.Figure
        Figura de matplotlib
    """
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Crear mapa de calor
    sns.heatmap(
        correlacion,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn',
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        cbar_kws={'label': 'Correlación', 'shrink': 0.8},
        ax=ax
    )
    
    ax.set_title('Matriz de Correlación entre Activos\n(Retornos Diarios)', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Activo', fontsize=12)
    ax.set_ylabel('Activo', fontsize=12)
    
    # Rotar etiquetas
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    plt.setp(ax.get_yticklabels(), rotation=0)
    
    plt.tight_layout()
    
    if guardar:
        os.makedirs('reports', exist_ok=True)
        fig.savefig('reports/mapa_calor_correlacion.png', dpi=150, bbox_inches='tight')
        print("✅ Mapa de calor guardado en: reports/mapa_calor_correlacion.png")
    
    return fig


# =========================================================
# 3. GRÁFICOS CANDLESTICK
# =========================================================

def graficar_candlestick(df: pd.DataFrame, ticker: str, 
                         sma_periodos: List[int] = [20, 50],
                         guardar: bool = True) -> plt.Figure:
    """
    Genera un gráfico candlestick con medias móviles.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos OHLC
    ticker : str
        Ticker del activo
    sma_periodos : list
        Lista de períodos para SMA
    guardar : bool
        Si True, guarda la imagen
        
    Retorna:
    --------
    plt.Figure
        Figura de matplotlib
    """
    # Filtrar por ticker
    df_ticker = df[df['Ticker'] == ticker].sort_values('Date').copy()
    
    if len(df_ticker) == 0:
        print(f"❌ No se encontró el ticker: {ticker}")
        return None
    
    # Tomar los últimos 90 días para mejor visualización
    df_ticker = df_ticker.tail(90).reset_index(drop=True)
    
    # Calcular medias móviles
    smas = {}
    for periodo in sma_periodos:
        smas[periodo] = calcular_media_movil(df_ticker['Close'].values, periodo)
    
    # Crear figura
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                    gridspec_kw={'height_ratios': [3, 1]},
                                    sharex=True)
    
    # === Gráfico principal (Candlestick) ===
    x = range(len(df_ticker))
    
    # Dibujar velas
    for i, (_, row) in enumerate(df_ticker.iterrows()):
        open_price = row['Open']
        close_price = row['Close']
        high = row['High']
        low = row['Low']
        
        # Determinar color
        if close_price >= open_price:
            color = 'green'
            body_bottom = open_price
            body_height = close_price - open_price
        else:
            color = 'red'
            body_bottom = close_price
            body_height = open_price - close_price
        
        # Dibujar mecha (high-low)
        ax1.plot([i, i], [low, high], color=color, linewidth=1)
        
        # Dibujar cuerpo (open-close)
        rect = Rectangle((i - 0.3, body_bottom), 0.6, body_height if body_height > 0 else 0.01,
                         facecolor=color if color == 'green' else color,
                         edgecolor=color, linewidth=1)
        ax1.add_patch(rect)
    
    # Dibujar medias móviles
    colores = ['blue', 'orange', 'purple']
    for idx, periodo in enumerate(sma_periodos):
        ax1.plot(x, smas[periodo], label=f'SMA {periodo}', 
                 color=colores[idx % len(colores)], linewidth=2)
    
    ax1.set_title(f'Gráfico Candlestick - {ticker}\n(Últimos 90 días)', 
                 fontsize=14, fontweight='bold')
    ax1.set_ylabel('Precio', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # === Gráfico inferior (Volumen) ===
    colores_vol = ['green' if df_ticker.iloc[i]['Close'] >= df_ticker.iloc[i]['Open'] else 'red' 
                   for i in range(len(df_ticker))]
    ax2.bar(x, df_ticker['Volume'], color=colores_vol, alpha=0.7)
    ax2.set_title('Volumen de Negociación', fontsize=12)
    ax2.set_xlabel('Días', fontsize=12)
    ax2.set_ylabel('Volumen', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if guardar:
        os.makedirs('reports', exist_ok=True)
        filename = f'reports/candlestick_{ticker}.png'
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"✅ Candlestick guardado en: {filename}")
    
    return fig


def graficar_todos_candlestick(df: pd.DataFrame, tickers: List[str] = None,
                                sma_periodos: List[int] = [20, 50]) -> Dict[str, plt.Figure]:
    """
    Genera gráficos candlestick para múltiples activos.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos financieros
    tickers : list
        Lista de tickers a graficar (None = todos)
    sma_periodos : list
        Períodos para SMA
        
    Retorna:
    --------
    dict
        Diccionario con {ticker: figura}
    """
    if tickers is None:
        tickers = df['Ticker'].unique().tolist()
    
    figuras = {}
    for ticker in tickers:
        try:
            fig = graficar_candlestick(df, ticker, sma_periodos, guardar=True)
            if fig:
                figuras[ticker] = fig
        except Exception as e:
            print(f"❌ Error al graficar {ticker}: {e}")
    
    return figuras


# =========================================================
# 4. EXPORTACIÓN A PDF
# =========================================================

def generar_reporte_pdf(df: pd.DataFrame, 
                         output_path: str = 'reports/reporte_tecnico.pdf') -> str:
    """
    Genera un reporte técnico en formato PDF.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos financieros
    output_path : str
        Ruta de salida del PDF
        
    Retorna:
    --------
    str
        Ruta del archivo generado
    """
    from matplotlib.backends.backend_pdf import PdfPages
    
    # Importar ReportLab para PDF real
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        print("⚠️  reportlab no está instalado. Instalando...")
        import subprocess
        subprocess.run(['pip', 'install', 'reportlab'], check=True)
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    
    # Crear documento
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("Reporte Técnico - Análisis de Activos Financieros", title_style))
    
    # Fecha
    date_style = ParagraphStyle(
        'CustomDate',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style))
    elements.append(Spacer(1, 20))
    
    # 1. Matriz de correlación
    elements.append(Paragraph("1. Matriz de Correlación", styles['Heading2']))
    correlacion = generar_matriz_correlacion(df)
    
    # Guardar imagen de correlación
    fig = graficar_mapa_calor(correlacion, guardar=True)
    elements.append(Spacer(1, 10))
    
    # 2. Clasificación de riesgo
    from src.patterns import clasificar_todos_activos
    elements.append(Paragraph("2. Clasificación de Riesgo", styles['Heading2']))
    reporte_riesgo = clasificar_todos_activos(df)
    
    # Crear tabla
    data = [['Ticker', 'Volatilidad', 'Clasificación']]
    for _, row in reporte_riesgo.iterrows():
        data.append([row['Ticker'], f"{row['Volatilidad_Anualizada']:.2f}%", row['Clasificacion_Riesgo']])
    
    table = Table(data[:11])  # Primeras 10 filas + header
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # 3. Gráficos candlestick de ejemplo
    elements.append(Paragraph("3. Gráficos Candlestick (Top 5 por volatilidad)", styles['Heading2']))
    elements.append(Paragraph("Los gráficos se encuentran en la carpeta reports/", styles['Normal']))
    
    # Generar candlesticks para top 5
    top5 = reporte_riesgo.head(5)['Ticker'].tolist()
    for ticker in top5:
        graficar_candlestick(df, ticker, guardar=True)
    
    # Construir PDF
    doc.build(elements)
    
    print(f"✅ Reporte PDF guardado en: {output_path}")
    return output_path


# =========================================================
# INTERFAZ UNIFICADA
# =========================================================

def generar_todas_visualizaciones(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera todas las visualizaciones del proyecto.
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con datos financieros
        
    Retorna:
    --------
    dict
        Diccionario con rutas de archivos generados
    """
    resultados = {}
    
    print("=" * 60)
    print("GENERANDO VISUALIZACIONES")
    print("=" * 60)
    
    # 1. Mapa de calor
    print("\n1. Generando mapa de calor de correlación...")
    correlacion = generar_matriz_correlacion(df)
    graficar_mapa_calor(correlacion, guardar=True)
    resultados['mapa_calor'] = 'reports/mapa_calor_correlacion.png'
    
    # 2. Candlesticks para todos los activos
    print("\n2. Generando gráficos candlestick...")
    graficar_todos_candlestick(df)
    resultados['candlesticks'] = 'reports/candlestick_*.png'
    
    # 3. Reporte PDF
    print("\n3. Generando reporte PDF...")
    generar_reporte_pdf(df)
    resultados['pdf'] = 'reports/reporte_tecnico.pdf'
    
    print("\n" + "=" * 60)
    print("✅ VISUALIZACIONES COMPLETADAS")
    print("=" * 60)
    
    return resultados


# =========================================================
# PRUEBAS
# =========================================================


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    
    print("=" * 60)
    print("PRUEBAS DEL MÓDULO DE VISUALIZACIÓN")
    print("=" * 60)
    
    # Cargar datos
    data_path = project_root / "data" / "processed" / "precios_unificados.csv"
    df = pd.read_csv(data_path, parse_dates=['Date'])
    print(f"\nDatos cargados: {len(df)} registros")
    
    # Prueba 1: Media móvil
    print("\n1. PRUEBA DE MEDIA MÓVIL")
    print("-" * 40)
    precios = df[df['Ticker'] == 'ECOPETROL'].sort_values('Date')['Close'].values[-30:]
    sma_20 = calcular_media_movil(precios, 20)
    print(f"   SMA-20 calculada: {sma_20[-5:]}")
    
    # Prueba 2: Matriz de correlación
    print("\n2. PRUEBA DE MATRIZ DE CORRELACIÓN")
    print("-" * 40)
    correlacion = generar_matriz_correlacion(df)
    print(f"   Matriz generada: {correlacion.shape}")
    
    # Prueba 3: Candlestick
    print("\n3. PRUEBA DE CANDLESTICK")
    print("-" * 40)
    graficar_candlestick(df, 'ECOPETROL', guardar=True)
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)