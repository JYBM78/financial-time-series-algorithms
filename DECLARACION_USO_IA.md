# Declaración Explícita de Uso de Herramientas de Inteligencia Artificial

**Proyecto:** Financial Time Series Algorithms - Análisis de Algoritmos  
**Curso:** Análisis de Algoritmos  
**Integrantes:** Adriana Garcia Garaviz, Daniela Lopez Guarin, Jose Yovany Beltran Matallana  
**Fecha:** Mayo 2026  
**Herramienta IA Utilizada:** GitHub Copilot (modelo OpenAI GPT-based)

---

## 1. Contexto y Restricciones

De acuerdo con las especificaciones del proyecto, se establece que:

> "El uso de herramientas de inteligencia artificial generativa como apoyo al desarrollo del proyecto deberá ser declarado explícitamente. Dichas herramientas podrán utilizarse como soporte, **pero no podrán reemplazar el diseño algorítmico ni el análisis formal solicitado en el curso**."

Esta declaración cumple con tal requisito, documentando de manera transparente y detallada cómo se utilizó GitHub Copilot en el desarrollo.

---

## 2. Herramienta: GitHub Copilot

### 2.1 Descripción Técnica

- **Proveedor:** GitHub (Microsoft)
- **Modelo Subyacente:** OpenAI GPT (transformers)
- **Capacidad:** Sugerencia de código en contexto basada en comentarios, docstrings y código anterior
- **Modo de Uso:** Asistente integrado en VS Code durante el desarrollo

### 2.2 Ventajas Operacionales Observadas

- Aceleración en escritura de código repetitivo (boilerplate)
- Sugerencias de convenciones de nomenclatura Python
- Generación de docstrings con formato y estructura correcta
- Validación de sintaxis a nivel de sugerencia
- Propuestas de manejo de errores comunes

---

## 3. Usos Realizados (✓ Permitidos)

### 3.1 Revisión y Validación Sintáctica

**Contexto:** Durante la codificación de funciones matemáticas complejas  
**Acción:** Copilot sugería correcciones de sintaxis Python cuando se detectaban errores de tipo o estructura  
**Ejemplo:** Validación de indexación numpy, uso correcto de type hints  
**Impacto:** Reducción de errores triviales de sintaxis, no afectó lógica algorítmica

### 3.2 Refactoring y Optimización de Código Existente

**Contexto:** Mejora de legibilidad en funciones ya implementadas  
**Acciones realizadas:**

- Cambio de nombres de variables poco descriptivos a nombres más claros
- Simplificación de condicionales anidados
- Reorganización de imports siguiendo PEP 8

**Ejemplo concreto:**

```python
# Antes (codificado manualmente)
for i in range(len(a)):
    for j in range(len(a[0])):
        s = 0
        for k in range(len(b)):
            s += a[i][k] * b[k][j]
        c[i][j] = s

# Después (refactoring con apoyo de Copilot para legibilidad)
for i in range(n):
    for j in range(m):
        producto_punto = 0
        for k in range(p):
            producto_punto += matriz_a[i][k] * matriz_b[k][j]
        matriz_resultado[i][j] = producto_punto
```

**Impacto:** Mejora de mantenibilidad, sin cambio en algoritmo subyacente

### 3.3 Generación de Documentación Técnica

**Contexto:** Creación de docstrings y comentarios explicativos  
**Acciones:**

- Generación de docstrings formato Google/NumPy para funciones
- Creación de comentarios explicativos para bloques de código complejos
- Documentación de parámetros y valores de retorno

**Ejemplo:**

```python
def dynamic_time_warping(a, b):
    """
    Calcula la distancia Dynamic Time Warping entre dos series.

    Parámetros:
    -----------
    a : array-like
        Primera serie temporal
    b : array-like
        Segunda serie temporal

    Retorna:
    --------
    float
        Distancia DTW normalizada por la longitud del camino

    Complejidad: O(n*m) tiempo, O(n*m) espacio
    """
    # ... implementación ...
```

**Impacto:** Mejora de documentación, facilita comprensión de código

### 3.4 Sugerencias de Nombres y Convenciones

**Contexto:** Nomenclatura de variables, funciones y clases  
**Ejemplos de sugerencias aceptadas:**

- `ticker` en lugar de `t`
- `correlacion_pearson()` en lugar de `corr_p()`
- `metricas_dispersion` en lugar de `metrics_disp`

**Impacto:** Código más legible, cumplimiento de convenciones Python

### 3.5 Manejo de Errores y Casos Edge

**Contexto:** Implementación de validaciones y excepciones  
**Acciones:**

- Sugerencias para validar entrada de datos (None checks, tipo de datos)
- Implementación de try-except blocks estándar
- Manejo de divisiones por cero en fórmulas matemáticas

**Ejemplo:**

```python
def correlacion_pearson(a, b):
    # ... cálculos ...
    denom = np.sqrt(var_x * var_y)
    if denom == 0:  # Validación sugerida por Copilot
        return 0.0
    return cov / denom
```

**Impacto:** Robustez del código, prevención de excepciones

---

## 4. Usos NO Realizados (✗ No Permitidos)

### 4.1 Implementación Directa de Algoritmos de Similitud

**Restricción:** "Los algoritmos deberán ser implementados de forma explícita por los estudiantes"

**Algoritmos implementados manualmente (sin generar completamente con IA):**

1. **Distancia Euclidiana** - Implementada manualmente desde fórmula
2. **Correlación de Pearson** - Cálculo manual de covarianza y varianzas
3. **Dynamic Time Warping (DTW)** - Programación dinámica completamente explícita
4. **Similitud por Coseno** - Producto punto y normas calculados manualmente

**Justificación:** Aunque Copilot sugería implementaciones, los estudiantes eligieron reimplementar desde cero basándose en la fórmula matemática para garantizar comprensión completa.

### 4.2 Lógica del Pipeline ETL

**Restricción:** "La obtención de los datos deberá realizarse mediante peticiones explícitas"

**Componentes NO generados automáticamente:**

- Construcción manual de URLs para Yahoo Finance API
- Parsing manual de respuestas JSON
- Lógica de limpieza (deduplicación, interpolación)
- Unificación en formato largo

**Ejemplo de control manual:**

```python
# Construcción explícita de request, sin usar yfinance
url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
params = {
    "period1": int(fecha_inicio.timestamp()),
    "period2": int(fecha_fin.timestamp()),
    "interval": "1d"
}
# Manejo manual de respuesta
response = requests.get(url, params=params, headers=headers)
```

### 4.3 Decisiones de Complejidad Algorítmica

**Restricción:** "Análisis formal de la complejidad algorítmica"

**No delegado a IA:**

- Análisis O(n) vs O(n²) vs O(n log n)
- Justificación de trade-offs entre tiempo y espacio
- Comparación de enfoques alternativos

**Documentación de complejidad:** Completamente realizada por estudiantes

### 4.4 Arquitectura y Diseño del Sistema

**Restricción:** "Diseño e implementación de una serie de algoritmos"

**Decisiones de diseño NO delegadas:**

- Estructura modular por requerimientos (requerimiento_1/, etc.)
- Selección de framework (Streamlit vs Flask)
- Interfaz de usuario y flujo de interacción
- Formato de almacenamiento y serialización de datos

---

## 5. Análisis de Impacto en Integridad Académica

### 5.1 Criterio de Transparencia

✓ **Cumplido:** Esta declaración documenta explícitamente cada uso de IA  
✓ **Cumplido:** Distinción clara entre trabajo manual vs asistido  
✓ **Cumplido:** Justificación de por qué IA no fue usada en componentes críticos

### 5.2 Criterio de Aprendizaje

✓ **Cumplido:** Los algoritmos fueron estudiados y entendidos antes de implementarlos  
✓ **Cumplido:** Las decisiones algorítmicas fueron tomadas por estudiantes  
✓ **Cumplido:** El análisis de complejidad fue realizado de forma rigurosa

### 5.3 Criterio de Reproducibilidad

✓ **Cumplido:** Cualquier evaluador puede ejecutar el código sin IA  
✓ **Cumplido:** La lógica algorítmica es completamente transparente  
✓ **Cumplido:** Todos los cálculos son verificables manualmente

### 5.4 Criterio de Originalidad

⚠ **Consideración:** Aunque Copilot sugiere código, la **selección** de qué usar fue manual  
✓ **Cumplido:** Adaptación específica al contexto del proyecto  
✓ **Cumplido:** Extensiones y variaciones personalizadas

---

## 6. Comparación: Con IA vs Sin IA

### 6.1 Tiempo de Desarrollo

| Aspecto                          | Sin IA | Con Copilot | Ahorro |
| -------------------------------- | ------ | ----------- | ------ |
| Escritura de funciones           | 100%   | ~70%        | ~30%   |
| Generación de docstrings         | 100%   | ~40%        | ~60%   |
| Detección de errores sintácticos | 100%   | ~50%        | ~50%   |
| Análisis algorítmico             | 100%   | 100%        | 0%     |
| Diseño de arquitectura           | 100%   | 100%        | 0%     |

### 6.2 Calidad del Código

| Métrica                 | Sin IA | Con Copilot |
| ----------------------- | ------ | ----------- |
| Cumplimiento PEP 8      | ✓      | ✓✓          |
| Docstrings              | ✓      | ✓✓          |
| Type hints              | ✓      | ✓✓          |
| Manejo de errores       | ✓      | ✓✓          |
| Correctness algorítmico | ✓      | ✓           |

---

## 7. Limitaciones Observadas de la IA

Durante el desarrollo, se identificaron limitaciones importantes de GitHub Copilot:

1. **Comprensión limitada del contexto:** Copilot no entiende siempre el dominio financiero específico
2. **Sugerencias genéricas:** Tiende a proponer soluciones estándar, no optimizadas para el problema
3. **No valida matemáticas:** Las fórmulas numéricas requieren validación manual
4. **Sin análisis de complejidad:** No sugiere estructuras basadas en requisitos algorítmicos
5. **Dependencia de ejemplos:** La calidad depende del código anterior en el archivo

**Conclusión:** GitHub Copilot fue útil como acelerador de escritura de código repetitivo, pero **no puede reemplazar el análisis algorítmico riguroso requerido en este curso**.

---

## 8. Cumplimiento de Especificaciones

### 8.1 Requisitos del Proyecto sobre IA

| Requisito                                     | Estado | Evidencia                                      |
| --------------------------------------------- | ------ | ---------------------------------------------- |
| "IA debe ser declarada explícitamente"        | ✓      | Este documento + sección README                |
| "IA podrá utilizarse como soporte"            | ✓      | Usos permitidos documentados (sec 3)           |
| "Pero no podrá reemplazar diseño algorítmico" | ✓      | Algoritmos implementados manualmente (sec 4.1) |
| "Comportamiento algorítmico transparente"     | ✓      | Código explícito y comentado                   |
| "Demostrar comprensión del algoritmo"         | ✓      | Análisis de complejidad manual                 |
| "Reproducibilidad sin IA"                     | ✓      | Código ejecutable sin Copilot                  |

### 8.2 Restricción: No usar librerías encapsuladas

✓ **Cumplido:** Todos los algoritmos implementados from scratch, sin `sklearn.metrics.euclidean_distances()` u equivalentes

---

## 9. Recomendaciones para Evaluadores

1. **Verificar manualmente:** Las funciones en `src/requerimiento_2/algoritmos_similitud/similitud.py` muestran la lógica completa
2. **Revisar commits:** El historial de Git muestra cambios incrementales, no generación masiva
3. **Ejecutar pruebas:** `python scripts/test_similarity.py` valida correctness de algoritmos
4. **Análisis de complejidad:** Documentado en docstrings y comentarios, sin delegación a IA

---

## 10. Conclusiones

GitHub Copilot fue utilizado de manera ética y transparente como **herramienta de soporte** durante el desarrollo, limitándose a:

- Mejoras de legibilidad y sintaxis
- Generación de documentación
- Validación de convenciones

**Permanecieron bajo control completo de los estudiantes:**

- Diseño e implementación de algoritmos
- Análisis de complejidad
- Arquitectura del sistema
- Decisiones algorítmicas críticas

Esta declaración evidencia que el proyecto **cumple con las restricciones y especificaciones del curso** en relación al uso de IA, manteniendo la integridad académica y el rigor algorítmico requerido.

---

**Versión del Documento:** 1.0  
**Última Actualización:** Mayo 12, 2026  
**Firmado por:** Equipo de Desarrollo (Adriana, Daniela, Jose Yovany)
