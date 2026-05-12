import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
from flask import Flask, render_template_string, request, send_file, jsonify
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.requerimiento_1.etl.config import TICKERS
from src.requerimiento_1.etl.unificacion import unificar
from src.requerimiento_2.algoritmos_similitud.similitud import comparar_activos
from src.requerimiento_3.deteccion_patrones.patrones import analizar_activo, clasificar_todos_activos
from src.requerimiento_4.mapa_calor.correlacion import generar_matriz_correlacion, graficar_mapa_calor
from src.requerimiento_4.graficos_velas.candlestick import graficar_candlestick
from src.requerimiento_4.reporte_pdf.generador import generar_reporte_pdf

app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/datos")
def api_datos():
    ruta = PROJECT_ROOT / "data" / "processed" / "precios_unificados.csv"
    if ruta.exists():
        df = pd.read_csv(ruta, parse_dates=["Date"])
        return jsonify({
            "registros": len(df),
            "activos": sorted(df["Ticker"].unique().tolist()),
            "fecha_min": str(df["Date"].min()),
            "fecha_max": str(df["Date"].max()),
        })
    return jsonify({"error": "No hay datos unificados"})

@app.route("/api/etl", methods=["POST"])
def api_etl():
    from src.requerimiento_1.etl.descarga import descargar_todos
    try:
        descargar_todos()
        df = unificar()
        return jsonify({"mensaje": "ETL completado", "registros": len(df), "activos": df["Ticker"].nunique()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/similitud")
def api_similitud():
    ticker1 = request.args.get("ticker1")
    ticker2 = request.args.get("ticker2")
    ruta = PROJECT_ROOT / "data" / "processed" / "precios_unificados.csv"
    if not ruta.exists():
        return jsonify({"error": "Ejecuta ETL primero"}), 400
    df = pd.read_csv(ruta, parse_dates=["Date"])
    try:
        resultado = comparar_activos(df, ticker1, ticker2)
        return jsonify({k: float(v) if isinstance(v, (int, float, np.floating)) else v for k, v in resultado.items()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analisis/<ticker>")
def api_analisis(ticker):
    ruta = PROJECT_ROOT / "data" / "processed" / "precios_unificados.csv"
    if not ruta.exists():
        return jsonify({"error": "Ejecuta ETL primero"}), 400
    df = pd.read_csv(ruta, parse_dates=["Date"])
    try:
        resultado = analizar_activo(df, ticker)
        resultado["metricas_dispersion"] = {k: float(v) for k, v in resultado["metricas_dispersion"].items()}
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/grafico/mapa_calor")
def api_grafico_mapa_calor():
    ruta = PROJECT_ROOT / "data" / "processed" / "precios_unificados.csv"
    if not ruta.exists():
        return jsonify({"error": "Ejecuta ETL primero"}), 400
    df = pd.read_csv(ruta, parse_dates=["Date"])
    try:
        matriz = generar_matriz_correlacion(df)
        fig = graficar_mapa_calor(matriz, guardar=False)
        img = io.BytesIO()
        FigureCanvas(fig).print_png(img)
        plt.close(fig)
        img.seek(0)
        return send_file(img, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/grafico/candlestick/<ticker>")
def api_grafico_candlestick(ticker):
    ruta = PROJECT_ROOT / "data" / "processed" / "precios_unificados.csv"
    if not ruta.exists():
        return jsonify({"error": "Ejecuta ETL primero"}), 400
    df = pd.read_csv(ruta, parse_dates=["Date"])
    try:
        fig = graficar_candlestick(df, ticker, guardar=False)
        if fig is None:
            return jsonify({"error": "No hay datos suficientes"}), 400
        img = io.BytesIO()
        FigureCanvas(fig).print_png(img)
        plt.close(fig)
        img.seek(0)
        return send_file(img, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reporte/pdf")
def api_reporte_pdf():
    ruta = PROJECT_ROOT / "data" / "processed" / "precios_unificados.csv"
    if not ruta.exists():
        return jsonify({"error": "Ejecuta ETL primero"}), 400
    df = pd.read_csv(ruta, parse_dates=["Date"])
    try:
        ruta_pdf = generar_reporte_pdf(df)
        return send_file(ruta_pdf, mimetype="application/pdf", as_attachment=True, download_name="reporte_analisis.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clasificacion")
def api_clasificacion():
    ruta = PROJECT_ROOT / "data" / "processed" / "precios_unificados.csv"
    if not ruta.exists():
        return jsonify({"error": "Ejecuta ETL primero"}), 400
    df = pd.read_csv(ruta, parse_dates=["Date"])
    try:
        reporte = clasificar_todos_activos(df)
        return jsonify(reporte.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def ejecutar(host="0.0.0.0", port=5000, debug=True):
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    ejecutar()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Financiero - Req 5</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f2f5; color: #333; }
        .navbar { background: linear-gradient(135deg, #1a237e, #283593); color: white; padding: 1rem 2rem; }
        .navbar h1 { font-size: 1.5rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1.5rem; }
        .card h2 { color: #1a237e; margin-bottom: 1rem; border-bottom: 2px solid #e0e0e0; padding-bottom: 0.5rem; }
        .btn { background: #1a237e; color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 4px; cursor: pointer; font-size: 0.9rem; }
        .btn:hover { background: #283593; }
        .btn-success { background: #2e7d32; }
        .btn-success:hover { background: #388e3c; }
        select, input { padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; font-size: 0.9rem; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
        .metric { text-align: center; padding: 1rem; background: #f5f5f5; border-radius: 8px; }
        .metric .value { font-size: 1.8rem; font-weight: bold; color: #1a237e; }
        .metric .label { font-size: 0.85rem; color: #666; margin-top: 0.3rem; }
        img { max-width: 100%; height: auto; border-radius: 4px; }
        .tab { display: none; }
        .tab.active { display: block; }
        .tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
        .tab-btn { background: #e0e0e0; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }
        .tab-btn.active { background: #1a237e; color: white; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #e0e0e0; }
        th { background: #f5f5f5; font-weight: bold; }
        .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
        .badge-bajo { background: #c8e6c9; color: #2e7d32; }
        .badge-medio { background: #fff9c4; color: #f57f17; }
        .badge-alto { background: #ffccbc; color: #d84315; }
        .badge-muy-alto { background: #ffcdd2; color: #c62828; }
    </style>
</head>
<body>
    <nav class="navbar"><h1>Dashboard Financiero - Requerimiento 5</h1></nav>
    <div class="container">
        <div class="card">
            <div class="tabs">
                <button class="tab-btn active" onclick="showTab('etl')">1. ETL</button>
                <button class="tab-btn" onclick="showTab('similitud')">2. Similitud</button>
                <button class="tab-btn" onclick="showTab('patrones')">3. Patrones</button>
                <button class="tab-btn" onclick="showTab('visualizacion')">4. Visualizacion</button>
                <button class="tab-btn" onclick="showTab('reporte')">5. Reporte PDF</button>
            </div>

            <div id="tab-etl" class="tab active">
                <h2>1. Carga de Datos (ETL)</h2>
                <p style="margin-bottom: 1rem;">Descarga y unifica los datos de los activos financieros desde Yahoo Finance.</p>
                <button class="btn btn-success" onclick="ejecutarETL()">Ejecutar ETL completo</button>
                <div id="resultado-etl" style="margin-top: 1rem;"></div>
                <div id="datos-resumen" style="margin-top: 1rem;"></div>
            </div>

            <div id="tab-similitud" class="tab">
                <h2>2. Comparador de Similitud</h2>
                <div class="grid-2" style="margin-bottom: 1rem;">
                    <div><label>Activo 1:</label><br><select id="sim-ticker1"></select></div>
                    <div><label>Activo 2:</label><br><select id="sim-ticker2"></select></div>
                </div>
                <button class="btn" onclick="compararSimilitud()">Comparar activos</button>
                <div id="resultado-similitud" style="margin-top: 1rem;"></div>
            </div>

            <div id="tab-patrones" class="tab">
                <h2>3. Analisis de Patrones y Riesgo</h2>
                <div style="margin-bottom: 1rem;">
                    <label>Activo:</label>
                    <select id="pat-ticker"></select>
                    <button class="btn" onclick="analizarActivo()" style="margin-left: 0.5rem;">Analizar</button>
                </div>
                <div id="resultado-patrones"></div>
                <hr style="margin: 1rem 0;">
                <button class="btn" onclick="cargarClasificacion()">Ver clasificacion general de riesgo</button>
                <div id="resultado-clasificacion" style="margin-top: 1rem;"></div>
            </div>

            <div id="tab-visualizacion" class="tab">
                <h2>4. Visualizaciones</h2>
                <button class="btn" onclick="cargarMapaCalor()">Cargar Mapa de Calor</button>
                <div id="mapa-calor-container" style="margin-top: 1rem;"></div>
                <hr style="margin: 1rem 0;">
                <div style="margin-bottom: 1rem;">
                    <label>Activo para candlestick:</label>
                    <select id="vela-ticker"></select>
                    <button class="btn" onclick="cargarCandlestick()" style="margin-left: 0.5rem;">Graficar</button>
                </div>
                <div id="candlestick-container"></div>
            </div>

            <div id="tab-reporte" class="tab">
                <h2>5. Generacion de Reporte PDF</h2>
                <p style="margin-bottom: 1rem;">Genera un reporte tecnico completo en formato PDF con todas las visualizaciones y analisis.</p>
                <a id="link-pdf" href="/api/reporte/pdf" target="_blank"><button class="btn btn-success">Descargar Reporte PDF</button></a>
            </div>
        </div>
    </div>

    <script>
        async function cargarDatosResumen() {
            try {
                const r = await fetch('/api/datos');
                const d = await r.json();
                if (d.error) {
                    document.getElementById('datos-resumen').innerHTML = '<p style="color:#c62828;">No hay datos unificados. Ejecuta el ETL primero.</p>';
                    return;
                }
                document.getElementById('datos-resumen').innerHTML = `
                    <div class="grid-3">
                        <div class="metric"><div class="value">${d.registros}</div><div class="label">Registros</div></div>
                        <div class="metric"><div class="value">${d.activos.length}</div><div class="label">Activos</div></div>
                        <div class="metric"><div class="value">${d.fecha_min} / ${d.fecha_max}</div><div class="label">Periodo</div></div>
                    </div>
                `;
                const selects = ['sim-ticker1', 'sim-ticker2', 'pat-ticker', 'vela-ticker'];
                selects.forEach(id => {
                    const sel = document.getElementById(id);
                    if (sel) {
                        sel.innerHTML = d.activos.map(t => `<option value="${t}">${t}</option>`).join('');
                    }
                });
            } catch(e) {
                document.getElementById('datos-resumen').innerHTML = '<p style="color:#c62828;">Error al conectar con el servidor.</p>';
            }
        }

        async function ejecutarETL() {
            const div = document.getElementById('resultado-etl');
            div.innerHTML = '<p>Ejecutando ETL...</p>';
            try {
                const r = await fetch('/api/etl', { method: 'POST' });
                const d = await r.json();
                div.innerHTML = d.error ? `<p style="color:#c62828;">Error: ${d.error}</p>` : `<p style="color:#2e7d32;">${d.mensaje}: ${d.registros} registros, ${d.activos} activos</p>`;
                cargarDatosResumen();
            } catch(e) {
                div.innerHTML = `<p style="color:#c62828;">Error: ${e}</p>`;
            }
        }

        async function compararSimilitud() {
            const t1 = document.getElementById('sim-ticker1').value;
            const t2 = document.getElementById('sim-ticker2').value;
            const div = document.getElementById('resultado-similitud');
            div.innerHTML = '<p>Calculando...</p>';
            try {
                const r = await fetch(`/api/similitud?ticker1=${t1}&ticker2=${t2}`);
                const d = await r.json();
                if (d.error) { div.innerHTML = `<p style="color:#c62828;">${d.error}</p>`; return; }
                div.innerHTML = `
                    <div class="grid-3">
                        <div class="metric"><div class="value">${d.distancia_euclidiana.toFixed(4)}</div><div class="label">Distancia Euclidiana</div></div>
                        <div class="metric"><div class="value">${d.correlacion_pearson.toFixed(4)}</div><div class="label">Correlacion Pearson</div></div>
                        <div class="metric"><div class="value">${d.dtw.toFixed(4)}</div><div class="label">DTW</div></div>
                        <div class="metric"><div class="value">${d.similitud_coseno.toFixed(4)}</div><div class="label">Similitud Coseno</div></div>
                        <div class="metric"><div class="value">${d.distancia_coseno.toFixed(4)}</div><div class="label">Distancia Coseno</div></div>
                    </div>
                `;
            } catch(e) {
                div.innerHTML = `<p style="color:#c62828;">Error: ${e}</p>`;
            }
        }

        async function analizarActivo() {
            const ticker = document.getElementById('pat-ticker').value;
            const div = document.getElementById('resultado-patrones');
            div.innerHTML = '<p>Analizando...</p>';
            try {
                const r = await fetch(`/api/analisis/${ticker}`);
                const d = await r.json();
                if (d.error) { div.innerHTML = `<p style="color:#c62828;">${d.error}</p>`; return; }
                const m = d.metricas_dispersion;
                const badgeClass = d.clasificacion_riesgo === 'Bajo' ? 'badge-bajo' : d.clasificacion_riesgo === 'Medio' ? 'badge-medio' : d.clasificacion_riesgo === 'Alto' ? 'badge-alto' : 'badge-muy-alto';
                div.innerHTML = `
                    <p><strong>Riesgo:</strong> <span class="badge ${badgeClass}">${d.clasificacion_riesgo}</span></p>
                    <div class="grid-2">
                        <div class="metric"><div class="value">${m.volatilidad_anualizada.toFixed(2)}%</div><div class="label">Volatilidad Anualizada</div></div>
                        <div class="metric"><div class="value">${m.volatilidad_diaria.toFixed(2)}%</div><div class="label">Volatilidad Diaria</div></div>
                    </div>
                `;
            } catch(e) {
                div.innerHTML = `<p style="color:#c62828;">Error: ${e}</p>`;
            }
        }

        async function cargarClasificacion() {
            const div = document.getElementById('resultado-clasificacion');
            div.innerHTML = '<p>Cargando...</p>';
            try {
                const r = await fetch('/api/clasificacion');
                const datos = await r.json();
                if (datos.error) { div.innerHTML = `<p style="color:#c62828;">${datos.error}</p>`; return; }
                let html = '<table><tr><th>Ticker</th><th>Volatilidad Anualizada</th><th>Clasificacion</th></tr>';
                datos.forEach(d => {
                    const badgeClass = d.Clasificacion_Riesgo === 'Bajo' ? 'badge-bajo' : d.Clasificacion_Riesgo === 'Medio' ? 'badge-medio' : d.Clasificacion_Riesgo === 'Alto' ? 'badge-alto' : 'badge-muy-alto';
                    html += `<tr><td>${d.Ticker}</td><td>${d.Volatilidad_Anualizada.toFixed(2)}%</td><td><span class="badge ${badgeClass}">${d.Clasificacion_Riesgo}</span></td></tr>`;
                });
                html += '</table>';
                div.innerHTML = html;
            } catch(e) {
                div.innerHTML = `<p style="color:#c62828;">Error: ${e}</p>`;
            }
        }

        async function cargarMapaCalor() {
            document.getElementById('mapa-calor-container').innerHTML = '<img src="/api/grafico/mapa_calor" alt="Mapa de Calor">';
        }

        async function cargarCandlestick() {
            const ticker = document.getElementById('vela-ticker').value;
            document.getElementById('candlestick-container').innerHTML = `<img src="/api/grafico/candlestick/${ticker}?t=${Date.now()}" alt="Candlestick ${ticker}">`;
        }

        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('tab-' + tab).classList.add('active');
            event.target.classList.add('active');
        }

        cargarDatosResumen();
    </script>
</body>
</html>
"""
