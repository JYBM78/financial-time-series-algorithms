import numpy as np
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.requerimiento_3.deteccion_patrones.patrones import analizar_activo, clasificar_todos_activos
from src.requerimiento_4.mapa_calor.correlacion import generar_matriz_correlacion, graficar_mapa_calor
from src.requerimiento_4.graficos_velas.candlestick import graficar_candlestick

def generar_reporte_pdf(df, ruta_salida=None):
    if ruta_salida is None:
        ruta_salida = Path(__file__).resolve().parents[3] / "reports" / "reporte_analisis_tecnico.pdf"
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(str(ruta_salida), pagesize=letter,
                            rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Titulo", parent=styles["Heading1"], fontSize=20, spaceAfter=20))
    styles.add(ParagraphStyle(name="Subtitulo", parent=styles["Heading2"], fontSize=14, spaceAfter=12))
    elements = []
    elements.append(Paragraph("Reporte de Analisis Tecnico", styles["Titulo"]))
    elements.append(Paragraph("Financial Time Series - Dashboard de Visualizacion", styles["Subtitulo"]))
    elements.append(Spacer(1, 12))
    elementos_texto = [
        f"Fecha de generacion: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        f"Activos analizados: {df['Ticker'].nunique()}",
        f"Registros totales: {len(df)}",
    ]
    for txt in elementos_texto:
        elements.append(Paragraph(txt, styles["Normal"]))
    elements.append(Spacer(1, 24))
    elements.append(PageBreak())
    elements.append(Paragraph("1. Matriz de Correlacion", styles["Heading2"]))
    elements.append(Paragraph(
        "La matriz de correlacion muestra el coeficiente de Pearson entre "
        "los retornos diarios de cada par de activos. Valores cercanos a 1 "
        "indican alta correlacion positiva; cercanos a -1, correlacion negativa.",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 12))
    try:
        matriz = generar_matriz_correlacion(df)
        ruta_heat = ruta_salida.parent / "mapa_calor_correlacion.png"
        graficar_mapa_calor(matriz, guardar=True, ruta=ruta_heat)
        if ruta_heat.exists():
            elements.append(Image(str(ruta_heat), width=6 * inch, height=5 * inch))
    except Exception as e:
        elements.append(Paragraph(f"Error al generar mapa de calor: {e}", styles["Normal"]))
    elements.append(PageBreak())
    elements.append(Paragraph("2. Analisis por Activo", styles["Heading2"]))
    for ticker in sorted(df["Ticker"].unique()):
        elements.append(Paragraph(f"2.1 {ticker}", styles["Heading3"]))
        try:
            resultado = analizar_activo(df, ticker)
            metricas = resultado["metricas_dispersion"]
            clasif = resultado["clasificacion_riesgo"]
            tabla_data = [
                ["Metrica", "Valor"],
                ["Volatilidad Anualizada", f"{metricas['volatilidad_anualizada']:.2f}%"],
                ["Volatilidad Diaria", f"{metricas['volatilidad_diaria']:.2f}%"],
                ["Desviacion Estandar", f"{metricas['desviacion_estandar']:.5f}"],
                ["Clasificacion de Riesgo", clasif],
            ]
            tabla = Table(tabla_data, colWidths=[3 * inch, 3 * inch])
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(tabla)
            elements.append(Spacer(1, 8))
            ruta_vela = ruta_salida.parent / f"candlestick_{ticker}.png"
            graficar_candlestick(df, ticker, guardar=True, ruta=ruta_vela)
            if ruta_vela.exists():
                elements.append(Image(str(ruta_vela), width=6 * inch, height=4 * inch))
        except Exception as e:
            elements.append(Paragraph(f"Error analizando {ticker}: {e}", styles["Normal"]))
        elements.append(Spacer(1, 16))
    elements.append(PageBreak())
    elements.append(Paragraph("3. Clasificacion de Riesgo General", styles["Heading2"]))
    try:
        reporte = clasificar_todos_activos(df)
        tabla_riesgo = [["Ticker", "Volatilidad Anualizada", "Clasificacion"]]
        for _, row in reporte.iterrows():
            tabla_riesgo.append([
                row["Ticker"],
                f"{row['Volatilidad_Anualizada']:.2f}%",
                row["Clasificacion_Riesgo"],
            ])
        t = Table(tabla_riesgo, colWidths=[1.5 * inch, 2 * inch, 1.5 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
    except Exception as e:
        elements.append(Paragraph(f"Error generando clasificacion: {e}", styles["Normal"]))
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(
        "--- Fin del Reporte ---", styles["Normal"]
    ))
    doc.build(elements)
    return str(ruta_salida)

def generar_todas_visualizaciones(df):
    resultados = {}
    try:
        matriz = generar_matriz_correlacion(df)
        ruta_heat = Path(__file__).resolve().parents[3] / "reports" / "mapa_calor_correlacion.png"
        graficar_mapa_calor(matriz, guardar=True, ruta=ruta_heat)
        resultados["mapa_calor"] = str(ruta_heat)
    except Exception as e:
        resultados["mapa_calor"] = f"Error: {e}"
    for ticker in sorted(df["Ticker"].unique()):
        try:
            ruta_vela = Path(__file__).resolve().parents[3] / "reports" / f"candlestick_{ticker}.png"
            graficar_candlestick(df, ticker, guardar=True, ruta=ruta_vela)
            resultados[f"candlestick_{ticker}"] = str(ruta_vela)
        except Exception as e:
            resultados[f"candlestick_{ticker}"] = f"Error: {e}"
    try:
        ruta_pdf = generar_reporte_pdf(df)
        resultados["reporte_pdf"] = ruta_pdf
    except Exception as e:
        resultados["reporte_pdf"] = f"Error: {e}"
    return resultados
