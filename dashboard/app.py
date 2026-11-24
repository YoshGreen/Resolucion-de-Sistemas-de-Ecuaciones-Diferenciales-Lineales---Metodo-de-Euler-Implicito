"""
EulerLab — Observatorio Interactivo de Sistemas Dinámicos Rígidos
=================================================================
Dashboard científico avanzado para la materia Métodos Numéricos II (UMSA · Grupo 3).
Incluye:
  - Fundamento visual interactivo y animación Manim en 6 etapas.
  - Plano complejo de estabilidad y comparación Euler Implícito vs Crank-Nicolson vs Explícito.
  - Sandbox Libre N×N (matrices arbitrarias y biblioteca de sistemas rígidos notables).
  - Inspector LU (matrices M, P, L, U en vivo, número de condición y descomposición modal).
  - Casos físicos completos (Circuito RLC, Cinética Química, Edificio Sísmico con Canvas 60fps).
  - Benchmark de rendimiento computacional (Speedup CPU y pasos) + Tabla de Richardson O(h).
  - Modo Exposición (Guía del orador para el Grupo 3 y simulador de preguntas del jurado).
  - Galería científica 300 DPI, descarga de datos CSV y generación del informe PDF.
"""

from pathlib import Path
import sys
import io
import subprocess
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import streamlit.components.v1 as components

# Asegurar importación del core numérico
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.euler_implicito import (
    euler_implicito_lineal,
    euler_explicito_lineal,
    crank_nicolson_lineal,
    analizar_estabilidad,
    solucion_exacta_lineal,
    estudio_convergencia,
    descomposicion_lu_inspector,
    descomposicion_modal_lineal,
    tabla_convergencia_formal,
    benchmark_rendimiento_comparativo,
)
from dashboard.animaciones import (
    html_manim_inicio,
    html_animacion_rlc,
    html_animacion_cinetica,
    html_animacion_edificio,
)

# -----------------------------------------------------------------------------
# Configuración inicial de Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EulerLab · Observatorio de EDOs Rígidas",
    page_icon=":material/bolt:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta editorial-científica
BG_COLOR = "#0e1a17"
PANEL_COLOR = "#152823"
BOARD_COLOR = "#091512"
BORDER_COLOR = "#26413a"
EMERALD = "#3ecf9f"      # Euler Implícito / Exacta
CORAL = "#ff7a66"        # Euler Explícito / Alerta
AMBER = "#f4b942"        # Acento principal / Activo
CYAN = "#38bdf8"         # Cian técnico
PURPLE = "#a78bfa"       # Crank-Nicolson / Modos
TEXT_CRISP = "#f1ead8"
TEXT_MUTED = "#a3a58f"

IMG_DIR = ROOT_DIR / "img"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Inyección de estilos CSS responsivos
css_file = ROOT_DIR / "dashboard" / "styles.css"
if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Utilidades visuales
# -----------------------------------------------------------------------------
def aplicar_estilo_plotly(fig: go.Figure, titulo: str = "", height: int = 430) -> go.Figure:
    """Aplica la estética oscura de EulerLab a figuras Plotly."""
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>" if titulo else "",
            font=dict(family="Fraunces, Georgia, serif", size=15, color=TEXT_CRISP),
            x=0.01,
            y=0.97,
        ),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BOARD_COLOR,
        font=dict(family="DM Sans, sans-serif", color=TEXT_CRISP, size=11.5),
        height=height,
        margin=dict(l=45, r=25, t=52, b=45),
        legend=dict(
            bgcolor="rgba(21, 40, 35, 0.9)",
            bordercolor=BORDER_COLOR,
            borderwidth=1,
            font=dict(size=10.5, color=TEXT_CRISP),
        ),
        xaxis=dict(
            gridcolor="#1c332d",
            zerolinecolor=BORDER_COLOR,
            tickfont=dict(family="JetBrains Mono", size=10, color=TEXT_MUTED),
            title_font=dict(size=11.5, color=TEXT_CRISP),
        ),
        yaxis=dict(
            gridcolor="#1c332d",
            zerolinecolor=BORDER_COLOR,
            tickfont=dict(family="JetBrains Mono", size=10, color=TEXT_MUTED),
            title_font=dict(size=11.5, color=TEXT_CRISP),
        ),
        hoverlabel=dict(
            bgcolor=PANEL_COLOR,
            font_family="JetBrains Mono",
            font_size=11,
            bordercolor=AMBER,
        ),
    )
    return fig


def render_kpis(kpi_list: list[dict]) -> None:
    """Renderiza tarjetas KPI responsivas."""
    cards = []
    for item in kpi_list:
        bar_class = f"kpi-bar-{item.get('bar', 'emerald')}"
        cards.append(
            f'<div class="kpi-card">'
            f'<div class="kpi-bar {bar_class}"></div>'
            f'<div class="kpi-label">{item.get("label", "")}</div>'
            f'<div class="kpi-value">{item.get("val", "")}</div>'
            f'<div class="kpi-subtext">{item.get("sub", "")}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="kpi-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_route_stepper(current_idx: int, secciones: list[tuple[str, str]]) -> None:
    """Renderiza la barra de progreso superior."""
    steps_html = ['<div class="route-bar">']
    for idx, (_, nombre_corto) in enumerate(secciones):
        cls = "on" if idx == current_idx else ("done" if idx < current_idx else "")
        dot_content = "✓" if idx < current_idx else str(idx + 1)
        steps_html.append(
            f'<div class="route-step {cls}">'
            f'<div class="route-dot">{dot_content}</div>'
            f'<div class="route-label">{nombre_corto}</div>'
            f'</div>'
        )
    steps_html.append("</div>")
    st.markdown("".join(steps_html), unsafe_allow_html=True)


def descargar_dataframe_csv(df: pd.DataFrame, filename: str, label: str = "Descargar CSV"):
    """Genera un botón para descargar un dataframe en formato CSV."""
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        icon=":material/download:",
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# Navegación lateral izquierda con botones e iconos Material
# -----------------------------------------------------------------------------
SECCIONES = [
    (":material/home:", "Inicio", "Inicio y Teoría Visual"),
    (":material/radar:", "Estabilidad", "Estabilidad · Plano z y Métodos"),
    (":material/tune:", "Sandbox N×N", "Sandbox Libre N×N (Laboratorio)"),
    (":material/table_view:", "Inspector LU", "Inspector LU y Descomposición"),
    (":material/bolt:", "Casos Físicos", "Casos de Estudio Físicos"),
    (":material/speed:", "Benchmark", "Benchmark y Convergencia O(h)"),
    (":material/photo_library:", "Galería e Informe", "Galería e Informe PDF"),
]

if "vista_idx" not in st.session_state:
    st.session_state.vista_idx = 0

with st.sidebar:
    st.markdown(
        """
        <div class="euler-brand">
            <div class="euler-brand-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>
            </div>
            <span>EulerLab</span>
        </div>
        <div class="euler-sub">EDOs Rígidas · Métodos II</div>
        """,
        unsafe_allow_html=True,
    )

    for idx, (icono_mat, _, label_menu) in enumerate(SECCIONES):
        es_activo = st.session_state.vista_idx == idx
        if st.button(
            label_menu,
            icon=icono_mat,
            key=f"nav_btn_{idx}",
            type="primary" if es_activo else "secondary",
            use_container_width=True,
        ):
            st.session_state.vista_idx = idx
            st.rerun()

    st.markdown(
        """
        <div class="euler-foot">
            <b>UMSA · Informática</b><br>
            Métodos Numéricos II<br>
            <i>Exposiciones II · Grupo 3</i><br>
            <span style="color:#f4b942;font-size:0.7rem;">Euler Implícito & Factorización LU</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

vista_idx = st.session_state.vista_idx
render_route_stepper(vista_idx, [(s[0], s[1]) for s in SECCIONES])


# =============================================================================
# VISTA 0: Inicio, Fundamento Visual y Derivación Manim
# =============================================================================
if vista_idx == 0:
    st.markdown(
        """
        <h1>Euler implícito para sistemas rígidos</h1>
        <p class="q-subtitle">
            Comprende visualmente qué es un sistema de ecuaciones diferenciales rígido (stiff), por qué los métodos
            explícitos tradicionales colapsan y cómo Euler Implícito logra estabilidad incondicional mediante factorización LU.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Animación estilo Manim en 6 etapas
    components.html(html_manim_inicio(), height=560, scrolling=False)

    # Secciones educativas enriquecidas
    st.markdown(
        r"""
        <div class="stage-card">
            <h2 style="margin-top:0;">¿Qué resuelve este proyecto y por qué es fundamental?</h2>
            <p class="q-subtitle" style="margin-bottom:0.8rem;">
                En ingeniería electrónica, cinéticas químicas, dinámica estructural y simulación física, los fenómenos acoplados
                se modelan mediante sistemas lineales: $\mathbf{y}'(t) = A\mathbf{y}(t) + \mathbf{g}(t)$.
                El desafío insalvable para los métodos clásicos aparece cuando el sistema es <b>rígido (stiff)</b>.
            </p>
            <div class="info-grid">
                <div class="info-card">
                    <span class="badge-pill badge-amber">Escalas Disparadas</span>
                    <h4>¿Qué es la Rigidez (Stiffness)?</h4>
                    <p>
                        Coexisten modos dinámicos <b>ultrarrápidos</b> (que decaen en microsegundos) con modos <b>lentos</b>
                        (que evolucionan en segundos u horas). La razón de rigidez se define como:
                        $$S = \frac{\max_i |\text{Re}(\lambda_i)|}{\min_i |\text{Re}(\lambda_i)|} \gg 1$$
                    </p>
                </div>
                <div class="info-card">
                    <span class="badge-pill badge-coral">El Cuello de Botella</span>
                    <h4>¿Por qué falla Euler Explícito?</h4>
                    <p>
                        Aunque la solución física esté casi quieta y suave, el método explícito queda esclavizado por el modo más rápido:
                        si $h > 2 / |\lambda_{\max}|$, cada paso amplifica el error y la simulación explota hacia $\pm \infty$.
                    </p>
                </div>
                <div class="info-card">
                    <span class="badge-pill badge-emerald">Freno Automático</span>
                    <h4>El Poder de Mirar al Futuro</h4>
                    <p>
                        Euler Implícito evalúa la derivada en el instante futuro $t_{k+1}$. Esto genera el sistema lineal
                        $(I - hA)\mathbf{y}_{k+1} = \mathbf{y}_k + h\mathbf{g}(t_{k+1})$, cuya función de estabilidad es
                        $R(z) = 1/(1-z)$. Es <b>A-estable</b> y <b>L-estable</b> en todo el semiplano izquierdo.
                    </p>
                </div>
                <div class="info-card">
                    <span class="badge-pill badge-cyan">Eficiencia Computacional</span>
                    <h4>Precomputación LU O(n²)</h4>
                    <p>
                        Cuando $A$ y $h$ son constantes, la matriz $M = (I - hA)$ nunca se reinvierte paso a paso. Se factoriza
                        como $PM = LU$ una sola vez al inicio ($O(n^3)$), y cada paso de integración se resuelve en $O(n^2)$
                        mediante sustitución hacia adelante y hacia atrás.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabla comparativa
    st.markdown(
        r"""
        <div class="stage-card">
            <h3 style="margin-top:0;">Matriz Comparativa de Esquemas Numéricos</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin-top:10px;">
                <div style="background:#091512;border:1px solid #26413a;border-radius:14px;padding:16px;">
                    <span class="badge-pill badge-coral">Euler Explícito</span>
                    <ul style="margin:10px 0 0;padding-left:18px;color:#a3a58f;font-size:0.88rem;line-height:1.7;">
                        <li>Orden local $O(h^2)$, global $O(h)$.</li>
                        <li><b>Región:</b> disco $|1+z| \le 1$.</li>
                        <li>Paso limitado por estabilidad: $h \le 2/|\lambda_{\max}|$.</li>
                        <li>En sistemas rígidos requiere millones de pasos o diverge.</li>
                    </ul>
                </div>
                <div style="background:#091512;border:1px solid #a78bfa;border-radius:14px;padding:16px;">
                    <span class="badge-pill" style="background:rgba(167,139,250,0.18);color:#a78bfa;border:1px solid rgba(167,139,250,0.4);">Crank-Nicolson (Trapecio)</span>
                    <ul style="margin:10px 0 0;padding-left:18px;color:#cbd5e1;font-size:0.88rem;line-height:1.7;">
                        <li>Orden local $O(h^3)$, global $O(h^2)$.</li>
                        <li><b>A-estable:</b> $|R(z)| \le 1$ en $\text{Re}(z) \le 0$.</li>
                        <li><b>NO L-estable:</b> $|R(-\infty)| = 1$.</li>
                        <li>Genera oscilaciones espurias persistentes con pasos grandes.</li>
                    </ul>
                </div>
                <div style="background:#091512;border:1px solid #3ecf9f;border-radius:14px;padding:16px;">
                    <span class="badge-pill badge-stable">Euler Implícito (LU)</span>
                    <ul style="margin:10px 0 0;padding-left:18px;color:#f1ead8;font-size:0.88rem;line-height:1.7;">
                        <li>Orden global $O(h)$, precomputación $LU$.</li>
                        <li><b>A-estable y L-estable:</b> $|R(-\infty)| = 0$.</li>
                        <li>Amortigua modos rápidos al instante sin oscilar.</li>
                        <li>Permite pasos <b>20× a 100× más grandes</b>, ahorrando hasta 95% de cómputo.</li>
                    </ul>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# VISTA 1: Estabilidad, Plano z y Comparación de Métodos
# =============================================================================
elif vista_idx == 1:
    st.markdown(
        r"""
        <h1>Plano de estabilidad y comparación de esquemas</h1>
        <p class="q-subtitle">
            Explora interactivamente cómo $z = h\lambda$ entra o sale de las regiones de estabilidad de Euler Explícito,
            Crank-Nicolson y Euler Implícito, y comprueba por qué la L-estabilidad es vital.
        </p>
        """,
        unsafe_allow_html=True,
    )

    col_ctrl, col_plot = st.columns([1, 2.2])

    with col_ctrl:
        with st.container(border=True):
            sistema_preset = st.selectbox(
                "Sistema Lineal:",
                [
                    "Circuito RLC Rígido (2×2, S = 1000)",
                    "Cinética Química (3×3, S = 200)",
                    "Edificio Sísmico (4×4, Modos Complejos)",
                    "Oscilador Amortiguado Rígido (2×2, S = 400)",
                    "Matriz 2×2 Personalizada",
                ],
            )

            if sistema_preset == "Circuito RLC Rígido (2×2, S = 1000)":
                A_mat = np.array([[0.0, -1000.0], [1.0, -1001.0]])
                h_def, h_min, h_max, h_step = 0.0025, 0.0005, 0.02, 0.0005
            elif sistema_preset == "Cinética Química (3×3, S = 200)":
                A_mat = np.array([[-0.5, 0.0, 0.0], [0.5, -100.0, 0.0], [0.0, 100.0, 0.0]])
                h_def, h_min, h_max, h_step = 0.025, 0.005, 0.08, 0.002
            elif sistema_preset == "Edificio Sísmico (4×4, Modos Complejos)":
                A_mat = np.array([
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                    [-200.0, 80.0, -10.0, 4.0],
                    [80.0, -80.0, 4.0, -4.0],
                ])
                h_def, h_min, h_max, h_step = 0.06, 0.005, 0.14, 0.002
            elif sistema_preset == "Oscilador Amortiguado Rígido (2×2, S = 400)":
                A_mat = np.array([[0.0, 1.0], [-400.0, -401.0]])
                h_def, h_min, h_max, h_step = 0.01, 0.001, 0.05, 0.001
            else:
                c1, c2 = st.columns(2)
                with c1:
                    a11 = st.number_input("a11", value=-50.0)
                    a21 = st.number_input("a21", value=0.0)
                with c2:
                    a12 = st.number_input("a12", value=0.0)
                    a22 = st.number_input("a22", value=-2.0)
                A_mat = np.array([[a11, a12], [a21, a22]])
                h_def, h_min, h_max, h_step = 0.05, 0.002, 0.2, 0.004

            h_val = st.slider(
                "Paso temporal h [s]:",
                min_value=float(h_min),
                max_value=float(h_max),
                value=float(h_def),
                step=float(h_step),
                format="%.4f",
            )

            info_est = analizar_estabilidad(A_mat, h_val)
            st.markdown("**Valores propios $\\lambda_i$:**")
            for ev in info_est["eigenvalores"]:
                st.markdown(f"• `{ev.real:+.2f} {ev.imag:+.2f}j`")
            st.markdown(f"**Límite Explícito:** `{info_est['h_critico_explicito']:.4f} s`")

    with col_plot:
        flag_expl = "INESTABLE" if not info_est["estable_explicito"] else "ESTABLE"
        bar_expl = "coral" if not info_est["estable_explicito"] else "emerald"
        render_kpis([
            {"label": "Paso Temporal h", "val": f"{h_val:.4f} s", "sub": f"h_crit = {info_est['h_critico_explicito']:.4f} s", "bar": "amber"},
            {"label": "Rigidez (S)", "val": f"{info_est['razon_rigidez']:.1f}", "sub": info_est["clasificacion_rigidez"], "bar": "cyan"},
            {"label": "|R(z)| Implícito", "val": f"{info_est['radio_espectral_implicito']:.3f}", "sub": "Siempre ≤ 1.0 (L-Estable)", "bar": "emerald"},
            {"label": "|R(z)| Explícito", "val": f"{info_est['radio_espectral_explicito']:.3f}", "sub": f"Estado: {flag_expl}", "bar": bar_expl},
        ])

        tab_z, tab_race, tab_cn = st.tabs([
            ":material/radar: Plano Complejo z = h·λ",
            ":material/flag: La Carrera (y' = λy)",
            ":material/compare: Crank-Nicolson vs Implícito (L-Estabilidad)",
        ])

        with tab_z:
            theta = np.linspace(0, 2 * np.pi, 200)
            fig_z = go.Figure()
            # Semiplano izquierdo estable para Euler Implícito
            fig_z.add_shape(type="rect", x0=-50, y0=-50, x1=0, y1=50, fillcolor="rgba(62, 207, 159, 0.08)", line=dict(width=0), layer="below")
            # Región estable de Euler Explícito |1+z| <= 1
            fig_z.add_trace(go.Scatter(x=-1.0 + np.cos(theta), y=np.sin(theta), fill="toself", fillcolor="rgba(244, 185, 66, 0.22)", line=dict(color=AMBER, width=2.4), name="Estable Explícito |1+z| ≤ 1", hoverinfo="skip"))
            # Disco excluido de Euler Implícito |1-z| < 1
            fig_z.add_trace(go.Scatter(x=1.0 + np.cos(theta), y=np.sin(theta), line=dict(color=CORAL, width=1.6, dash="dot"), name="Excluido Implícito |1-z| < 1", hoverinfo="skip"))
            fig_z.add_hline(y=0, line=dict(color=BORDER_COLOR, width=1.2))
            fig_z.add_vline(x=0, line=dict(color=BORDER_COLOR, width=1.2))

            z_pts = info_est["z_puntos"]
            re_z = [zi.real for zi in z_pts]
            im_z = [zi.imag for zi in z_pts]
            colores_pt = [EMERALD if abs(1.0 + zi) <= 1.0 + 1e-6 else CORAL for zi in z_pts]
            hover_txt = [
                f"z = {zi.real:.3f}{zi.imag:+.3f}j<br>|R_impl| = {ri:.3f}<br>|R_expl| = {re:.3f}"
                for zi, ri, re in zip(z_pts, info_est["amplificacion_implicito"], info_est["amplificacion_explicito"])
            ]
            fig_z.add_trace(go.Scatter(
                x=re_z, y=im_z, mode="markers+text",
                marker=dict(size=14, color=colores_pt, line=dict(color=TEXT_CRISP, width=2)),
                text=[f"z{i+1}" for i in range(len(z_pts))],
                textposition="top right", name="Puntos z = h·λᵢ", hoverinfo="text", hovertext=hover_txt
            ))
            min_x = min(-2.8, min(re_z) * 1.25)
            max_y = max(2.2, max(np.abs(im_z)) * 1.3)
            fig_z.update_xaxes(title_text="Re(z) = h·Re(λ)", range=[min_x, 2.3])
            fig_z.update_yaxes(title_text="Im(z) = h·Im(λ)", range=[-max_y, max_y])
            aplicar_estilo_plotly(fig_z, titulo="Regiones de Estabilidad en el Plano Complejo", height=440)
            st.plotly_chart(fig_z, use_container_width=True)

        with tab_race:
            z_race = st.slider("Paso adimensional z = h·|λ| en la carrera:", min_value=0.2, max_value=4.0, value=2.4, step=0.1)
            A_r = np.array([[-1.0]])
            y0_r = np.array([1.0])
            t_r_imp, y_r_imp = euler_implicito_lineal(A_r, y0_r, (0.0, 8.0), z_race)
            t_r_exp, y_r_exp = euler_explicito_lineal(A_r, y0_r, (0.0, 8.0), z_race, limite_divergencia=20.0)
            t_r_ex = np.linspace(0.0, 8.0, 200)
            y_r_ex = np.exp(-t_r_ex)

            fig_r = go.Figure()
            fig_r.add_trace(go.Scatter(x=t_r_ex, y=y_r_ex, line=dict(color=TEXT_CRISP, width=2.5), name="Exacta e^(-t)"))
            fig_r.add_trace(go.Scatter(x=t_r_imp, y=y_r_imp[:, 0], mode="lines+markers", line=dict(color=EMERALD, width=2.4), marker=dict(size=7), name="Euler Implícito"))
            mask_re = ~np.isnan(y_r_exp[:, 0])
            fig_r.add_trace(go.Scatter(x=t_r_exp[mask_re], y=y_r_exp[mask_re, 0], mode="lines+markers", line=dict(color=CORAL, width=2.0, dash="dash"), marker=dict(size=7), name="Euler Explícito"))
            fig_r.update_xaxes(title_text="Tiempo adimensional t")
            fig_r.update_yaxes(title_text="y(t)", range=[-3.0, 2.5])
            aplicar_estilo_plotly(fig_r, titulo=f"La Carrera: z = {z_race:.1f} ({'Explícito oscila y crece' if z_race > 2 else 'Ambos estables'})", height=440)
            st.plotly_chart(fig_r, use_container_width=True)

        with tab_cn:
            st.markdown(
                r"""
                <div class="speaker-card" style="margin-top:0;">
                    <h4>¿Por qué Euler Implícito y no Crank-Nicolson?</h4>
                    <p>
                        <b>Crank-Nicolson (Trapecio)</b> tiene orden 2 ($O(h^2)$) y es A-estable. Sin embargo, <b>NO es L-estable</b>:
                        su factor de amplificación satisface $\lim_{z \to -\infty} R(z) = -1$.
                        Ante pasos grandes, no amortigua los transitorios rápidos, sino que los hace <b>oscilar indefinidamente con signo alternante</b>.
                        <b>Euler Implícito</b>, al ser L-estable ($\lim R(z) = 0$), absorbe y apaga los modos rígidos de inmediato.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            z_cn = st.slider("Paso para modo rápido z = h·|λ| (ej. λ = -100):", min_value=1.0, max_value=30.0, value=12.0, step=1.0)
            A_cn = np.array([[-100.0]])
            y0_cn = np.array([1.0])
            h_cn_eval = z_cn / 100.0
            t_span_cn = (0.0, 0.4)

            t_eval_cn, y_eval_cn = crank_nicolson_lineal(A_cn, y0_cn, t_span_cn, h_cn_eval)
            t_eval_imp, y_eval_imp = euler_implicito_lineal(A_cn, y0_cn, t_span_cn, h_cn_eval)
            t_eval_fine = np.linspace(0.0, 0.4, 300)
            y_eval_exact = np.exp(-100.0 * t_eval_fine)

            fig_cn = go.Figure()
            fig_cn.add_trace(go.Scatter(x=t_eval_fine, y=y_eval_exact, line=dict(color=TEXT_CRISP, width=2.5), name="Exacta e^(-100t)"))
            fig_cn.add_trace(go.Scatter(x=t_eval_imp, y=y_eval_imp[:, 0], mode="lines+markers", line=dict(color=EMERALD, width=2.2), marker=dict(size=7), name="Euler Implícito (L-Estable: Amortiguación inmediata)"))
            fig_cn.add_trace(go.Scatter(x=t_eval_cn, y=y_eval_cn[:, 0], mode="lines+markers", line=dict(color=PURPLE, width=2.2, dash="dash"), marker=dict(size=7), name="Crank-Nicolson (Oscilación espuria |R|≈1)"))
            fig_cn.update_xaxes(title_text="Tiempo t [s]")
            fig_cn.update_yaxes(title_text="y(t)")
            aplicar_estilo_plotly(fig_cn, titulo=f"Efecto de la L-Estabilidad con h = {h_cn_eval:.3f} s (z = -{z_cn:.0f})", height=420)
            st.plotly_chart(fig_cn, use_container_width=True)


# =============================================================================
# VISTA 2: Sandbox Libre N×N (Laboratorio Matricial y Biblioteca Clásica)
# =============================================================================
elif vista_idx == 2:
    st.markdown(
        r"""
        <h1>Sandbox Libre N×N (Laboratorio Matricial)</h1>
        <p class="q-subtitle">
            Experimenta con cualquier sistema lineal arbitrario $\mathbf{y}' = A\mathbf{y}$. Modifica coeficientes,
            condiciones iniciales o carga sistemas rígidos históricos de la literatura científica.
        </p>
        """,
        unsafe_allow_html=True,
    )

    col_s1, col_s2 = st.columns([1.1, 2.2])

    with col_s1:
        with st.container(border=True):
            tipo_sistema = st.selectbox(
                "Cargar Sistema o Biblioteca:",
                [
                    "Matriz 2×2 Personalizada",
                    "Matriz 3×3 Personalizada",
                    "Problema de Robertson Linealizado (Extremo, S = 10,000)",
                    "Problema de Prothero-Robinson (Prueba Estándar)",
                    "Oscilador Acoplado Fuertemente Amortiguado (S = 500)",
                    "Circuito RLC Rígido (S = 1000)",
                ],
            )

            if tipo_sistema == "Matriz 2×2 Personalizada":
                n_dim = 2
                c1, c2 = st.columns(2)
                with c1:
                    a11 = st.number_input("A[0,0]", value=-200.0)
                    a21 = st.number_input("A[1,0]", value=1.0)
                    y0_1 = st.number_input("y0[0]", value=1.0)
                with c2:
                    a12 = st.number_input("A[0,1]", value=0.0)
                    a22 = st.number_input("A[1,1]", value=-1.0)
                    y0_2 = st.number_input("y0[1]", value=0.5)
                A_box = np.array([[a11, a12], [a21, a22]])
                y0_box = np.array([y0_1, y0_2])
                t_fin_box = st.slider("Horizonte T [s]:", min_value=0.5, max_value=10.0, value=3.0, step=0.5)
                h_box = st.slider("Paso h [s]:", min_value=0.001, max_value=0.1, value=0.02, step=0.001, format="%.4f")

            elif tipo_sistema == "Matriz 3×3 Personalizada":
                n_dim = 3
                st.markdown("**Matriz A (3×3):**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    a11 = st.number_input("A[0,0]", value=-100.0)
                    a21 = st.number_input("A[1,0]", value=100.0)
                    a31 = st.number_input("A[2,0]", value=0.0)
                with c2:
                    a12 = st.number_input("A[0,1]", value=0.0)
                    a22 = st.number_input("A[1,1]", value=-2.0)
                    a32 = st.number_input("A[2,1]", value=2.0)
                with c3:
                    a13 = st.number_input("A[0,2]", value=0.0)
                    a23 = st.number_input("A[1,2]", value=0.0)
                    a33 = st.number_input("A[2,2]", value=-0.1)
                A_box = np.array([[a11, a12, a13], [a21, a22, a23], [a31, a32, a33]])
                y0_box = np.array([1.0, 0.0, 0.0])
                t_fin_box = st.slider("Horizonte T [s]:", min_value=1.0, max_value=20.0, value=8.0, step=1.0)
                h_box = st.slider("Paso h [s]:", min_value=0.005, max_value=0.2, value=0.05, step=0.005, format="%.3f")

            elif tipo_sistema == "Problema de Robertson Linealizado (Extremo, S = 10,000)":
                # Cinética química de Robertson linealizada en el punto de equilibrio rápido
                A_box = np.array([
                    [-0.04, 1e4, 0.0],
                    [0.04, -1e4, 0.0],
                    [0.0, 0.0, -1.0],
                ])
                y0_box = np.array([1.0, 0.0, 0.0])
                t_fin_box = 5.0
                h_box = st.slider("Paso h [s]:", min_value=0.001, max_value=0.1, value=0.02, step=0.001, format="%.4f")

            elif tipo_sistema == "Problema de Prothero-Robinson (Prueba Estándar)":
                lambda_pr = st.slider("Rigidez lambda:", min_value=-1000.0, max_value=-50.0, value=-500.0, step=50.0)
                A_box = np.array([[lambda_pr, 0.0], [0.0, -1.0]])
                y0_box = np.array([1.0, 1.0])
                t_fin_box = 4.0
                h_box = st.slider("Paso h [s]:", min_value=0.002, max_value=0.1, value=0.025, step=0.002, format="%.4f")

            elif tipo_sistema == "Oscilador Acoplado Fuertemente Amortiguado (S = 500)":
                A_box = np.array([[0.0, 1.0], [-500.0, -501.0]])
                y0_box = np.array([2.0, 0.0])
                t_fin_box = 3.0
                h_box = st.slider("Paso h [s]:", min_value=0.001, max_value=0.08, value=0.02, step=0.001, format="%.4f")

            else:
                A_box = np.array([[0.0, -1000.0], [1.0, -1001.0]])
                y0_box = np.array([10.0, 0.0])
                t_fin_box = 3.0
                h_box = st.slider("Paso h [s]:", min_value=0.001, max_value=0.1, value=0.04, step=0.001, format="%.4f")

            info_sb = analizar_estabilidad(A_box, h_box)
            st.markdown(f"**Valores propios $\\lambda_i$:**")
            for ev in info_sb["eigenvalores"]:
                st.markdown(f"• `{ev.real:+.2e} {ev.imag:+.2e}j`")
            st.markdown(f"**Paso crítico explícito:** `{info_sb['h_critico_explicito']:.4e} s`")

    with col_s2:
        t_sb_imp, y_sb_imp = euler_implicito_lineal(A_box, y0_box, (0.0, t_fin_box), h_box)
        t_sb_fine = np.linspace(0.0, t_fin_box, 500)
        y_sb_exact = solucion_exacta_lineal(A_box, y0_box, t_sb_fine)
        y_sb_exact_nodes = solucion_exacta_lineal(A_box, y0_box, t_sb_imp)
        t_sb_exp, y_sb_exp = euler_explicito_lineal(A_box, y0_box, (0.0, min(t_fin_box, 1.5)), h_box, limite_divergencia=1e4)
        t_sb_cn, y_sb_cn = crank_nicolson_lineal(A_box, y0_box, (0.0, t_fin_box), h_box)

        err_sb_imp = float(np.max(np.abs(y_sb_imp - y_sb_exact_nodes)))
        flag_exp_sb = "DIVERGENTE" if not info_sb["estable_explicito"] else "ESTABLE"

        render_kpis([
            {"label": "Paso Temporal (h)", "val": f"{h_box:.4f} s", "sub": f"{len(t_sb_imp)-1} pasos", "bar": "amber"},
            {"label": "Razón Rigidez (S)", "val": f"{info_sb['razon_rigidez']:.1f}", "sub": info_sb["clasificacion_rigidez"], "bar": "cyan"},
            {"label": "Error ||e||_∞ Implícito", "val": f"{err_sb_imp:.3e}", "sub": "vs Solución Exacta", "bar": "emerald"},
            {"label": "Euler Explícito", "val": flag_exp_sb, "sub": f"h_crit = {info_sb['h_critico_explicito']:.4e} s", "bar": "coral" if flag_exp_sb == "DIVERGENTE" else "emerald"},
        ])

        # Opciones de trazado
        c_t1, c_t2, c_t3, c_t4 = st.columns(4)
        ver_exacta = c_t1.checkbox("Solución Exacta", value=True)
        ver_impl = c_t2.checkbox("Euler Implícito", value=True)
        ver_cn = c_t3.checkbox("Crank-Nicolson", value=True)
        ver_expl = c_t4.checkbox("Euler Explícito", value=True)

        fig_sb = go.Figure()
        n_vars = A_box.shape[0]
        colores_vars = [CYAN, EMERALD, AMBER, PURPLE]

        for i in range(n_vars):
            c_base = colores_vars[i % len(colores_vars)]
            if ver_exacta:
                fig_sb.add_trace(go.Scatter(x=t_sb_fine, y=y_sb_exact[:, i], line=dict(color=c_base, width=2.2), name=f"y{i+1} Exacta"))
            if ver_impl:
                fig_sb.add_trace(go.Scatter(x=t_sb_imp, y=y_sb_imp[:, i], mode="lines+markers", line=dict(color=c_base, width=1.8, dash="dot"), marker=dict(size=4), name=f"y{i+1} Implícito"))
            if ver_cn:
                fig_sb.add_trace(go.Scatter(x=t_sb_cn, y=y_sb_cn[:, i], mode="lines", line=dict(color=PURPLE, width=1.4, dash="dash"), name=f"y{i+1} Crank-Nicolson"))
            if ver_expl:
                mask_e = (~np.isnan(y_sb_exp[:, i])) & (np.abs(y_sb_exp[:, i]) < 50.0)
                if np.any(mask_e):
                    fig_sb.add_trace(go.Scatter(x=t_sb_exp[mask_e], y=y_sb_exp[mask_e, i], mode="lines", line=dict(color=CORAL, width=1.5, dash="longdash"), name=f"y{i+1} Explícito"))

        fig_sb.update_xaxes(title_text="Tiempo t [s]")
        fig_sb.update_yaxes(title_text="Variables de estado y_i(t)")
        aplicar_estilo_plotly(fig_sb, titulo="Simulación en el Sandbox Libre", height=420)
        st.plotly_chart(fig_sb, use_container_width=True)

        # Exportación CSV del sandbox
        df_sb = pd.DataFrame({"t": t_sb_imp})
        for i in range(n_vars):
            df_sb[f"y{i+1}_implicito"] = y_sb_imp[:, i]
            df_sb[f"y{i+1}_exacta"] = y_sb_exact_nodes[:, i]
            df_sb[f"y{i+1}_crank_nicolson"] = y_sb_cn[:, i]
        descargar_dataframe_csv(df_sb, "simulacion_sandbox_eulerlab.csv", "Descargar Datos de Simulación (CSV)")


# =============================================================================
# VISTA 3: Inspector LU y Descomposición Modal
# =============================================================================
elif vista_idx == 3:
    st.markdown(
        r"""
        <h1>Inspector LU y Descomposición Modal</h1>
        <p class="q-subtitle">
            Abre la caja negra del álgebra lineal numérica. Inspecciona las matrices $M = I - hA$, sus factores $P, L, U$,
            el número de condición espectral $\kappa(M)$ y la descomposición modal que origina la rigidez.
        </p>
        """,
        unsafe_allow_html=True,
    )

    col_lu_ctrl, col_lu_view = st.columns([1, 2.3])

    with col_lu_ctrl:
        with st.container(border=True):
            sis_lu = st.selectbox(
                "Seleccionar Sistema:",
                [
                    "Circuito RLC (2×2, S = 1000)",
                    "Cinética Química (3×3, S = 200)",
                    "Edificio Sísmico (4×4, Modos Complejos)",
                    "Oscilador Amortiguado (2×2, S = 400)",
                ],
            )
            if sis_lu == "Circuito RLC (2×2, S = 1000)":
                A_lu = np.array([[0.0, -1000.0], [1.0, -1001.0]])
                y0_lu = np.array([10.0, 0.0])
                h_lu = st.slider("Paso h [s]:", min_value=0.001, max_value=0.1, value=0.04, step=0.002, format="%.4f")
                t_max_lu = 2.5
            elif sis_lu == "Cinética Química (3×3, S = 200)":
                A_lu = np.array([[-0.5, 0.0, 0.0], [0.5, -100.0, 0.0], [0.0, 100.0, 0.0]])
                y0_lu = np.array([1.0, 0.0, 0.0])
                h_lu = st.slider("Paso h [s]:", min_value=0.005, max_value=0.2, value=0.05, step=0.005, format="%.3f")
                t_max_lu = 6.0
            elif sis_lu == "Edificio Sísmico (4×4, Modos Complejos)":
                A_lu = np.array([
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                    [-200.0, 80.0, -10.0, 4.0],
                    [80.0, -80.0, 4.0, -4.0],
                ])
                y0_lu = np.array([0.1, 0.0, 0.0, 0.0])
                h_lu = st.slider("Paso h [s]:", min_value=0.01, max_value=0.15, value=0.06, step=0.005, format="%.3f")
                t_max_lu = 8.0
            else:
                A_lu = np.array([[0.0, 1.0], [-400.0, -401.0]])
                y0_lu = np.array([2.0, 0.0])
                h_lu = st.slider("Paso h [s]:", min_value=0.002, max_value=0.08, value=0.02, step=0.002, format="%.4f")
                t_max_lu = 2.0

            info_lu = descomposicion_lu_inspector(A_lu, h_lu)
            st.markdown(f"**Determinante $\\det(M)$:** `{info_lu['det']:.3e}`")
            st.markdown(f"**Número de condición $\\kappa_2(M)$:** `{info_lu['cond']:.2f}`")
            st.markdown(f"**Estado:** `{info_lu['estado_condicion']}`")

    with col_lu_view:
        tab_mat, tab_modal = st.tabs([
            ":material/table_view: Factorización M = P·L·U",
            ":material/timeline: Descomposición Modal (Rápido vs Lento)",
        ])

        with tab_mat:
            st.markdown(
                r"""
                <div class="speaker-card" style="margin-top:0;">
                    <h4>Optimización Algorítmica con Factorización LU</h4>
                    <p>
                        Para dar $N$ pasos con matriz e intervalo constantes, invertir $(I - hA)$ explícitamente en cada paso
                        costaría $O(N \cdot n^3)$. Con <code>scipy.linalg.lu_factor</code> se precomputa $PM = LU$ una sola vez
                        con costo inicial $O(n^3)$, y luego cada paso temporal se resuelve mediante dos sustituciones triangulares
                        con costo $O(n^2)$.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_m1, c_m2 = st.columns(2)
            with c_m1:
                st.markdown("<div class='matrix-title'>Matriz del Sistema M = (I − hA)</div>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(np.round(info_lu["M"], 4)), use_container_width=True)

                st.markdown("<div class='matrix-title'>Matriz Triangular Inferior L</div>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(np.round(info_lu["L"], 4)), use_container_width=True)

            with c_m2:
                st.markdown("<div class='matrix-title'>Matriz de Permutación P</div>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(np.round(info_lu["P"], 4)), use_container_width=True)

                st.markdown("<div class='matrix-title'>Matriz Triangular Superior U</div>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(np.round(info_lu["U"], 4)), use_container_width=True)

        with tab_modal:
            t_modal_vec = np.linspace(0.0, t_max_lu, 400)
            modal_data = descomposicion_modal_lineal(A_lu, y0_lu, t_modal_vec)

            fig_mod = go.Figure()
            n_modos = A_lu.shape[0]
            colores_mod = [CORAL, CYAN, AMBER, EMERALD]

            for j in range(n_modos):
                ev = modal_data["eigenvalores"][j]
                tau = modal_data["escalas_tiempo"][j]
                tau_str = f"τ = {tau:.4e} s" if np.isfinite(tau) else "τ = ∞"
                es_rapido = (j == modal_data["idx_rapido"])
                label_modo = f"Modo {j+1} (λ = {ev.real:.1f}{ev.imag:+.1f}j, {tau_str}) {'[RÁPIDO]' if es_rapido else ''}"

                fig_mod.add_trace(go.Scatter(
                    x=t_modal_vec,
                    y=modal_data["modos_magnitud"][:, j],
                    line=dict(
                        color=colores_mod[j % len(colores_mod)],
                        width=3.0 if es_rapido else 2.0,
                        dash="dash" if es_rapido else "solid",
                    ),
                    name=label_modo,
                ))

            fig_mod.update_xaxes(title_text="Tiempo t [s]")
            fig_mod.update_yaxes(title_text="Magnitud del modo ||c_j·e^(λ_j·t)·v_j||")
            aplicar_estilo_plotly(fig_mod, titulo="Descomposición Modal: El Transitorio Rápido se Extingue al Inicio", height=420)
            st.plotly_chart(fig_mod, use_container_width=True)

            st.info(
                f"Modo ultrarrápido dominante: λ = {modal_data['eigenvalores'][modal_data['idx_rapido']].real:.1f}. "
                f"Su constante de tiempo es τ = {modal_data['escalas_tiempo'][modal_data['idx_rapido']]:.4e} s. "
                "Euler Implícito permite tomar pasos h decenas de veces mayores que τ sin perder estabilidad."
            )


# =============================================================================
# VISTA 4: Casos de Estudio Físicos (RLC, Química, Sismo)
# =============================================================================
elif vista_idx == 4:
    st.markdown(
        """
        <h1>Casos de Estudio Físicos</h1>
        <p class="q-subtitle">
            Simulaciones científicas interactivas con esquemas animados estilo Canvas a 60 fps y retratos de fase.
        </p>
        """,
        unsafe_allow_html=True,
    )

    tab_rlc, tab_chem, tab_bldg = st.tabs([
        ":material/bolt: Caso 1: Circuito RLC (2×2)",
        ":material/science: Caso 2: Cinética Química (3×3)",
        ":material/apartment: Caso 3: Edificio Sísmico (4×4)",
    ])

    # -------------------------------------------------------------------------
    # SUB-CASO 1: RLC
    # -------------------------------------------------------------------------
    with tab_rlc:
        with st.expander("Parámetros del Circuito RLC", icon=":material/tune:", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                R_val = st.number_input("Resistencia R [Ω]:", value=1001.0, step=50.0)
            with c2:
                L_val = st.number_input("Inductancia L [H]:", value=1.0, step=0.1)
            with c3:
                C_val = st.number_input("Capacitancia C [F]:", value=1e-3, format="%.4e")
            with c4:
                t_fin = st.slider("Tiempo T [s]:", min_value=0.5, max_value=6.0, value=3.0, step=0.5, key="t_rlc")
            h_ej1 = st.slider("Paso temporal h [s]:", min_value=0.001, max_value=0.15, value=0.05, step=0.001, format="%.4f", key="h_rlc")

        A_rlc = np.array([[0.0, -1.0 / C_val], [1.0 / L_val, -R_val / L_val]])
        y0_rlc = np.array([10.0, 0.0])

        t_imp, y_imp = euler_implicito_lineal(A_rlc, y0_rlc, (0.0, t_fin), h_ej1)
        y_ex_imp = solucion_exacta_lineal(A_rlc, y0_rlc, t_imp)
        t_fine = np.linspace(0.0, t_fin, 600)
        y_ex_fine = solucion_exacta_lineal(A_rlc, y0_rlc, t_fine)
        t_exp, y_exp = euler_explicito_lineal(A_rlc, y0_rlc, (0.0, min(t_fin, 0.3)), h_ej1)

        info_rlc = analizar_estabilidad(A_rlc, h_ej1)
        err_inf_rlc = float(np.max(np.abs(y_imp - y_ex_imp)))
        flag_expl = "DIVERGENTE" if not info_rlc["estable_explicito"] else "ESTABLE"

        render_kpis([
            {"label": "Paso Temporal (h)", "val": f"{h_ej1:.4f} s", "sub": f"{len(t_imp)-1} pasos", "bar": "amber"},
            {"label": "Rigidez (S)", "val": f"{info_rlc['razon_rigidez']:.1f}", "sub": info_rlc["clasificacion_rigidez"], "bar": "cyan"},
            {"label": "Error Global L_∞", "val": f"{err_inf_rlc:.3e}", "sub": "Euler Implícito vs Exacta", "bar": "emerald"},
            {"label": "Euler Explícito", "val": flag_expl, "sub": f"Límite h = {info_rlc['h_critico_explicito']:.4f} s", "bar": "coral" if flag_expl == "DIVERGENTE" else "emerald"},
        ])

        t1, t2, t3, t4 = st.tabs([
            ":material/play_circle: Animación Interactiva 60fps",
            ":material/show_chart: Voltaje y Corriente",
            ":material/autorenew: Retrato de Fase",
            ":material/stacked_line_chart: Convergencia O(h)",
        ])

        with t1:
            components.html(html_animacion_rlc(t_imp, y_imp, t_fine, y_ex_fine, t_exp, y_exp), height=445, scrolling=False)

        with t2:
            fig = make_subplots(rows=1, cols=2, subplot_titles=("Voltaje V_C(t) [V]", "Corriente I(t) [A]"))
            fig.add_trace(go.Scatter(x=t_fine, y=y_ex_fine[:, 0], line=dict(color=TEXT_CRISP, width=2.2), name="Exacta"), row=1, col=1)
            fig.add_trace(go.Scatter(x=t_fine, y=y_ex_fine[:, 1], line=dict(color=TEXT_CRISP, width=2.2), showlegend=False), row=1, col=2)
            fig.add_trace(go.Scatter(x=t_imp, y=y_imp[:, 0], mode="lines+markers", line=dict(color=EMERALD, width=2.0), marker=dict(size=4), name="Euler Implícito"), row=1, col=1)
            fig.add_trace(go.Scatter(x=t_imp, y=y_imp[:, 1], mode="lines+markers", line=dict(color=EMERALD, width=2.0), marker=dict(size=4), showlegend=False), row=1, col=2)
            mask_exp = ~np.isnan(y_exp[:, 0])
            fig.add_trace(go.Scatter(x=t_exp[mask_exp], y=y_exp[mask_exp, 0], line=dict(color=CORAL, width=1.6, dash="dash"), name="Euler Explícito"), row=1, col=1)
            aplicar_estilo_plotly(fig, titulo="Simulación Temporal del Circuito RLC", height=430)
            st.plotly_chart(fig, use_container_width=True)

        with t3:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=y_ex_fine[:, 0], y=y_ex_fine[:, 1], line=dict(color=TEXT_CRISP, width=2.2), name="Exacta"))
            fig_p.add_trace(go.Scatter(x=y_imp[:, 0], y=y_imp[:, 1], mode="lines+markers", line=dict(color=EMERALD, width=2.0), marker=dict(size=5), name="Euler Implícito"))
            fig_p.update_xaxes(title_text="V_C [V]")
            fig_p.update_yaxes(title_text="I [A]")
            aplicar_estilo_plotly(fig_p, titulo="Retrato de Fase (V_C vs I)", height=430)
            st.plotly_chart(fig_p, use_container_width=True)

        with t4:
            conv = estudio_convergencia(A_rlc, y0_rlc, (0.0, t_fin), [0.2, 0.1, 0.05, 0.025, 0.0125])
            fig_c = go.Figure()
            fig_c.add_trace(go.Scatter(x=conv["hs"], y=conv["errores_inf"], mode="lines+markers", line=dict(color=EMERALD, width=2.4), marker=dict(size=7), name="Error ||e||_∞"))
            fig_c.add_trace(go.Scatter(x=conv["hs"], y=conv["errores_inf"][-1] * (conv["hs"] / conv["hs"][-1]), line=dict(color=AMBER, width=1.8, dash="dash"), name="Pendiente teórica O(h)"))
            fig_c.update_xaxes(type="log", title_text="Paso h [s]")
            fig_c.update_yaxes(type="log", title_text="Error ||e||_∞")
            aplicar_estilo_plotly(fig_c, titulo="Convergencia Log-Log de Primer Orden O(h)", height=420)
            st.plotly_chart(fig_c, use_container_width=True)

        # Descarga de datos RLC
        df_rlc = pd.DataFrame({"t": t_imp, "Vc_implicito": y_imp[:, 0], "I_implicito": y_imp[:, 1], "Vc_exacta": y_ex_imp[:, 0], "I_exacta": y_ex_imp[:, 1]})
        descargar_dataframe_csv(df_rlc, "circuito_rlc_eulerlab.csv", "Descargar Datos Circuito RLC (CSV)")

    # -------------------------------------------------------------------------
    # SUB-CASO 2: Cinética Química
    # -------------------------------------------------------------------------
    with tab_chem:
        with st.expander("Controles Cinéticos", icon=":material/tune:", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                k1_val = st.number_input("Constante lenta k1 [s⁻¹]:", value=0.5, step=0.1)
            with c2:
                k2_val = st.number_input("Constante rápida k2 [s⁻¹]:", value=100.0, step=10.0)
            with c3:
                h_chem = st.slider("Paso temporal h [s]:", min_value=0.005, max_value=0.2, value=0.05, step=0.005, format="%.3f", key="h_chem")

        A_chem = np.array([[-k1_val, 0.0, 0.0], [k1_val, -k2_val, 0.0], [0.0, k2_val, 0.0]])
        y0_chem = np.array([1.0, 0.0, 0.0])
        t_ch_imp, y_ch_imp = euler_implicito_lineal(A_chem, y0_chem, (0.0, 8.0), h_chem)
        t_fine_ch = np.linspace(0.0, 8.0, 600)

        def sol_chem(t_arr):
            a = np.exp(-k1_val * t_arr)
            b = (k1_val / (k2_val - k1_val)) * (np.exp(-k1_val * t_arr) - np.exp(-k2_val * t_arr))
            return np.column_stack([a, b, 1.0 - a - b])

        y_ch_fine = sol_chem(t_fine_ch)
        t_ch_exp, y_ch_exp = euler_explicito_lineal(A_chem, y0_chem, (0.0, 1.0), h_chem, limite_divergencia=1e4)

        masa_total = np.sum(y_ch_imp, axis=1)
        err_masa = float(np.max(np.abs(masa_total - 1.0)))
        min_b = float(np.min(y_ch_imp[:, 1]))
        info_chem = analizar_estabilidad(A_chem, h_chem)
        flag_ch = "DIVERGENTE" if not info_chem["estable_explicito"] else "ESTABLE"

        render_kpis([
            {"label": "Paso Temporal (h)", "val": f"{h_chem:.3f} s", "sub": f"Límite expl. = {2.0/k2_val:.3f} s", "bar": "amber"},
            {"label": "Rigidez (S)", "val": f"{k2_val/k1_val:.1f}", "sub": "k2 / k1", "bar": "cyan"},
            {"label": "Error Masa", "val": f"{err_masa:.2e}", "sub": "max |A+B+C - 1|", "bar": "emerald"},
            {"label": "Euler Explícito", "val": flag_ch, "sub": f"Min [B] Impl. = {min_b:.1e}", "bar": "coral" if flag_ch == "DIVERGENTE" else "emerald"},
        ])

        t1, t2, t3 = st.tabs([
            ":material/play_circle: Reactor en Vivo 60fps",
            ":material/show_chart: Especies y Masa",
            ":material/biotech: Capa Límite B(t)",
        ])

        with t1:
            components.html(html_animacion_cinetica(t_ch_imp, y_ch_imp), height=435, scrolling=False)

        with t2:
            fig_ch = make_subplots(rows=1, cols=2, subplot_titles=("Concentraciones [A] y [C]", "Conservación de Masa A+B+C"))
            fig_ch.add_trace(go.Scatter(x=t_fine_ch, y=y_ch_fine[:, 0], line=dict(color=CYAN, width=2.2), name="[A] Exacta"), row=1, col=1)
            fig_ch.add_trace(go.Scatter(x=t_ch_imp[::3], y=y_ch_imp[::3, 0], mode="markers", marker=dict(color=CYAN, size=5), name="[A] Implícito"), row=1, col=1)
            fig_ch.add_trace(go.Scatter(x=t_fine_ch, y=y_ch_fine[:, 2], line=dict(color=EMERALD, width=2.2), name="[C] Exacta"), row=1, col=1)
            fig_ch.add_trace(go.Scatter(x=t_ch_imp[::3], y=y_ch_imp[::3, 2], mode="markers", marker=dict(color=EMERALD, size=5), name="[C] Implícito"), row=1, col=1)
            fig_ch.add_trace(go.Scatter(x=t_ch_imp, y=masa_total, line=dict(color=AMBER, width=2.4), name="Masa A+B+C"), row=1, col=2)
            aplicar_estilo_plotly(fig_ch, titulo="Evolución Química y Conservación de Masa", height=430)
            st.plotly_chart(fig_ch, use_container_width=True)

        with t3:
            fig_z = go.Figure()
            tz = t_fine_ch[t_fine_ch <= 1.2]
            fig_z.add_trace(go.Scatter(x=tz, y=sol_chem(tz)[:, 1] * 1e3, line=dict(color=TEXT_CRISP, width=2.2), name="[B] Exacta"))
            fig_z.add_trace(go.Scatter(x=t_ch_imp[t_ch_imp <= 1.2], y=y_ch_imp[t_ch_imp <= 1.2, 1] * 1e3, mode="lines+markers", line=dict(color=EMERALD, width=2.0), name="[B] Implícito (Positivo)"))
            me = (t_ch_exp <= 0.6) & (~np.isnan(y_ch_exp[:, 1]))
            fig_z.add_trace(go.Scatter(x=t_ch_exp[me], y=y_ch_exp[me, 1] * 1e3, mode="lines+markers", line=dict(color=CORAL, width=1.6, dash="dash"), name="[B] Explícito (Negativo no físico)"))
            fig_z.update_xaxes(title_text="Tiempo t [s]")
            fig_z.update_yaxes(title_text="[B](t) [mmol/L]")
            aplicar_estilo_plotly(fig_z, titulo="Positividad de Euler Implícito vs Oscilación Explícita", height=430)
            st.plotly_chart(fig_z, use_container_width=True)

        # Descarga de datos cinética
        df_chem = pd.DataFrame({"t": t_ch_imp, "A": y_ch_imp[:, 0], "B": y_ch_imp[:, 1], "C": y_ch_imp[:, 2], "Masa_Total": masa_total})
        descargar_dataframe_csv(df_chem, "cinetica_quimica_eulerlab.csv", "Descargar Datos Cinética Química (CSV)")

    # -------------------------------------------------------------------------
    # SUB-CASO 3: Edificio Sísmico
    # -------------------------------------------------------------------------
    with tab_bldg:
        with st.expander("Parámetros Estructurales", icon=":material/tune:", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                k1_ed = st.number_input("Rigidez k1 [N/m]:", value=120.0, step=10.0)
                k2_ed = st.number_input("Rigidez k2 [N/m]:", value=80.0, step=10.0)
            with c2:
                c1_ed = st.number_input("Amortiguamiento c1:", value=6.0, step=1.0)
                c2_ed = st.number_input("Amortiguamiento c2:", value=4.0, step=1.0)
            with c3:
                h_bldg = st.slider("Paso temporal h [s]:", min_value=0.01, max_value=0.12, value=0.06, step=0.005, format="%.3f", key="h_bldg")
                t_fin_b = st.slider("Horizonte T [s]:", min_value=4.0, max_value=12.0, value=8.0, step=1.0, key="t_bldg")

        A_b = np.array([
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [-(k1_ed + k2_ed), k2_ed, -(c1_ed + c2_ed), c2_ed],
            [k2_ed, -k2_ed, c2_ed, -c2_ed],
        ])

        def g_sismo(ti: float) -> np.ndarray:
            ag = 12.0 * np.exp(-0.4 * ti) * np.sin(4.5 * ti)
            return np.array([0.0, 0.0, -ag, -ag])

        y0_b = np.zeros(4)
        t_b_imp, y_b_imp = euler_implicito_lineal(A_b, y0_b, (0.0, t_fin_b), h_bldg, g=g_sismo)
        y_b_ref = solucion_exacta_lineal(A_b, y0_b, t_b_imp, g=g_sismo)
        t_b_exp, y_b_exp = euler_explicito_lineal(A_b, y0_b, (0.0, t_fin_b), h_bldg, g=g_sismo, limite_divergencia=1e4)

        def calc_e(ym):
            return 0.5 * (ym[:, 2]**2 + ym[:, 3]**2) + 0.5 * (k1_ed * ym[:, 0]**2 + k2_ed * (ym[:, 1] - ym[:, 0])**2)

        e_imp, e_ref, e_exp = calc_e(y_b_imp), calc_e(y_b_ref), calc_e(y_b_exp)
        err_x2 = float(np.max(np.abs(y_b_imp[:, 1] - y_b_ref[:, 1])))
        max_exp = float(np.nanmax(np.abs(y_b_exp[:, 1])))
        info_b = analizar_estabilidad(A_b, h_bldg)
        flag_b = "DIVERGENTE" if not info_b["estable_explicito"] else "ESTABLE"

        render_kpis([
            {"label": "Paso Temporal (h)", "val": f"{h_bldg:.3f} s", "sub": f"{len(t_b_imp)-1} pasos", "bar": "amber"},
            {"label": "Error Máx. Piso 2", "val": f"{err_x2:.3e} m", "sub": "vs Referencia Radau", "bar": "emerald"},
            {"label": "Euler Explícito", "val": flag_b, "sub": f"Pico x2 = {max_exp:.2f} m", "bar": "coral" if flag_b == "DIVERGENTE" else "emerald"},
            {"label": "Energía Máx. Impl.", "val": f"{np.max(e_imp):.2f} J", "sub": f"Ref = {np.max(e_ref):.2f} J", "bar": "cyan"},
        ])

        t1, t2, t3, t4 = st.tabs([
            ":material/play_circle: Oscilación 2D 60fps",
            ":material/show_chart: Desplazamientos",
            ":material/autorenew: Retrato de Fase",
            ":material/bolt: Energía Mecánica",
        ])

        with t1:
            components.html(html_animacion_edificio(t_b_imp, y_b_imp, y_b_ref), height=445, scrolling=False)

        with t2:
            fig_e = make_subplots(rows=1, cols=2, subplot_titles=("Piso 2 x2(t)", "Piso 1 x1(t)"))
            fig_e.add_trace(go.Scatter(x=t_b_imp, y=y_b_ref[:, 1], line=dict(color=TEXT_CRISP, width=2.2), name="Ref. Radau"), row=1, col=1)
            fig_e.add_trace(go.Scatter(x=t_b_imp, y=y_b_imp[:, 1], mode="lines+markers", line=dict(color=EMERALD, width=1.8), marker=dict(size=4), name="Euler Implícito"), row=1, col=1)
            fig_e.add_trace(go.Scatter(x=t_b_imp, y=y_b_ref[:, 0], line=dict(color=TEXT_CRISP, width=2.2), showlegend=False), row=1, col=2)
            fig_e.add_trace(go.Scatter(x=t_b_imp, y=y_b_imp[:, 0], mode="lines+markers", line=dict(color=AMBER, width=1.8), marker=dict(size=4), name="Piso 1 Implícito"), row=1, col=2)
            aplicar_estilo_plotly(fig_e, titulo="Respuesta Sísmica de los 2 Pisos", height=430)
            st.plotly_chart(fig_e, use_container_width=True)

        with t3:
            fig_p = go.Figure()
            fig_p.add_trace(go.Scatter(x=y_b_ref[:, 1], y=y_b_ref[:, 3], line=dict(color=TEXT_CRISP, width=2.0), name="Referencia"))
            fig_p.add_trace(go.Scatter(x=y_b_imp[:, 1], y=y_b_imp[:, 3], line=dict(color=EMERALD, width=1.8, dash="dash"), name="Euler Implícito"))
            fig_p.update_xaxes(title_text="Desplazamiento x2 [m]")
            fig_p.update_yaxes(title_text="Velocidad v2 [m/s]")
            aplicar_estilo_plotly(fig_p, titulo="Retrato de Fase Piso 2 (x2 vs v2)", height=430)
            st.plotly_chart(fig_p, use_container_width=True)

        with t4:
            fig_en = go.Figure()
            fig_en.add_trace(go.Scatter(x=t_b_imp, y=e_ref, line=dict(color=TEXT_CRISP, width=2.2), name="Energía Referencia"))
            fig_en.add_trace(go.Scatter(x=t_b_imp, y=e_imp, line=dict(color=EMERALD, width=2.0, dash="dash"), name="Energía Implícito"))
            me = (~np.isnan(e_exp)) & (e_exp < 50.0)
            fig_en.add_trace(go.Scatter(x=t_b_exp[me], y=e_exp[me], line=dict(color=CORAL, width=1.6), name="Energía Explícito (Inyección espuria)"))
            fig_en.update_xaxes(title_text="Tiempo t [s]")
            fig_en.update_yaxes(title_text="Energía E(t) [J]")
            aplicar_estilo_plotly(fig_en, titulo="Balance Energético Estructural", height=430)
            st.plotly_chart(fig_en, use_container_width=True)

        # Descarga de datos sismo
        df_bldg = pd.DataFrame({"t": t_b_imp, "x1": y_b_imp[:, 0], "x2": y_b_imp[:, 1], "v1": y_b_imp[:, 2], "v2": y_b_imp[:, 3], "E_implicito": e_imp, "E_referencia": e_ref})
        descargar_dataframe_csv(df_bldg, "edificio_sismo_eulerlab.csv", "Descargar Datos Respuesta Sísmica (CSV)")


# =============================================================================
# VISTA 5: Benchmark de Cómputo y Convergencia O(h)
# =============================================================================
elif vista_idx == 5:
    st.markdown(
        """
        <h1>Benchmark de Cómputo y Convergencia Numérica</h1>
        <p class="q-subtitle">
            Demostración cuantitativa: evalúa el factor de aceleración real (Speedup de CPU y pasos) y verifica
            empíricamente el orden teórico de convergencia $O(h)$ mediante la Tabla de Richardson.
        </p>
        """,
        unsafe_allow_html=True,
    )

    tab_bm, tab_rich = st.tabs([
        ":material/speed: Benchmark de Rendimiento y Speedup",
        ":material/table_rows: Tabla Formal de Richardson O(h)",
    ])

    with tab_bm:
        c_bm1, c_bm2 = st.columns([1, 2])
        with c_bm1:
            with st.container(border=True):
                sis_bm = st.selectbox(
                    "Sistema para Benchmark:",
                    [
                        "Circuito RLC Rígido (S = 1000)",
                        "Cinética Química en Cadena (S = 200)",
                        "Oscilador Acoplado (S = 400)",
                    ],
                )
                if sis_bm == "Circuito RLC Rígido (S = 1000)":
                    A_bm = np.array([[0.0, -1000.0], [1.0, -1001.0]])
                    y0_bm = np.array([10.0, 0.0])
                    t_fin_bm = 3.0
                    h_bm = st.slider("Paso para Euler Implícito [s]:", min_value=0.01, max_value=0.1, value=0.05, step=0.005, format="%.3f")
                elif sis_bm == "Cinética Química en Cadena (S = 200)":
                    A_bm = np.array([[-0.5, 0.0, 0.0], [0.5, -100.0, 0.0], [0.0, 100.0, 0.0]])
                    y0_bm = np.array([1.0, 0.0, 0.0])
                    t_fin_bm = 6.0
                    h_bm = st.slider("Paso para Euler Implícito [s]:", min_value=0.01, max_value=0.15, value=0.06, step=0.005, format="%.3f")
                else:
                    A_bm = np.array([[0.0, 1.0], [-400.0, -401.0]])
                    y0_bm = np.array([2.0, 0.0])
                    t_fin_bm = 2.0
                    h_bm = st.slider("Paso para Euler Implícito [s]:", min_value=0.005, max_value=0.06, value=0.025, step=0.005, format="%.3f")

                res_bm = benchmark_rendimiento_comparativo(A_bm, y0_bm, (0.0, t_fin_bm), h_bm)
                st.markdown(f"**Paso Implícito:** `{res_bm['h_impl']:.4f} s`")
                st.markdown(f"**Paso Explícito Estable:** `{res_bm['h_expl_estable']:.4e} s`")

        with c_bm2:
            render_kpis([
                {"label": "Pasos Implícito", "val": f"{res_bm['n_pasos_impl']}", "sub": f"Tiempo: {res_bm['cpu_impl_ms']:.2f} ms", "bar": "emerald"},
                {"label": "Pasos Explícito", "val": f"{res_bm['n_pasos_expl']}", "sub": f"Tiempo: {res_bm['cpu_expl_ms']:.2f} ms", "bar": "coral"},
                {"label": "Aceleración Pasos", "val": f"{res_bm['speedup_pasos']:.1f}×", "sub": "Menor esfuerzo numérico", "bar": "amber"},
                {"label": "Ahorro de Cómputo", "val": f"{res_bm['ahorro_porcentaje']:.1f}%", "sub": "Pasos evitados", "bar": "cyan"},
            ])

            # Gráfico de barras comparativo
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=["Euler Implícito (LU)", "Euler Explícito"],
                y=[res_bm["n_pasos_impl"], res_bm["n_pasos_expl"]],
                marker_color=[EMERALD, CORAL],
                text=[f"{res_bm['n_pasos_impl']} pasos", f"{res_bm['n_pasos_expl']} pasos"],
                textposition="auto",
            ))
            fig_bar.update_yaxes(title_text="Número total de pasos temporales N")
            aplicar_estilo_plotly(fig_bar, titulo=f"Comparativa de Costo en Pasos (Speedup: {res_bm['speedup_pasos']:.1f}×)", height=320)
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab_rich:
        st.markdown(
            r"""
            <div class="speaker-card" style="margin-top:0;">
                <h4>Verificación Rigurosa del Orden Teórico O(h)</h4>
                <p>
                    El orden de convergencia experimental $p$ se calcula comparando el error global entre pasos sucesivos
                    mediante la relación:
                    $$p = \frac{\ln(E_{h_{k-1}} / E_{h_k})}{\ln(h_{k-1} / h_k)}$$
                    A medida que $h \to 0$, $p$ converge exactamente a <b>1.00</b>, confirmando la validez teórica del esquema.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        A_rich = np.array([[0.0, -1000.0], [1.0, -1001.0]])
        y0_rich = np.array([10.0, 0.0])
        hs_rich = [0.1, 0.05, 0.025, 0.0125, 0.00625]

        tabla_filas = tabla_convergencia_formal(A_rich, y0_rich, (0.0, 2.0), hs_rich)
        df_rich = pd.DataFrame(tabla_filas)

        # Mostrar tabla sin columnas privadas
        cols_mostrar = [c for c in df_rich.columns if not c.startswith("_")]
        st.dataframe(df_rich[cols_mostrar], use_container_width=True)

        # Gráfico log-log de convergencia
        fig_conv_log = go.Figure()
        fig_conv_log.add_trace(go.Scatter(
            x=df_rich["_h"],
            y=df_rich["_e_inf"],
            mode="lines+markers",
            line=dict(color=EMERALD, width=2.5),
            marker=dict(size=8),
            name="Error experimental ||e||_∞",
        ))
        # Recta de referencia O(h)
        h_arr = df_rich["_h"].values
        ref_line = df_rich["_e_inf"].values[-1] * (h_arr / h_arr[-1])
        fig_conv_log.add_trace(go.Scatter(
            x=h_arr,
            y=ref_line,
            line=dict(color=AMBER, width=2.0, dash="dash"),
            name="Pendiente teórica 1.0 (O(h))",
        ))
        fig_conv_log.update_xaxes(type="log", title_text="Paso temporal h [s] (Escala Logarítmica)")
        fig_conv_log.update_yaxes(type="log", title_text="Error Global ||e||_∞ (Escala Logarítmica)")
        aplicar_estilo_plotly(fig_conv_log, titulo="Curva de Convergencia Experimental Log-Log", height=410)
        st.plotly_chart(fig_conv_log, use_container_width=True)


# =============================================================================
# VISTA 6: Galería e Informe PDF
# =============================================================================
elif vista_idx == 6:
    st.markdown(
        """
        <h1>Galería de Figuras e Informe Académico</h1>
        <p class="q-subtitle">
            Figuras científicas en alta resolución (300 DPI) generadas por el proyecto y acceso directo al informe en PDF (UMSA).
        </p>
        """,
        unsafe_allow_html=True,
    )

    c_act1, c_act2 = st.columns([1, 1])
    with c_act1:
        if st.button("Regenerar figuras científicas (300 DPI)", icon=":material/refresh:", type="primary", use_container_width=True):
            with st.spinner("Actualizando figuras en alta resolución..."):
                for s in [
                    "ejercicios/ejercicio1_circuito_rlc_rigido.py",
                    "ejercicios/ejercicio2_reaccion_quimica_cadena.py",
                    "ejercicios/ejercicio3_sismo_edificio_2pisos.py",
                ]:
                    subprocess.run([sys.executable, str(ROOT_DIR / s)], check=True, cwd=str(ROOT_DIR))
            st.success("Figuras actualizadas correctamente.")

    with c_act2:
        pdf_path = ROOT_DIR / "informe.pdf"
        if pdf_path.exists():
            with open(pdf_path, "rb") as f_pdf:
                st.download_button(
                    label="Descargar Informe Académico (PDF)",
                    icon=":material/download:",
                    data=f_pdf.read(),
                    file_name="informe_euler_implicito.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        else:
            if st.button("Compilar Informe PDF", icon=":material/picture_as_pdf:", use_container_width=True):
                with st.spinner("Generando documento PDF..."):
                    subprocess.run(["pdflatex", "-interaction=nonstopmode", "informe.tex"], check=True, cwd=str(ROOT_DIR))
                    subprocess.run(["pdflatex", "-interaction=nonstopmode", "informe.tex"], check=True, cwd=str(ROOT_DIR))
                st.success("Informe PDF generado exitosamente.")
                st.rerun()

    st.markdown("---")

    figuras_png = [
        ("ej1_rlc_comparacion.png", "Caso 1 · Circuito RLC Rígido (300 DPI)"),
        ("ej2_cinetica_quimica.png", "Caso 2 · Cinética Química en Cadena (300 DPI)"),
        ("ej3_edificio_sismo.png", "Caso 3 · Edificio Sísmico de 2 Pisos (300 DPI)"),
    ]
    for fname, cap in figuras_png:
        fpath = IMG_DIR / fname
        if fpath.exists():
            st.image(str(fpath), caption=cap, use_container_width=True)
