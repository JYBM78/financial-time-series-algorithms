import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Asegurar acceso al paquete src
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from src.requerimiento_1.etl.descarga import descargar_todos
from src.requerimiento_1.etl.unificacion import unificar
from src.requerimiento_2.algoritmos_similitud.similitud import comparar_activos
from src.requerimiento_3.deteccion_patrones.patrones import analizar_activo, clasificar_todos_activos
from src.requerimiento_4.mapa_calor.correlacion import generar_matriz_correlacion, graficar_mapa_calor
from src.requerimiento_4.graficos_velas.candlestick import graficar_candlestick
from src.requerimiento_4.reporte_pdf.generador import generar_reporte_pdf


@st.cache_data
def cargar_dataset() -> pd.DataFrame | None:
    ruta = PROJECT_ROOT / "data" / "processed" / "precios_unificados.csv"
    if ruta.exists():
        return pd.read_csv(ruta, parse_dates=["Date"])
    return None


def mostrar_encabezado():
    st.title("Financial Time Series Dashboard")
    st.write(
        "Interfaz integrada para descargar datos, comparar activos, detectar patrones, visualizar resultados y generar reportes.")
    st.markdown(
        "---\n" 
        "### Funcionalidades incluidas:\n" 
        "- Descarga y unificación automática de datos desde Yahoo Finance\n" 
        "- Comparación de activos con algoritmos de similitud\n" 
        "- Detección de patrones y clasificación de riesgo\n" 
        "- Visualizaciones interactivas y generación de PDF técnico"
    )


def etl_section(df):
    st.header("1. Descarga y Unificación de Datos")

    if st.button("Descargar y unificar datos desde cero"):
        with st.spinner("Descargando datos desde Yahoo Finance..."):
            descargar_todos()
            df = unificar()
        st.success("ETL completado. Dataset regenerado.")

    if df is None:
        st.warning("No se encontró el dataset unificado. Ejecuta la ETL para generar el archivo.")
        return None

    st.subheader("Dataset Unificado")
    st.write(f"Registros: {len(df)} | Activos: {df['Ticker'].nunique()}")
    st.dataframe(df.head(10))
    return df


def similitud_section(df):
    st.header("2. Comparador de Similitud")
    if df is None:
        st.warning("Carga primero el dataset en la sección ETL.")
        return

    tickers = sorted(df['Ticker'].unique().tolist())
    col1, col2 = st.columns(2)

    with col1:
        ticker1 = st.selectbox("Activo 1", tickers, index=0)
    with col2:
        ticker2 = st.selectbox("Activo 2", tickers, index=1)

    if st.button("Comparar activos"):
        resultados = comparar_activos(df, ticker1, ticker2)
        st.subheader(f"Resultados: {ticker1} vs {ticker2}")
        cols = st.columns(3)
        cols[0].metric("Distancia Euclidiana", f"{resultados['distancia_euclidiana']:.4f}")
        cols[0].metric("Euclidiana Normalizada", f"{resultados['distancia_euclidiana_normalizada']:.4f}")
        cols[1].metric("Correlación Pearson", f"{resultados['correlacion_pearson']:.4f}")
        cols[1].metric("Distancia DTW", f"{resultados['dtw']:.4f}")
        cols[2].metric("Similitud Coseno", f"{resultados['similitud_coseno']:.4f}")
        cols[2].metric("Distancia Coseno", f"{resultados['distancia_coseno']:.4f}")

        with st.expander("Ver explicaciones de los algoritmos"):
            st.markdown(
                "- **Distancia Euclidiana**: √Σ(xi-yi)²\n"
                "- **Correlación de Pearson**: cov(x,y) / (σxσy)\n"
                "- **DTW**: Alineamiento temporal mínimo entre series\n"
                "- **Similitud Coseno**: (x·y) / (||x|| ||y||)"
            )


def patrones_section(df):
    st.header("3. Análisis de Patrones y Riesgo")
    if df is None:
        st.warning("Carga primero el dataset en la sección ETL.")
        return

    tickers = sorted(df['Ticker'].unique().tolist())
    ticker = st.selectbox("Selecciona un activo", tickers)

    if st.button("Analizar activo"):
        resultado = analizar_activo(df, ticker)
        metricas = resultado['metricas_dispersion']
        patrones = resultado['patrones']
        clasificacion = resultado['clasificacion_riesgo']

        st.subheader(f"Activo: {ticker}")
        st.success(f"Clasificación de riesgo: {clasificacion}")

        col1, col2 = st.columns(2)
        col1.write("**Métricas de dispersión**")
        col1.metric("Volatilidad anualizada", f"{metricas['volatilidad_anualizada']:.2f}%")
        col1.metric("Volatilidad diaria", f"{metricas['volatilidad_diaria']:.2f}%")
        col1.metric("Desviación estándar", f"{metricas['desviacion_estandar']:.5f}")
        col2.write("**Patrones detectados**")
        col2.metric("Días al alza", f"{patrones['dias_consecutivos_alza']['frecuencia_porcentual']:.2f}%")
        col2.metric("Volatilidad extrema", f"{patrones['volatilidad_extrema']['frecuencia_porcentual']:.2f}%")
        col2.metric("Cambios significativos", f"{patrones['cambio_significativo']['frecuencia_porcentual']:.2f}%")

        with st.expander("Ver detalles de patrones"):
            st.write(patrones)

        if st.button("Generar reporte de riesgo general"):
            reporte = clasificar_todos_activos(df)
            report_path = PROJECT_ROOT / "reports" / "reporte_riesgo.csv"
            reporte.to_csv(report_path, index=False)
            st.success(f"Reporte de riesgo guardado en: {report_path}")
            st.dataframe(reporte.head(10))


def visualizacion_section(df):
    st.header("4. Visualización")
    if df is None:
        st.warning("Carga primero el dataset en la sección ETL.")
        return

    tickers = sorted(df['Ticker'].unique().tolist())
    ticker = st.selectbox("Selecciona un activo para candlestick", tickers, index=0)

    if st.button("Generar visualizaciones"):
        with st.spinner("Generando mapa de calor y gráfico candlestick..."):
            correlacion = generar_matriz_correlacion(df)
            fig_heat = graficar_mapa_calor(correlacion, guardar=False)
            st.pyplot(fig_heat)
            st.write("Matriz de correlación de retornos diarios")

            fig_candle = graficar_candlestick(df, ticker, guardar=False)
            if fig_candle is not None:
                st.pyplot(fig_candle)
            st.success("Visualizaciones generadas.")

    if st.button("Generar reporte PDF técnico"):
        with st.spinner("Creando reporte PDF..."):
            ruta_pdf = generar_reporte_pdf(df)
        st.success(f"Reporte PDF guardado en: {ruta_pdf}")
        if Path(ruta_pdf).exists():
            pdf_bytes = Path(ruta_pdf).read_bytes()
            st.download_button(
                label="Descargar reporte PDF",
                data=pdf_bytes,
                file_name=Path(ruta_pdf).name,
                mime="application/pdf"
            )
        else:
            st.error("No se encontró el archivo PDF generado.")


def main():
    st.set_page_config(
        page_title="Financial Time Series App",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    mostrar_encabezado()

    menu = st.sidebar.radio(
        "Sección",
        ["Inicio", "ETL", "Similitud", "Patrones y Riesgo", "Visualización"]
    )

    df = cargar_dataset()

    if menu == "Inicio":
        st.write("Selecciona una sección en el menú lateral para comenzar.")
        if df is not None:
            st.info("Dataset unificado encontrado. Puedes usar las secciones ETL, Similitud, Patrones y Visualización.")
        else:
            st.warning("No se encontró dataset unificado. Ve a ETL para descargar y unificar los datos.")

    elif menu == "ETL":
        df = etl_section(df)

    elif menu == "Similitud":
        similitud_section(df)

    elif menu == "Patrones y Riesgo":
        patrones_section(df)

    elif menu == "Visualización":
        visualizacion_section(df)


if __name__ == "__main__":
    main()
