# `design.md` — Sistema de Diseño UI/UX del Dashboard Interactivo

## 1. Identidad Visual y Concepto Temático
- **Nombre del Dashboard:** **EulerLab — Observatorio de Sistemas Dinámicos Rígidos**
- **Concepto Estético:** *PhaseSpace Observatory* (Laboratorio Científico Oscuro). Inspirado en planos complejos de estabilidad, retratos de fase de sistemas dinámicos y consolas de simulación física.
- **Objetivo Visual:** Que el estudiante o docente distinga al instante la **estabilidad incondicional** del Método de Euler Implícito frente a la **divergencia explosiva** del Método de Euler Explícito, mediante contraste cromático semántico, animaciones fluidas y gráficas interactivas.

---

## 2. Paleta de Colores Semántica

| Rol Visual | Nombre | Código HEX | Uso en el Dashboard |
| :--- | :--- | :--- | :--- |
| Fondo principal | Deep Space Navy | `#0B1120` | Lienzo global de la aplicación y fondo de gráficas |
| Superficie de tarjetas | Slate Observatory | `#111827` | Contenedores KPI, paneles de parámetros y cards |
| Superficie elevada | Midnight Steel | `#1E293B` | Sidebar izquierdo, estados hover y tablas |
| Borde sutil | Hairline Slate | `#334155` | Divisores finos (1px) y contornos de tarjetas |
| **Euler Implícito** | **Electric Cyan** | `#06B6D4` | Curva principal, acento de navegación activa y glow |
| **Solución Exacta** | **Precision Emerald** | `#10B981` | Curva de referencia analítica y badge "Estable" |
| **Euler Explícito** | **Divergence Coral** | `#F97316` | Curva comparativa y advertencia de oscilación |
| **Alerta / Explosión** | **Critical Crimson** | `#EF4444` | Badge "Inestable", región fuera del disco de estabilidad |
| **Eigenvalores / Rigidez** | **Spectral Violet** | `#8B5CF6` | Puntos $z = h\lambda_i$ en el plano complejo y acentos |
| Texto principal | Crisp Snow | `#F8FAFC` | Títulos, valores KPI y texto de lectura (contraste > 12:1) |
| Texto secundario | Muted Cool Gray | `#94A3B8` | Etiquetas de ejes, subtítulos y notas técnicas |

---

## 3. Tipografía y Jerarquía
- **Fuente de Interfaz y Títulos:** `Plus Jakarta Sans` o `Inter` (fallback: `system-ui, sans-serif`).
- **Fuente Matemática, Código y KPIs:** `JetBrains Mono` (fallback: `Fira Code, monospace`) con `font-variant-numeric: tabular-nums` para evitar saltos horizontales durante las animaciones de parámetros.
- **Escala Tipográfica:**
  - Título de módulo: `26px`, peso `700`, tracking `-0.02em`.
  - Subtítulo de sección: `17px`, peso `600`, color `#E2E8F0`.
  - Valor KPI numérico: `24px`, `JetBrains Mono`, peso `700`.
  - Cuerpo descriptivo: `14.5px`, interlineado `1.6`, color `#CBD5E1`.
  - Etiquetas de ejes y metadatos: `12px`, mayúsculas suaves o monospace.

---

## 4. Arquitectura de Layout y Menú Lateral Izquierdo (Colapsable / Fijable)

### 4.1 Comportamiento del Menú Izquierdo (`Sidebar`)
El menú se ubica de forma fija en el **lado izquierdo** con dos modos controlables por el usuario:

1. **Modo Expandido / Fijado (`280px`):**
   - Muestra logotipo temático **EulerLab**, subtítulo *"Sistemas de EDOs Lineales"*, botones de navegación con iconos, estado de fijación (**Mantener abierto / Pin**) y panel inferior con el botón de exportación rápida a `img/`.
2. **Modo Oculto / Colapsado (`0px` o riel compacto de `60px`):**
   - El botón hamburguesa/chevron en la esquina superior izquierda colapsa suavemente el panel (`transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1)`), expandiendo el área de gráficas interactivas al 100% del ancho de pantalla.
   - En **Streamlit**, se combina `st.sidebar` (colapsable de forma nativa) con un toggle de estado `"Mantener menú fijo"` en `st.session_state` y CSS personalizado para controlar el ancho, el sombreado lateral y el botón flotante de reapertura.

### 4.2 Estructura de Secciones del Menú Izquierdo
1. **Inicio y Fundamento Teórico:** Resumen interactivo de $\mathbf{y}' = A\mathbf{y} + \mathbf{g}(t)$, esquema matricial $(I - hA)\mathbf{y}_{k+1} = \mathbf{y}_k + h\mathbf{g}(t_{k+1})$ y flujo animado de factorización LU.
2. **Laboratorio de Estabilidad (Plano Complejo):** Gráfico interactivo de la región de estabilidad $|1 - z| \ge 1$ vs $|1 + z| \le 1$, donde mover el slider de $h$ desplaza en tiempo real los puntos $z_i = h\lambda_i$.
3. **Ejercicio 1 — Circuito RLC Rígido (2×2):** Simulación interactiva + comparación Implícito vs Explícito vs Exacto + reproductor de `img/ej1_rlc_animacion.gif`.
4. **Ejercicio 2 — Cinética Química en Cadena (3×3):** Concentraciones $A \to B \to C$, verificación de conservación de masa + reproductor de `img/ej2_cinetica_animacion.gif`.
5. **Ejercicio 3 — Dinámica Sísmica de Edificio (4×4):** Oscilación de 2 pisos bajo excitación sísmica, energía mecánica + reproductor de `img/ej3_edificio_animacion.gif`.
6. **Galería `img/` y Reporte LaTeX:** Visor de todas las gráficas y GIFs guardados en `img/`, tabla de errores globales y botón para descargar o inspeccionar `informe.tex`.

---

## 5. Especificación de Componentes y Tarjetas

### 5.1 Fila Superior de KPIs (4 Tarjetas Simétricas)
Cada ejercicio muestra en la parte superior 4 tarjetas con fondo `#111827`, borde `1px solid #334155`, radio `12px` y barra superior de acento (`3px`):
- **KPI 1 — Paso Temporal ($h$):** Valor actual y número total de pasos $N$.
- **KPI 2 — Razón de Rigidez ($S$):** Cociente de valores propios con etiqueta semántica (*Moderado* / *Rígido* / *Extremo*).
- **KPI 3 — Error Global Implícito ($\|e\|_\infty$):** Error en notación científica (`1.42e-03`) en color `#06B6D4`.
- **KPI 4 — Estado de Estabilidad:** Pill animado en `#10B981` (`IMPLÍCITO: ESTABLE`) junto al indicador de Euler Explícito (`ESTABLE` o `DIVERGENTE` en `#EF4444` con pulso suave).

### 5.2 Panel de Controles Interactivos
Ubicado sobre o junto a la gráfica principal dentro de una tarjeta colapsable:
- Slider de paso temporal $h$ (escala logarítmica o pasos discretos finos).
- Slider de horizonte temporal $T$.
- Toggle para mostrar/ocultar: *Solución Exacta*, *Euler Implícito*, *Euler Explícito*.
- Botón **"Guardar gráfica actual en `img/`"** con confirmación visual (*toast*).

---

## 6. Animaciones y Gráficas Interactivas

### 6.1 Animaciones de Gráficas (Plotly + Matplotlib GIF)
- **Plotly Frames Interactivos:** Botones nativos `▶ Play` y `⏸ Pause` con slider temporal para observar paso a paso cómo avanza el método en el tiempo y en el **retrato de fase** $(y_1, y_2)$.
- **Sincronización con `img/`:** Cada ejercicio permite alternar entre la vista **Interactiva Plotly** (para explorar con zoom, hover y cambio de $h$) y la **Animación Renderizada (`img/*.gif`)** generada por el script científico de Python.
- **Curva de Convergencia Log-Log:** Gráfica interactiva de error global vs $h$ con recta de referencia de pendiente $1$ ($O(h)$).

### 6.2 Micro-Animaciones CSS (Sutiles y Funcionales)
- **Entrada de secciones:** `fadeSlideUp` de `0.30s ease-out` (desplazamiento `8px`).
- **Sidebar colapsable:** Transición suave de ancho y opacidad sin saltos bruscos de layout.
- **Badge de divergencia:** Pulso suave (`keyframes pulseDanger`) únicamente cuando Euler Explícito viola el criterio $|1 + h\lambda_{\max}| > 1$, reforzando visualmente el concepto matemático de inestabilidad numérica.
- **Respeto de accesibilidad:** Incluir `@media (prefers-reduced-motion: reduce)` para desactivar animaciones CSS si el sistema operativo lo solicita.

---

## 7. Stack Tecnológico Recomendado para el Dashboard
- **Framework Web en Python:** `streamlit>=1.36` (con `initial_sidebar_state="expanded"` y CSS inyectado desde `dashboard/styles.css`).
- **Gráficas Interactivas y Animaciones Web:** `plotly>=5.22` (`plotly.graph_objects` con `layout.updatemenus` y `frames`).
- **Cálculo Científico:** `numpy`, `scipy`.
- **Exportación de Imágenes desde el Dashboard:** `kaleido` (para guardar gráficas Plotly en `img/`) + integración directa con los scripts `matplotlib` de `ejercicios/`.
