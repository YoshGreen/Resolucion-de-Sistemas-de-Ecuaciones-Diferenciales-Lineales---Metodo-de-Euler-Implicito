# `agent.md` — Especificación de Agente para Proyecto de Métodos Numéricos

## 1. Rol y Especialidad del Agente
Actúa como un **Especialista Senior en Métodos Numéricos, Álgebra Lineal Computacional y Desarrollo Científico en Python**. Tu objetivo es diseñar, implementar, verificar y documentar un proyecto académico completo sobre la **Resolución de Sistemas de Ecuaciones Diferenciales Ordinarias (EDOs) Lineales mediante el Método de Euler Implícito (Backward Euler)**.

Todo el código del proyecto debe escribirse en **Python 3.10+**, priorizando rigor matemático, estabilidad numérica, reproducibilidad y visualización científica de alto impacto.

---

## 2. Fundamento Matemático Obligatorio
El núcleo del proyecto resuelve sistemas lineales de EDOs de primer orden con valor inicial (PVI):

$$\mathbf{y}'(t) = A\mathbf{y}(t) + \mathbf{g}(t), \qquad \mathbf{y}(t_0) = \mathbf{y}_0$$

donde $\mathbf{y}(t) \in \mathbb{R}^n$, $A \in \mathbb{R}^{n \times n}$ es la matriz de coeficientes constantes y $\mathbf{g}(t) \in \mathbb{R}^n$ es el término de forzamiento.

### Esquema de Euler Implícito
Con tamaño de paso $h > 0$ y malla $t_{k+1} = t_k + h$:

$$\mathbf{y}_{k+1} = \mathbf{y}_k + h\left(A\mathbf{y}_{k+1} + \mathbf{g}(t_{k+1})\right)$$

Reordenando en forma de sistema lineal en cada paso:

$$(I - hA)\mathbf{y}_{k+1} = \mathbf{y}_k + h\mathbf{g}(t_{k+1})$$

### Propiedades que el Agente Debe Implementar y Demostrar
1. **A-estabilidad y L-estabilidad:** La función de estabilidad es $R(z) = \frac{1}{1 - z}$ con $z = h\lambda$. Se cumple $|R(z)| \le 1$ para todo $\text{Re}(z) \le 0$, y $\lim_{\text{Re}(z)\to -\infty} |R(z)| = 0$.
2. **Rigidez (*Stiffness*):** Calcular automáticamente los valores propios $\lambda_i$ de $A$ y la razón de rigidez $S = \frac{\max_i |\text{Re}(\lambda_i)|}{\min_i |\text{Re}(\lambda_i)|}$ cuando $\text{Re}(\lambda_i) < 0$.
3. **Eficiencia Computacional:** Cuando $A$ y $h$ son constantes, **nunca** invertir $(I - hA)$ explícitamente en cada iteración. Precomputar una sola factorización LU mediante `scipy.linalg.lu_factor(I - h*A)` y resolver cada paso en $O(n^2)$ con `scipy.linalg.lu_solve`.
4. **Verificación de Convergencia:** Medir el error global en norma infinito ($\|\mathbf{e}\|_\infty$) y norma euclidiana ($\|\mathbf{e}\|_2$) frente a la solución exacta o de referencia, verificando el orden teórico $O(h)$.

---

## 3. Estructura del Proyecto

```text
proyecto_euler_implicito/
├── agent.md                              # Reglas y arquitectura del agente
├── design.md                             # Sistema de diseño UI/UX del dashboard
├── prompt_antigravity.md                 # Prompt maestro de construcción
├── requirements.txt                      # Dependencias Python
├── core/
│   ├── __init__.py
│   └── euler_implicito.py                # Motor numérico reutilizable (Implícito, Explícito, Exacto, Estabilidad)
├── ejercicios/
│   ├── ejercicio1_circuito_rlc_rigido.py # Sistema 2x2 rígido (Circuito RLC acoplado)
│   ├── ejercicio2_reaccion_quimica_cadena.py # Sistema 3x3 rígido (Cinética A -> B -> C)
│   └── ejercicio3_sismo_edificio_2pisos.py   # Sistema 4x4 no homogéneo (Edificio bajo sismo)
├── dashboard/
│   ├── app.py                            # Aplicación principal Streamlit + Plotly
│   └── styles.css                        # Tema visual oscuro y animaciones del sidebar
├── img/                                  # Carpeta destino de TODAS las gráficas (.png) y animaciones (.gif)
└── informe.tex                           # Informe académico completo en LaTeX (UMSA)
```

---

## 4. Convenciones de Código y Calidad

### 4.1 Estándares Python
- Utilizar **type hints** (`np.ndarray`, `Callable[[float], np.ndarray]`, `tuple`, `dict`) y **docstrings** en formato NumPy.
- Usar `numpy`, `scipy.linalg`, `matplotlib` (con `matplotlib.animation.FuncAnimation` + `PillowWriter`) para los scripts de ejercicios, y `streamlit` + `plotly` para el dashboard interactivo.
- Asegurar reproducibilidad determinista y manejo seguro de singularidades (verificar que $\det(I - hA) \neq 0$ o número de condición `np.linalg.cond(M)` antes de resolver).
- Evitar rutas absolutas hardcodeadas: usar `pathlib.Path` relativo a la raíz del proyecto para guardar siempre en `img/`.

### 4.2 Política de Guardado en `img/`
- Cada script de ejercicio debe crear automáticamente la carpeta `img/` si no existe (`IMG_DIR.mkdir(parents=True, exist_ok=True)`).
- Exportar figuras estáticas en **PNG a 300 DPI** (`bbox_inches="tight"`) con nombres consistentes:
  - `img/ej1_rlc_comparacion.png` y `img/ej1_rlc_animacion.gif`
  - `img/ej2_cinetica_quimica.png` y `img/ej2_cinetica_animacion.gif`
  - `img/ej3_edificio_sismo.png` y `img/ej3_edificio_animacion.gif`
- En el dashboard, incluir un botón para **guardar o regenerar** la gráfica activa directamente en `img/`.

### 4.3 Reglas del Dashboard Interactivo
- Seguir estrictamente la paleta, tipografía, layout y animaciones definidas en `design.md`.
- El menú de navegación debe ubicarse en el **lado izquierdo** y permitir al usuario **ocultarlo (colapsar) o mantenerlo visible (fijar)** sin perder el estado de los controles (`st.session_state`).
- Toda simulación interactiva debe ejecutarse desde `core/euler_implicito.py`; prohibido duplicar ecuaciones o lógica numérica dentro de los componentes de interfaz.
- Las gráficas interactivas deben construirse con **Plotly** (hover detallado, zoom, pan, controles Play/Pause en frames animados y sliders de paso $h$ y rigidez).

### 4.4 Reglas del Informe LaTeX (`informe.tex`)
- Mantener la portada institucional (UMSA — Facultad de Ciencias Puras y Naturales, Carrera de Informática), usando `\IfFileExists{img/LOGOumsa.png}` para garantizar compilación limpia con o sin el logotipo local.
- Referenciar directamente las figuras generadas en `img/` mediante `\includegraphics`.
- Utilizar `amsmath`, `amssymb`, `booktabs`, `tabularx`, `graphicx` y `hyperref`.
- Toda tabla numérica de errores o estabilidad debe reflejar valores reales obtenidos por los scripts de Python.

---

## 5. Flujo de Trabajo y Verificación del Agente
Antes de dar por terminada cualquier tarea o modificación, el agente debe ejecutar esta lista de verificación:

1. **Verificación Numérica:** Ejecutar los 3 scripts en `ejercicios/` y comprobar que terminan con código de salida `0`, sin advertencias de `NaN`/`Inf` en Euler Implícito.
2. **Verificación de Artefactos Visuales:** Confirmar que los 6 archivos (`.png` y `.gif`) existen en `img/` y tienen tamaño mayor a 0 bytes.
3. **Verificación del Dashboard:** Ejecutar `streamlit run dashboard/app.py` (o validar importaciones y sintaxis) comprobando que el menú izquierdo colapsa/fija correctamente y las gráficas interactivas responden a cambios en $h$.
4. **Verificación LaTeX:** Compilar `informe.tex` con `pdflatex` (2 pasadas) verificando cero errores de sintaxis y referencias cruzadas resueltas.
