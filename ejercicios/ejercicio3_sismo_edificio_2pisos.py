"""
Ejercicio 3: Dinámica Estructural Sísmica — Edificio de 2 Pisos (Sistema 4x4).
==============================================================================
Modela un edificio de 2 niveles sometido a una aceleración sísmica amortiguada
a_g(t) = 12 * exp(-0.4*t) * sin(4.5*t) mediante el sistema lineal no homogéneo:
    y'(t) = A y(t) + g(t),    y = [x1, x2, v1, v2]^T

Resuelve con Euler Implícito mediante factorización LU precomputada y compara
con referencia de alta precisión (Radau) y Euler Explícito, evidenciando cómo
Euler Explícito inyecta energía artificial mientras Euler Implícito mantiene
estabilidad estructural.

Guarda automáticamente en img/:
    - img/ej3_edificio_sismo.png
    - img/ej3_edificio_animacion.gif
"""

import sys
from pathlib import Path
from typing import Callable
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.euler_implicito import (
    euler_implicito_lineal,
    euler_explicito_lineal,
    analizar_estabilidad,
)


BG_COLOR = "#0B1120"
PANEL_COLOR = "#111827"
GRID_COLOR = "#1E293B"
TEXT_COLOR = "#F8FAFC"
MUTED_COLOR = "#94A3B8"
CYAN_IMPL = "#06B6D4"
EMERALD_REF = "#10B981"
CORAL_EXPL = "#F97316"
VIOLET_PISO1 = "#8B5CF6"


def obtener_carpeta_img() -> Path:
    base = Path(__file__).resolve().parent
    img_dir = (base.parent / "img") if base.name == "ejercicios" else (base / "img")
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir


def aceleracion_sismica(t: float) -> float:
    return 12.0 * np.exp(-0.4 * t) * np.sin(4.5 * t)


def euler_implicito_no_homogeneo(
    A: np.ndarray,
    g_func: Callable[[float], np.ndarray],
    y0: np.ndarray,
    t_final: float,
    h: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve y' = A y + g(t) mediante Euler Implícito delegando en el core numérico."""
    return euler_implicito_lineal(A, y0, (0.0, t_final), h, g=g_func)


def euler_explicito_no_homogeneo(
    A: np.ndarray,
    g_func: Callable[[float], np.ndarray],
    y0: np.ndarray,
    t_final: float,
    h: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve y' = A y + g(t) mediante Euler Explícito delegando en el core numérico."""
    return euler_explicito_lineal(A, y0, (0.0, t_final), h, g=g_func, limite_divergencia=1e4)


def energia_mecanica(y: np.ndarray, m1: float, m2: float, k1: float, k2: float) -> np.ndarray:
    x1, x2, v1, v2 = y[:, 0], y[:, 1], y[:, 2], y[:, 3]
    cinetica = 0.5 * (m1 * v1**2 + m2 * v2**2)
    potencial = 0.5 * (k1 * x1**2 + k2 * (x2 - x1)**2)
    return cinetica + potencial


def configurar_estilo() -> None:
    plt.rcParams.update({
        "figure.facecolor": BG_COLOR,
        "axes.facecolor": PANEL_COLOR,
        "axes.edgecolor": "#334155",
        "axes.labelcolor": TEXT_COLOR,
        "xtick.color": MUTED_COLOR,
        "ytick.color": MUTED_COLOR,
        "text.color": TEXT_COLOR,
        "grid.color": GRID_COLOR,
        "grid.linestyle": "--",
        "grid.alpha": 0.8,
        "font.size": 10,
    })


def main() -> None:
    configurar_estilo()
    img_dir = obtener_carpeta_img()

    # Parámetros estructurales del edificio de 2 pisos
    m1, m2 = 1.0, 1.0
    k1, k2 = 120.0, 80.0
    c1, c2 = 6.0, 4.0

    A = np.array([
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [-(k1 + k2) / m1, k2 / m1, -(c1 + c2) / m1, c2 / m1],
        [k2 / m2, -k2 / m2, c2 / m2, -c2 / m2],
    ])

    def g_vec(ti: float) -> np.ndarray:
        ag = aceleracion_sismica(ti)
        return np.array([0.0, 0.0, -ag, -ag])

    y0 = np.zeros(4)
    t_final = 8.0
    h = 0.06  # Paso moderado donde Euler Explícito se vuelve inestable por modos complejos

    eigvals = np.linalg.eigvals(A)
    t_impl, y_impl = euler_implicito_no_homogeneo(A, g_vec, y0, t_final, h)
    t_expl, y_expl = euler_explicito_no_homogeneo(A, g_vec, y0, t_final, h)

    # Referencia de alta precisión
    sol_ref = solve_ivp(
        lambda ti, yi: A @ yi + g_vec(ti),
        (0.0, t_final),
        y0,
        method="Radau",
        t_eval=t_impl,
        rtol=1e-11,
        atol=1e-13,
    )
    y_ref = sol_ref.y.T

    e_impl = energia_mecanica(y_impl, m1, m2, k1, k2)
    e_ref = energia_mecanica(y_ref, m1, m2, k1, k2)
    e_expl = energia_mecanica(y_expl, m1, m2, k1, k2)

    err_x2 = np.max(np.abs(y_impl[:, 1] - y_ref[:, 1]))
    err_global = np.max(np.abs(y_impl - y_ref))
    max_expl = np.nanmax(np.abs(y_expl[:, 1]))

    print("=== EJERCICIO 3: DINÁMICA SÍSMICA — EDIFICIO 2 PISOS (4x4) ===")
    print("Valores propios de A:")
    for ev in eigvals:
        print(f"  {ev.real:+.4f} {ev.imag:+.4f}j | |1 + h*λ| = {abs(1 + h*ev):.4f} | |1/(1-h*λ)| = {abs(1/(1 - h*ev)):.4f}")
    print(f"Error máx. desplazamiento piso 2 (Implícito, h={h}): {err_x2:.6e} m")
    print(f"Error global estado completo (Implícito):            {err_global:.6e}")
    print(f"Desplazamiento pico piso 2 (Euler Explícito):        {max_expl:.4e} m (divergente)")

    # ------------------------------------------------------------------
    # 1. Gráfica estática (PNG 300 DPI)
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8), dpi=300)
    fig.suptitle(
        "Ejercicio 3: Edificio de 2 Pisos Bajo Sismo (Sistema 4×4 No Homogéneo, h = 0.06 s)",
        fontsize=13,
        fontweight="bold",
        color=TEXT_COLOR,
        y=1.02,
    )

    # Panel 1: Desplazamientos x1 y x2
    ax = axes[0]
    ax.plot(t_impl, y_ref[:, 1], color=EMERALD_REF, lw=2.2, label="Piso 2 (Referencia)")
    ax.plot(t_impl, y_impl[:, 1], "--", color=CYAN_IMPL, lw=1.8, label="Piso 2 (Euler Implícito)")
    ax.plot(t_impl, y_impl[:, 0], color=VIOLET_PISO1, lw=1.5, alpha=0.85, label="Piso 1 (Euler Implícito)")
    ax.set_title("Respuesta Sísmica de Pisos $x_1(t), x_2(t)$", fontsize=11, pad=8)
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel("Desplazamiento lateral [m]")
    ax.grid(True)
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8)

    # Panel 2: Retrato de fase del piso 2 (x2 vs v2)
    ax = axes[1]
    ax.plot(y_ref[:, 1], y_ref[:, 3], color=EMERALD_REF, lw=2.0, alpha=0.75, label="Referencia")
    ax.plot(y_impl[:, 1], y_impl[:, 3], color=CYAN_IMPL, lw=1.6, linestyle="--", label="Euler Implícito")
    ax.scatter([0], [0], color="#F8FAFC", s=30, zorder=5, label="Equilibrio (0,0)")
    ax.set_title("Retrato de Fase Piso 2 $(x_2, v_2)$", fontsize=11, pad=8)
    ax.set_xlabel("Desplazamiento $x_2$ [m]")
    ax.set_ylabel("Velocidad $v_2$ [m/s]")
    ax.grid(True)
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8)

    # Panel 3: Energía mecánica (Estabilidad energética vs explosión de Explícito)
    ax = axes[2]
    ax.plot(t_impl, e_ref, color=EMERALD_REF, lw=2.2, label="Energía Referencia")
    ax.plot(t_impl, e_impl, "--", color=CYAN_IMPL, lw=1.8, label="Energía Euler Implícito")
    mask_e = (~np.isnan(e_expl)) & (e_expl < 35.0)
    ax.plot(t_expl[mask_e], e_expl[mask_e], color=CORAL_EXPL, lw=1.5, label="Energía Euler Explícito")
    ax.set_ylim(0, 25)
    ax.set_title("Energía Mecánica Total $E(t)$", fontsize=11, pad=8)
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel("Energía [J]")
    ax.grid(True)
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8)

    plt.tight_layout()
    png_path = img_dir / "ej3_edificio_sismo.png"
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)

    # ------------------------------------------------------------------
    # 2. Gráfica animada (GIF): Edificio 2D oscilando + curvas en vivo
    # ------------------------------------------------------------------
    fig_anim, (ax_bldg, ax_ts) = plt.subplots(
        1, 2, figsize=(11.5, 4.8), dpi=110, gridspec_kw={"width_ratios": [1, 1.7]}
    )
    fig_anim.suptitle(
        "Animación: Oscilación Sísmica del Edificio de 2 Pisos (Euler Implícito)",
        fontsize=11.5,
        fontweight="bold",
        color=TEXT_COLOR,
    )

    # Escala visual para ver claramente el desplazamiento lateral
    escala = 2.6
    ancho = 0.9
    ax_bldg.set_xlim(-1.4, 1.4)
    ax_bldg.set_ylim(-0.3, 2.55)
    ax_bldg.set_aspect("equal")
    ax_bldg.set_title("Estructura 2D (escala lateral ×2.6)", fontsize=10)
    ax_bldg.set_xlabel("Desplazamiento amplificado")
    ax_bldg.set_yticks([0, 1, 2])
    ax_bldg.set_yticklabels(["Suelo", "Piso 1", "Piso 2"])
    ax_bldg.grid(True, alpha=0.4)
    ax_bldg.axhline(0.0, color="#64748B", lw=3.0)

    col_izq, = ax_bldg.plot([], [], color="#94A3B8", lw=3.0)
    col_der, = ax_bldg.plot([], [], color="#94A3B8", lw=3.0)
    losa1, = ax_bldg.plot([], [], color=VIOLET_PISO1, lw=7.0, solid_capstyle="round")
    losa2, = ax_bldg.plot([], [], color=CYAN_IMPL, lw=7.0, solid_capstyle="round")
    txt_bldg = ax_bldg.text(0.0, 2.32, "", ha="center", fontsize=9, fontweight="bold", color=TEXT_COLOR)

    ax_ts.set_xlim(0, t_final)
    y_lim = max(np.max(np.abs(y_impl[:, 1])), 0.25) * 1.25
    ax_ts.set_ylim(-y_lim, y_lim)
    ax_ts.set_xlabel("Tiempo $t$ [s]")
    ax_ts.set_ylabel("Desplazamiento [m]")
    ax_ts.set_title("Registro Sísmico en Vivo", fontsize=10)
    ax_ts.grid(True)
    ax_ts.plot(t_impl, y_ref[:, 1], color=EMERALD_REF, lw=1.2, alpha=0.35, label="Piso 2 (Ref.)")
    line_x1, = ax_ts.plot([], [], color=VIOLET_PISO1, lw=1.8, label="Piso 1 $x_1(t)$")
    line_x2, = ax_ts.plot([], [], color=CYAN_IMPL, lw=2.2, label="Piso 2 $x_2(t)$")
    ax_ts.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8.5, loc="upper right")

    n_frames = 65
    indices = np.linspace(0, len(t_impl) - 1, n_frames, dtype=int)

    def update(frame: int):
        idx = indices[frame]
        x1_s = y_impl[idx, 0] * escala
        x2_s = y_impl[idx, 1] * escala

        col_izq.set_data([-ancho / 2, x1_s - ancho / 2, x2_s - ancho / 2], [0.0, 1.0, 2.0])
        col_der.set_data([ancho / 2, x1_s + ancho / 2, x2_s + ancho / 2], [0.0, 1.0, 2.0])
        losa1.set_data([x1_s - ancho / 2, x1_s + ancho / 2], [1.0, 1.0])
        losa2.set_data([x2_s - ancho / 2, x2_s + ancho / 2], [2.0, 2.0])
        txt_bldg.set_text(f"t = {t_impl[idx]:.2f} s | x2 = {y_impl[idx, 1]:+.3f} m")

        line_x1.set_data(t_impl[: idx + 1], y_impl[: idx + 1, 0])
        line_x2.set_data(t_impl[: idx + 1], y_impl[: idx + 1, 1])
        return col_izq, col_der, losa1, losa2, txt_bldg, line_x1, line_x2

    anim = FuncAnimation(fig_anim, update, frames=n_frames, interval=80, blit=False)
    gif_path = img_dir / "ej3_edificio_animacion.gif"
    anim.save(gif_path, writer=PillowWriter(fps=13))
    plt.close(fig_anim)
    print(f"Archivos guardados: {png_path} y {gif_path}\n")


if __name__ == "__main__":
    main()
