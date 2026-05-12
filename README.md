# financial-time-series-algorithms

Algorithmic analysis of financial time series with explicit implementation of similarity metrics and complexity analysis.

Proyecto academico de Analisis de Algoritmos aplicado a series de tiempo financieras.

El objetivo es implementar explicitamente algoritmos de similitud, deteccion de patrones y medicion de volatilidad sobre datos reales obtenidos mediante procesos ETL desarrollados manualmente.

Integrantes

- Adriana Garcia Garaviz
- Daniela Lopez Guarin
- Jose Yovany Beltran Matallana

Requisitos previos

- Python 3.10 o superior
- Git instalado

Verificar version de Python:

bash
python --version

# Configuracion del entorno (OBLIGATORIO)

Cada integrante debe crear su propio entorno virtual, como un espacio aislado donde se instalan las dependencias de un proyecto sin afectar el Python global del sistema. Esto evita conflictos de versiones entre proyectos, que una libreria actualizada rompa el codigo o instalar paquetes innecesarios globalmente. Para ellos se siguen las siguientes instrucciones:

Clonar el repositorio:
git clone https://github.com/TU-USUARIO/financial-time-series-algorithms.git
cd financial-time-series-algorithms

Crear entorno virtual:
python -m venv venv

Activar entorno virtual:
venv\Scripts\activate
Debe aparecer (venv) en la terminal.

Instalar dependencias:
pip install -r requirements.txt

Ejecutar interfaz gráfica:
streamlit run app.py

Flujo de trabajo en equipo

No trabajar directamente sobre master. Crear siempre una rama nueva y Despues de trabajar:

git add .
git commit -m "Descripcion clara del cambio realizado"
git push origin <rama>

Luego crear Pull Request en GitHub.

---

## Requerimiento 1: Pipeline ETL y Algoritmos de Ordenamiento

### Pipeline ETL (`src/requerimiento_1/`)

- **descarga.py**: Descarga datos historicos desde Yahoo Finance API con rate limiting y reintentos.
- **limpieza.py**: Limpieza de datos (ordenamiento, deduplicacion, interpolacion).
- **unificacion.py**: Consolidacion en DataFrame unificado en formato largo.
- **ordenamiento.py**: Analisis de top 15 volumenes por activo.

### Algoritmos de Ordenamiento (`src/algorithms/sorting.py`)

12 algoritmos implementados manualmente: Selection Sort, Binary Insertion Sort, Gnome Sort, Comb Sort, Quick Sort, Heap Sort, Tree Sort, Pigeonhole Sort, Bucket Sort, Radix Sort, Bitonic Sort, Tim Sort.

### Multiplicacion de Matrices (`src/multiplicacionMatrices/`)

15 algoritmos: Naive (3 variantes), Winograd (2 variantes), Strassen (2 variantes), Blocked Row/Column (secuencial y paralelo).

---

## Requerimiento 2: Algoritmos de Similitud de Series de Tiempo

### Modulo de Similitud (`src/similarity/`)

Se implementan cuatro algoritmos de similitud entre series de tiempo financieras:

| Algoritmo                  | Complejidad Tiempo | Complejidad Espacio | Rango de Salida |
| -------------------------- | ------------------ | ------------------- | --------------- |
| **Distancia Euclidiana**   | O(n)               | O(1)                | [0, inf)        |
| **Correlacion de Pearson** | O(n)               | O(1)                | [-1, 1]         |
| **Dynamic Time Warping**   | O(n\*m)            | O(n\*m)             | [0, inf)        |
| **Similitud por Coseno**   | O(n)               | O(1)                | [-1, 1]         |

#### 1. Distancia Euclidiana (`src/similarity/euclidean.py`)

Mide la distancia geometrica directa entre dos series punto a punto.

**Formula**: d(X, Y) = sqrt(sum((xi - yi)^2))

**Funciones**:

- `euclidean_distance()`: Distancia euclidiana raw.
- `euclidean_distance_normalized()`: RMSD (Root Mean Square Deviation).
- `euclidean_similarity_score()`: Puntaje de similitud en [0, 1].

#### 2. Correlacion de Pearson (`src/similarity/pearson.py`)

Mide la relacion lineal entre dos activos sobre sus retornos diarios.

**Formula**: r = Cov(X, Y) / (sigma_X \* sigma_Y)

**Funciones**:

- `pearson_correlation()`: Coeficiente de correlacion en [-1, 1].
- `interpret_correlation()`: Interpretacion textual del coeficiente.

#### 3. Dynamic Time Warping (`src/similarity/dtw.py`)

Encuentra el alineamiento optimo entre series que pueden diferir en velocidad o fase mediante programacion dinamica.

**Formula**: D[i,j] = |xi - yj| + min(D[i-1,j], D[i,j-1], D[i-1,j-1])

**Funciones**:

- `dynamic_time_warping()`: Distancia DTW.
- `dynamic_time_warping_normalized()`: DTW normalizado por longitud del camino.
- `get_dtw_path()`: Recupera el camino de warping optimo.
- `dtw_similarity_score()`: Puntaje de similitud en [0, 1].

#### 4. Similitud por Coseno (`src/similarity/cosine.py`)

Mide el angulo entre dos vectores de rendimientos diarios, capturando similitud de patron independiente de magnitud.

**Formula**: cos(theta) = (X . Y) / (||X|| \* ||Y||)

**Funciones**:

- `cosine_similarity()`: Similitud por coseno en [-1, 1].
- `cosine_angle()`: Angulo en grados entre los vectores.
- `interpret_cosine_similarity()`: Interpretacion textual.

### Ejecucion del Analisis

```bash
python scripts/similarity_analysis.py
```

El script permite:

1. Seleccionar dos activos del dataset unificado.
2. Visualizar series temporales (precios normalizados, retornos, retornos acumulados).
3. Calcular los 4 algoritmos de similitud con tiempos de ejecucion.
4. Ver explicaciones matematicas, descripciones algoritmicas y analisis de complejidad.
5. Generar graficos en `results/similarity/`.

### Pruebas

```bash
python scripts/test_similarity.py
```

### Comparacion de Algoritmos

| Aspecto            | Euclidiana | Pearson | DTW | Coseno    |
| ------------------ | ---------- | ------- | --- | --------- |
| Mas rapido         | Si         | Si      | No  | Si        |
| Maneja desfases    | No         | No      | Si  | No        |
| Diferente longitud | No         | No      | Si  | No        |
| Captura forma      | Parcial    | Lineal  | Si  | Direccion |
| Sensible a escala  | Si         | No      | Si  | No        |

---

## Reproducibilidad y Datos

### Pipeline ETL Automatizado y Reproducible

El proyecto **no depende de datos estáticos pre-descargados**. Todo el proceso de descarga, limpieza y unificación de datos es completamente **automatizado y reproducible desde cero**.

**Flujo de reproducibilidad:**

1. Al ejecutar `streamlit run app.py`, la interfaz verifica si existe el dataset unificado (`data/processed/precios_unificados.csv`).
2. Si el archivo no existe, la app indica que se debe ejecutar el ETL.
3. En la sección "ETL" de la interfaz, el usuario puede hacer clic en **"Descargar y unificar datos desde cero"**.
4. El sistema automáticamente:
   - Descarga 5+ años de histórico diario de 20+ activos desde **Yahoo Finance API** (sin librerías de alto nivel como yfinance)
   - Implementa rate limiting y reintentos con exponential backoff
   - Limpia duplicados, interpola valores faltantes y detecta anomalías
   - Unifica todos los datos en un único DataFrame en formato largo
   - Guardar el dataset procesado

**Verificación de reproducibilidad:**

Un evaluador puede clonar el repositorio, instalar dependencias y ejecutar:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Luego hacer clic en "Descargar y unificar datos desde cero" para regenerar completamente el dataset desde fuentes públicas.

---

## Uso de Herramientas de Inteligencia Artificial

### Declaración de IA Generativa

Este proyecto ha utilizado **GitHub Copilot** como herramienta de apoyo durante el desarrollo. De acuerdo con las especificaciones del curso, el uso de IA se ha limitado a:

**✓ Usos permitidos y realizados:**

- Revisión de sintaxis y correctness de código
- Refactoring de código existente para mejorar legibilidad
- Sugerencias de nombres de variables y funciones
- Generación de comentarios y documentación técnica
- Validación de fórmulas matemáticas en implementaciones de algoritmos
- Revisión de prácticas de manejo de errores y casos edge

**✗ Usos NO realizados:**

- Implementación directa de algoritmos de similitud (distancia euclidiana, Pearson, DTW, coseno)
- Lógica central del pipeline ETL (descarga, limpieza, unificación)
- Detección de patrones y cálculo de volatilidad
- Análisis y decisiones sobre complejidad algorítmica

**Justificación:**

La implementación de los algoritmos solicitados fue realizada **manualmente por los estudiantes**, con Copilot actuando como asistente para validación sintáctica y documentación. Todos los algoritmos de similitud están explícitamente codificados con su lógica interna visible y analizable, cumpliendo así el requisito de "comportamiento algorítmico completamente transparente".

**Transparencia de cambios:**

Todos los usos de IA están trazables a través del historial de commits de Git. Los estudiantes mantuvieron control total sobre el flujo algorítmico y las decisiones de diseño arquitectónico.

---
