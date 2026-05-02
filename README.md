# financial-time-series-algorithms
Algorithmic analysis of financial time series with explicit implementation of similarity metrics and complexity analysis.

Proyecto académico de Análisis de Algoritmos aplicado a series de tiempo financieras.

El objetivo es implementar explícitamente algoritmos de similitud, detección de patrones y medición de volatilidad sobre datos reales obtenidos mediante procesos ETL desarrollados manualmente.

Integrantes

- Adriana García Garavíz
- Daniela López Guarín
- José Yovany Beltrán Matallana

Requisitos previos

- Python 3.10 o superior
- Git instalado

Verificar versión de Python:

bash
python --version

# Configuración del entorno (OBLIGATORIO)

Cada integrante debe crear su propio entorno virtual, como un espacio aislado donde se instalan las dependencias de un proyecto sin afectar el Python global del sistema. Esto evita conflictos de versiones entre proyectos, que una librería actualizada rompa el código o instalar paquetes innecesarios globalmente. Para ellos se siguen las siguientes instrucciones:

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

No trabajar directamente sobre master. Crear siempre una rama nueva y Después de trabajar:

  git add .
  git commit -m "Descripción clara del cambio realizado"
  git push origin <rama>

Luego crear Pull Request en GitHub.

  
