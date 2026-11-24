"""
EulerLab — Observatorio Interactivo de Sistemas Dinámicos Rígidos
=================================================================
Dashboard científico responsivo con animaciones fluidas estilo Manim y Canvas 60fps,
navegación lateral colapsable basada en botones e iconos estéticos (sin emojis ni código).
"""

from pathlib import Path
import sys
import subprocess
import numpy as np
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
    analizar_estabilidad,
    solucion_exacta_lineal,
    estudio_convergencia,
)
from dashboard.animaciones import (
    html_manim_inicio,
    html_animacion_rlc,
    html_animacion_cinetica,
    html_animacion_edificio,
)

# -----------------------------------------------------------------------------
# Configuración inicial de Streamlit (sin emojis)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EulerLab · La Ruta del Paso",
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
    """Aplica la estética oscura verde-pizarra de EulerLab a figuras Plotly."""
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
    """Renderiza 4 tarjetas KPI responsivas sin indentación Markdown."""
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


# -----------------------------------------------------------------------------
# Navegación lateral izquierda con botones e iconos Material (sin emojis)
# -----------------------------------------------------------------------------
SECCIONES = [
    (":material/home:", "Inicio", "Inicio y Teoría Visual"),
    (":material/radar:", "Estabilidad", "Estabilidad · Plano z"),
    (":material/bolt:", "Caso 1: RLC", "Caso 1 · Circuito RLC (2×2)"),
    (":material/science:", "Caso 2: Cinética", "Caso 2 · Cinética Química (3×3)"),
    (":material/apartment:", "Caso 3: Sismo", "Caso 3 · Edificio Sísmico (4×4)"),
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
        <div class="euler-sub">EDOs rígidas · Paso a paso</div>
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
            <i>Yoshua Cordova Avendaño</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

vista_idx = st.session_state.vista_idx
render_route_stepper(vista_idx, [(s[0], s[1]) for s in SECCIONES])


# =============================================================================
# VISTA 0: Inicio, Fundamento Visual y Fórmula Animada (Estilo Manim)
# =============================================================================
if vista_idx == 0:
    st.markdown(
        """
        <h1>Euler implícito para sistemas rígidos</h1>
        <p class="q-subtitle">
            Comprende visualmente qué es un sistema de ecuaciones diferenciales rígido, por qué los métodos
            tradicionales colapsan y cómo Euler Implícito logra estabilidad incondicional.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Animación interactiva estilo Manim (burbujas + derivación fluida en 6 etapas)
    components.html(html_manim_inicio(), height=560, scrolling=False)

    # Sección educativa rica e intuitiva (sin código)
    st.markdown(
        """
        <div class="stage-card">
            <h2 style="margin-top:0;">¿Qué resuelve este tema y por qué es tan importante?</h2>
            <p class="q-subtitle" style="margin-bottom:0.8rem;">
                En ingeniería, física, química y economía, los fenómenos que cambian en el tiempo se modelan con sistemas
                lineales de ecuaciones diferenciales ordinarias. El gran desafío aparece cuando el sistema es <b>rígido (stiff)</b>.
            </p>
            <div class="info-grid">
                <div class="info-card">
                    <span class="badge-pill badge-amber">Escalas Disparadas</span>
                    <h4>¿Qué es la Rigidez (Stiffness)?</h4>
                    <p>
                        Ocurre cuando un mismo sistema tiene procesos <b>ultrarrápidos</b> (que duran milisegundos) y procesos
                        <b>lentos</b> (que duran segundos u horas). La razón entre su valor propio más rápido y el más lento
                        se mide con el índice de rigidez <b>S</b>.
                    </p>
                </div>
                <div class="info-card">
                    <span class="badge-pill badge-coral">El Cuello de Botella</span>
                    <h4>¿Por qué falla Euler Explícito?</h4>
                    <p>
                        Aunque la curva de interés ya esté casi plana y suave, un método explícito queda prisionero del componente
                        más rápido: si el paso <i>h</i> supera <i>2 / |λ_max|</i>, cada paso amplifica el error y la solución explota.
                    </p>
                </div>
                <div class="info-card">
                    <span class="badge-pill badge-emerald">Freno Automático</span>
                    <h4>El Poder de Mirar al Futuro</h4>
                    <p>
                        Euler Implícito evalúa la pendiente en el instante destino <b>t_{k+1}</b>. Esto transforma el avance en un
                        sistema lineal <i>(I − hA) y_{k+1} = y_k + h g</i> que es <b>A-estable</b>: nunca diverge para ningún paso <i>h > 0</i>.
                    </p>
                </div>
                <div class="info-card">
                    <span class="badge-pill badge-cyan">Aplicaciones Reales</span>
                    <h4>¿Dónde se utiliza en la práctica?</h4>
                    <p>
                        Simulación de circuitos electrónicos RLC, cinética de reacciones químicas en cadena, respuesta sísmica
                        de edificios, modelos climáticos, robótica y redes neuronales continuas.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cuadro comparativo visual
    st.markdown(
        """
        <div class="stage-card">
            <h3 style="margin-top:0;">Comparación Directa: Explícito vs Implícito</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:10px;">
                <div style="background:#091512;border:1px solid #26413a;border-radius:14px;padding:16px;">
                    <span class="badge-pill badge-coral">Euler Explícito</span>
                    <ul style="margin:10px 0 0;padding-left:18px;color:#a3a58f;font-size:0.88rem;line-height:1.7;">
                        <li>Calcula el siguiente punto usando solo la pendiente actual.</li>
                        <li><b>Región de estabilidad pequeña:</b> disco de radio 1 centrado en (-1, 0).</li>
                        <li>En sistemas rígidos genera oscilaciones artificiales y explosión numérica.</li>
                        <li>Puede producir valores físicamente imposibles (concentraciones negativas).</li>
                    </ul>
                </div>
                <div style="background:#091512;border:1px solid #3ecf9f;border-radius:14px;padding:16px;">
                    <span class="badge-pill badge-stable">Euler Implícito (LU)</span>
                    <ul style="margin:10px 0 0;padding-left:18px;color:#f1ead8;font-size:0.88rem;line-height:1.7;">
                        <li>Resuelve un sistema lineal en cada paso usando factorización LU precomputada.</li>
                        <li><b>A-Estable y L-Estable:</b> estable en todo el semiplano izquierdo.</li>
                        <li>Permite pasos <b>25× a 100× más grandes</b> sin perder estabilidad.</li>
                        <li>Conserva invariantes físicos como la masa total y la disipación de energía.</li>
                    </ul>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# VISTA 1: Laboratorio de Estabilidad (Plano Complejo + La Carrera)
# =============================================================================
elif vista_idx == 1:
    st.markdown(
        """
        <h1>Plano de estabilidad y La Carrera</h1>
        <p class="q-subtitle">
            Mueve el tamaño de paso $h$ para observar en vivo cómo $z = h\\lambda$ entra o sale del disco de Euler Explícito,
            y compara la carrera temporal entre ambos métodos.
        </p>
        """,
        unsafe_allow_html=True,
    )

    col_ctrl, col_plot = st.columns([1, 2.2])

    with col_ctrl:
        st.markdown('<div class="stage-card">', unsafe_allow_html=True)
        sistema_preset = st.selectbox(
            "Sistema Lineal:",
            [
                "Circuito RLC Rígido (2×2, S = 1000)",
                "Cinética Química (3×3, S = 200)",
                "Edificio Sísmico (4×4, Modos Complejos)",
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
            st.markdown(f"• {ev.real:+.2f} {ev.imag:+.2f}j")
        st.markdown(f"**Límite Explícito:** {info_est['h_critico_explicito']:.4f} s")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_plot:
        flag_expl = "INESTABLE" if not info_est["estable_explicito"] else "ESTABLE"
        bar_expl = "coral" if not info_est["estable_explicito"] else "emerald"
        render_kpis([
            {"label": "Paso Temporal h", "val": f"{h_val:.4f} s", "sub": f"h_crit = {info_est['h_critico_explicito']:.4f} s", "bar": "amber"},
            {"label": "Rigidez (S)", "val": f"{info_est['razon_rigidez']:.1f}", "sub": info_est["clasificacion_rigidez"], "bar": "cyan"},
            {"label": "|R(z)| Implícito", "val": f"{info_est['radio_espectral_implicito']:.3f}", "sub": "Siempre <= 1.0", "bar": "emerald"},
            {"label": "|R(z)| Explícito", "val": f"{info_est['radio_espectral_explicito']:.3f}", "sub": f"Estado: {flag_expl}", "bar": bar_expl},
        ])

        tab_z, tab_race = st.tabs([":material/radar: Plano Complejo z = h·λ", ":material/flag: La Carrera (y' = λy)"])

        with tab_z:
            theta = np.linspace(0, 2 * np.pi, 200)
            fig_z = go.Figure()
            fig_z.add_shape(type="rect", x0=-50, y0=-50, x1=0, y1=50, fillcolor="rgba(62, 207, 159, 0.08)", line=dict(width=0), layer="below")
            fig_z.add_trace(go.Scatter(x=-1.0 + np.cos(theta), y=np.sin(theta), fill="toself", fillcolor="rgba(244, 185, 66, 0.22)", line=dict(color=AMBER, width=2.4), name="Estable Explícito |1+z| ≤ 1", hoverinfo="skip"))
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
            z_race = st.slider("Paso adimensional z = h·|λ| en la carrera:", min_value=0.2, max_value=3.5, value=2.4, step=0.1)
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


# =============================================================================
# VISTA 2: Caso 1 — Circuito RLC Rígido (2×2)
# =============================================================================
elif vista_idx == 2:
    st.markdown(
        """
        <h1>Caso 1: Circuito RLC Rígido (2×2)</h1>
        <p class="q-subtitle">
            Descarga con rigidez $S = 1000$ ($\\lambda_1 = -1, \\lambda_2 = -1000$).
            Euler Explícito exige $h \\le 0.002$ s; Euler Implícito integra con pasos grandes manteniendo estabilidad.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Controles de Simulación", icon=":material/tune:", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            R_val = st.number_input("Resistencia R [Ω]:", value=1001.0, step=50.0)
        with c2:
            L_val = st.number_input("Inductancia L [H]:", value=1.0, step=0.1)
        with c3:
            C_val = st.number_input("Capacitancia C [F]:", value=1e-3, format="%.4e")
        with c4:
            t_fin = st.slider("Tiempo T [s]:", min_value=0.5, max_value=6.0, value=3.0, step=0.5)
        h_ej1 = st.slider("Paso temporal h [s]:", min_value=0.001, max_value=0.15, value=0.05, step=0.001, format="%.4f")

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


# =============================================================================
# VISTA 3: Caso 2 — Cinética Química A -> B -> C (3×3)
# =============================================================================
elif vista_idx == 3:
    st.markdown(
        """
        <h1>Caso 2: Cinética Química en Cadena A → B → C (3×3)</h1>
        <p class="q-subtitle">
            Especie intermedia $B$ de vida ultracorta ($S = k_2/k_1 = 200$).
            Euler Implícito preserva positividad ($[B] \\ge 0$) y conservación estricta de masa ($A+B+C = 1$).
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Controles Cinéticos", icon=":material/tune:", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            k1_val = st.number_input("Constante lenta k1 [s⁻¹]:", value=0.5, step=0.1)
        with c2:
            k2_val = st.number_input("Constante rápida k2 [s⁻¹]:", value=100.0, step=10.0)
        with c3:
            h_chem = st.slider("Paso temporal h [s]:", min_value=0.005, max_value=0.2, value=0.05, step=0.005, format="%.3f")

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


# =============================================================================
# VISTA 4: Caso 3 — Dinámica Sísmica de Edificio (4×4)
# =============================================================================
elif vista_idx == 4:
    st.markdown(
        """
        <h1>Caso 3: Edificio de 2 Pisos Bajo Sismo (4×4)</h1>
        <p class="q-subtitle">
            Sistema no homogéneo forzado por aceleración sísmica $a_g(t) = 12 e^{-0.4t}\\sin(4.5t)$.
            Compara desplazamientos, retrato de fase y estabilidad energética.
        </p>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Parámetros Estructurales", icon=":material/tune:", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            k1_ed = st.number_input("Rigidez k1 [N/m]:", value=120.0, step=10.0)
            k2_ed = st.number_input("Rigidez k2 [N/m]:", value=80.0, step=10.0)
        with c2:
            c1_ed = st.number_input("Amortiguamiento c1:", value=6.0, step=1.0)
            c2_ed = st.number_input("Amortiguamiento c2:", value=4.0, step=1.0)
        with c3:
            h_bldg = st.slider("Paso temporal h [s]:", min_value=0.01, max_value=0.12, value=0.06, step=0.005, format="%.3f")
            t_fin_b = st.slider("Horizonte T [s]:", min_value=4.0, max_value=12.0, value=8.0, step=1.0)

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


# =============================================================================
# VISTA 5: Galería e Informe PDF (Sin GIFs ni código)
# =============================================================================
elif vista_idx == 5:
    st.markdown(
        """
        <h1>Galería de Figuras e Informe Académico</h1>
        <p class="q-subtitle">
            Figuras científicas en alta resolución (300 DPI) generadas por el proyecto y acceso directo al informe en PDF.
        </p>
        """,
        unsafe_allow_html=True,
    )

    c_act1, c_act2 = st.columns([1, 1])
    with c_act1:
        if st.button("Regenerar figuras científicas", icon=":material/refresh:", type="primary", use_container_width=True):
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

    # Solo figuras PNG científicas de alta resolución (300 DPI), sin GIFs ni código
    figuras_png = [
        ("ej1_rlc_comparacion.png", "Caso 1 · Circuito RLC Rígido (300 DPI)"),
        ("ej2_cinetica_quimica.png", "Caso 2 · Cinética Química en Cadena (300 DPI)"),
        ("ej3_edificio_sismo.png", "Caso 3 · Edificio Sísmico de 2 Pisos (300 DPI)"),
    ]
    for fname, cap in figuras_png:
        fpath = IMG_DIR / fname
        if fpath.exists():
            st.image(str(fpath), caption=cap, use_container_width=True)
