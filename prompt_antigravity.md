# Prompt Maestro para Google Antigravity

Copia y pega el siguiente prompt directamente en **Google Antigravity** dentro de la carpeta del proyecto (asegurándote de tener `agent.md`, `design.md`, la carpeta `ejercicios/` y `informe.tex` en el espacio de trabajo):

---

```text
Actúa como un especialista en Métodos Numéricos y desarrollo científico en Python.
Antes de escribir cualquier línea de código, lee íntegramente los archivos `agent.md` y `design.md` ubicados en la raíz de este proyecto y síguelos estrictamente como especificación técnica y de diseño.

OBJETIVO DEL PROYECTO:
Construir y verificar un proyecto completo en Python sobre la "Resolución de Sistemas de Ecuaciones Diferenciales Lineales mediante el Método de Euler Implícito", incluyendo:

1. MOTOR NUMÉRICO REUTILIZABLE (`core/euler_implicito.py`):
   - Implementar `euler_implicito_lineal(A, y0, t_span, h, g=None)` usando factorización LU precomputada (`scipy.linalg.lu_factor` y `scipy.linalg.lu_solve`) para resolver `(I - h*A) y_{k+1} = y_k + h*g(t_{k+1})`.
   - Implementar `euler_explicito_lineal(A, y0, t_span, h, g=None)` para comparación directa de estabilidad.
   - Implementar `analizar_estabilidad(A, h)` que retorne los valores propios de `A`, la razón de rigidez `S`, los factores de amplificación `|1/(1 - h*lambda)|` vs `|1 + h*lambda|` y banderas booleanas de estabilidad.
   - Implementar `estudio_convergencia(...)` para calcular errores globales en norma infinito y norma L2 para una secuencia de pasos `h`.

2. INTEGRACIÓN DE LOS 3 EJERCICIOS Y CARPETA `img/`:
   - Verificar y ejecutar los scripts existentes en `ejercicios/`:
     - `ejercicios/ejercicio1_circuito_rlc_rigido.py` (Sistema 2x2 rígido)
     - `ejercicios/ejercicio2_reaccion_quimica_cadena.py` (Sistema 3x3 de cinética química A -> B -> C)
     - `ejercicios/ejercicio3_sismo_edificio_2pisos.py` (Sistema 4x4 de dinámica sísmica de un edificio de 2 pisos)
   - Garantizar que todas las gráficas estáticas (`.png` a 300 DPI) y animaciones (`.gif`) se guarden automáticamente en la carpeta `img/`.

3. DASHBOARD INTERACTIVO EN PYTHON (`dashboard/app.py` + `dashboard/styles.css`):
   - Construir la aplicación con Streamlit + Plotly aplicando la paleta, tipografía y tarjetas KPI definidas en `design.md` (tema oscuro científico "EulerLab").
   - Implementar el menú de navegación en el LADO IZQUIERDO con capacidad de esconderse (colapsar) o mantenerse visible (fijar), conservando el estado en `st.session_state` y con transiciones CSS suaves.
   - Incluir 6 vistas interactivas:
     (a) Inicio y teoría interactiva del método de Euler Implícito.
     (b) Laboratorio de Estabilidad en el plano complejo `z = h*lambda` con slider de `h` que mueva los eigenvalores en vivo.
     (c) Ejercicio 1 (Circuito RLC rígido) con sliders de `h` y rigidez, animación Plotly Play/Pause y visor de `img/ej1_rlc_animacion.gif`.
     (d) Ejercicio 2 (Cinética química A -> B -> C) con gráfica interactiva, conservación de masa y visor de `img/ej2_cinetica_animacion.gif`.
     (e) Ejercicio 3 (Edificio sísmico de 2 pisos) con animación interactiva, retrato de fase y visor de `img/ej3_edificio_animacion.gif`.
     (f) Galería de imágenes de `img/` con botón para regenerar y guardar nuevas gráficas desde el dashboard, más acceso al informe `informe.tex`.

4. ARCHIVO DE DEPENDENCIAS Y VERIFICACIÓN:
   - Generar `requirements.txt` con todas las librerías necesarias (`numpy`, `scipy`, `matplotlib`, `pillow`, `streamlit`, `plotly`, `kaleido`).
   - Ejecutar los 3 scripts de `ejercicios/` y comprobar que las 6 figuras/animaciones se generan sin errores en `img/`.
   - Ejecutar pruebas rápidas del módulo `core/euler_implicito.py` verificando el orden de convergencia O(h) y la A-estabilidad.
   - Verificar que `streamlit run dashboard/app.py` inicie sin errores de importación ni de sintaxis y dejar todo listo para compilar `informe.tex`.
```
