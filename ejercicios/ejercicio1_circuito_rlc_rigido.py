"""
Ejercicio 1: Circuito RLC Acoplado con Rigidez Extrema (Sistema Lineal 2x2).
===========================================================================
Resuelve el sistema de EDOs lineales rígido:
    dV_C/dt = -(1/C) * I
    dI/dt   = (1/L) * V_C - (R/L) * I

con R = 1001 Ohm, L = 1 H, C = 1e-3 F, cuyos valores propios exactos son
lambda_1 = -1 y lambda_2 = -1000 (razón de rigidez S = 1000).

Demuestra la A-estabilidad del Método de Euler Implícito con factorización LU
frente a la divergencia explosiva de Euler Explícito cuando h > 2 / |lambda_max|.

Guarda automáticamente en img/:
    - img/ej1_rlc_comparacion.png
    - img/ej1_rlc_animacion.gif
"""

import sys
from pathlib import Path
import numpy as np
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
    solucion_exacta_lineal,
    analizar_estabilidad,
    estudio_convergencia,
)


# Paleta temática "PhaseSpace Observatory" (design.md)
BG_COLOR = "#0B1120"
PANEL_COLOR = "#111827"
GRID_COLOR = "#1E293B"
TEXT_COLOR = "#F8FAFC"
MUTED_COLOR = "#94A3B8"
CYAN_IMPL = "#06B6D4"
EMERALD_EXACT = "#10B981"
CORAL_EXPL = "#F97316"
VIOLET_ACCENT = "#8B5CF6"


def obtener_carpeta_img() -> Path:
    """Devuelve la carpeta img/ del proyecto y la crea si no existe."""
    base = Path(__file__).resolve().parent
    img_dir = (base.parent / "img") if base.name == "ejercicios" else (base / "img")
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir


def euler_implicito(A: np.ndarray, y0: np.ndarray, t_final: float, h: float) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve y' = A y mediante Euler Implícito delegando en el core numérico."""
    return euler_implicito_lineal(A, y0, (0.0, t_final), h)


def euler_explicito(A: np.ndarray, y0: np.ndarray, t_final: float, h: float) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve y' = A y mediante Euler Explícito delegando en el core numérico."""
    return euler_explicito_lineal(A, y0, (0.0, t_final), h)


def solucion_exacta(A: np.ndarray, y0: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Calcula la solución exacta y(t) = expm(A * t) y0 delegando en el core numérico."""
    return solucion_exacta_lineal(A, y0, t)


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

    # Parámetros del circuito RLC rígido
    R, L, C = 1001.0, 1.0, 1e-3
    A = np.array([
        [0.0, -1.0 / C],
        [1.0 / L, -R / L],
    ])
    y0 = np.array([10.0, 0.0])  # V_C(0) = 10 V, I(0) = 0 A
    t_final = 3.0

    eigvals = np.linalg.eigvals(A)
    rigidez = np.max(np.abs(np.real(eigvals))) / np.min(np.abs(np.real(eigvals)))
    h_critico = 2.0 / np.max(np.abs(np.real(eigvals)))

    # Simulaciones principales
    h_impl = 0.05      # 25 veces mayor que el límite de Euler Explícito
    h_expl_div = 0.00208  # Apenas superior al límite crítico 0.002 -> oscilación divergente visible

    t_impl, y_impl = euler_implicito(A, y0, t_final, h_impl)
    y_exact_impl = solucion_exacta(A, y0, t_impl)

    t_fine = np.linspace(0.0, t_final, 600)
    y_exact_fine = solucion_exacta(A, y0, t_fine)

    t_expl, y_expl = euler_explicito(A, y0, 0.25, h_expl_div)

    # Estudio de convergencia O(h) para Euler Implícito
    hs = np.array([0.2, 0.1, 0.05, 0.025, 0.0125])
    errores_inf = []
    for h_i in hs:
        t_i, y_i = euler_implicito(A, y0, t_final, h_i)
        y_ex_i = solucion_exacta(A, y0, t_i)
        errores_inf.append(np.max(np.abs(y_i - y_ex_i)))
    errores_inf = np.array(errores_inf)
    ordenes = np.log(errores_inf[:-1] / errores_inf[1:]) / np.log(hs[:-1] / hs[1:])

    # Resumen numérico por consola
    print("=== EJERCICIO 1: CIRCUITO RLC RÍGIDO (2x2) ===")
    print(f"Valores propios: {np.sort(np.real(eigvals))}")
    print(f"Razón de rigidez S = {rigidez:.1f}")
    print(f"Paso crítico Euler Explícito: h_max = {h_critico:.4f} s")
    print(f"Error global L_inf (Euler Implícito, h={h_impl}): {np.max(np.abs(y_impl - y_exact_impl)):.6e}")
    print("Estudio de convergencia:")
    for i, h_i in enumerate(hs):
        p_str = f"{ordenes[i-1]:.3f}" if i > 0 else "  -  "
        print(f"  h = {h_i:6.4f} | Error L_inf = {errores_inf[i]:.6e} | Orden p = {p_str}")

    # ------------------------------------------------------------------
    # 1. Gráfica estática (PNG 300 DPI)
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8), dpi=300)
    fig.suptitle(
        "Ejercicio 1: Circuito RLC Rígido (S = 1000) — Euler Implícito vs Explícito",
        fontsize=13,
        fontweight="bold",
        color=TEXT_COLOR,
        y=1.02,
    )

    # Panel 1: Descarga de voltaje V_C(t)
    ax = axes[0]
    ax.plot(t_fine, y_exact_fine[:, 0], color=EMERALD_EXACT, lw=2.2, label="Exacta")
    ax.plot(t_impl, y_impl[:, 0], "o--", color=CYAN_IMPL, ms=3.5, lw=1.4, label=f"Euler Implícito (h={h_impl}s)")
    ax.set_title("Voltaje en el Capacitor $V_C(t)$", fontsize=11, pad=8)
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel("$V_C(t)$ [V]")
    ax.grid(True)
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8.5)

    # Panel 2: Explosión numérica de Euler Explícito en capa límite
    ax = axes[1]
    t_zoom = np.linspace(0.0, 0.16, 300)
    y_ex_zoom = solucion_exacta(A, y0, t_zoom)
    mask_expl = (t_expl <= 0.16) & (~np.isnan(y_expl[:, 0]))
    mask_impl = t_impl <= 0.16
    ax.plot(t_zoom, y_ex_zoom[:, 0], color=EMERALD_EXACT, lw=2.2, label="Exacta")
    ax.plot(t_impl[mask_impl], y_impl[mask_impl, 0], "o-", color=CYAN_IMPL, ms=5, lw=1.6, label=f"Implícito (h={h_impl}s)")
    ax.plot(t_expl[mask_expl], y_expl[mask_expl, 0], color=CORAL_EXPL, lw=1.4, label=f"Explícito (h={h_expl_div}s)")
    ax.set_ylim(-15, 35)
    ax.set_title("Inestabilidad de Euler Explícito ($h > 0.002$ s)", fontsize=11, pad=8)
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel("$V_C(t)$ [V]")
    ax.grid(True)
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8.5)

    # Panel 3: Convergencia log-log O(h)
    ax = axes[2]
    ax.loglog(hs, errores_inf, "o-", color=CYAN_IMPL, lw=2.0, ms=6, label="Error global $\\|e\\|_\\infty$")
    ref_line = errores_inf[-1] * (hs / hs[-1])
    ax.loglog(hs, ref_line, "--", color=VIOLET_ACCENT, lw=1.5, label="Pendiente teórica $O(h)$")
    ax.set_title("Convergencia de Euler Implícito", fontsize=11, pad=8)
    ax.set_xlabel("Tamaño de paso $h$ [s]")
    ax.set_ylabel("Error máximo $\\|e\\|_\\infty$")
    ax.grid(True, which="both")
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8.5)

    plt.tight_layout()
    png_path = img_dir / "ej1_rlc_comparacion.png"
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)

    # ------------------------------------------------------------------
    # 2. Gráfica animada (GIF)
    # ------------------------------------------------------------------
    fig_anim, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=110)
    fig_anim.suptitle(
        "Animación: Estabilidad de Euler Implícito vs Divergencia de Euler Explícito (RLC)",
        fontsize=11.5,
        fontweight="bold",
        color=TEXT_COLOR,
    )

    ax_l.set_xlim(0, t_final)
    ax_l.set_ylim(-0.5, 11.0)
    ax_l.set_xlabel("Tiempo $t$ [s]")
    ax_l.set_ylabel("$V_C(t)$ [V]")
    ax_l.set_title(f"Euler Implícito (h = {h_impl} s — A-estable)", fontsize=10)
    ax_l.grid(True)
    ax_l.plot(t_fine, y_exact_fine[:, 0], color=EMERALD_EXACT, lw=1.8, alpha=0.65, label="Exacta")
    line_impl, = ax_l.plot([], [], "o-", color=CYAN_IMPL, ms=4, lw=1.8, label="Euler Implícito")
    ax_l.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8.5, loc="upper right")

    t_anim_expl = t_expl[t_expl <= 0.14]
    y_anim_expl = y_expl[: len(t_anim_expl), 0]
    ax_r.set_xlim(0, 0.14)
    ax_r.set_ylim(-25, 45)
    ax_r.set_xlabel("Tiempo $t$ [s]")
    ax_r.set_ylabel("$V_C(t)$ [V]")
    ax_r.set_title(f"Euler Explícito (h = {h_expl_div} s — Inestable)", fontsize=10)
    ax_r.grid(True)
    ax_r.plot(t_zoom[t_zoom <= 0.14], y_ex_zoom[t_zoom <= 0.14, 0], color=EMERALD_EXACT, lw=1.8, alpha=0.65, label="Exacta")
    line_expl, = ax_r.plot([], [], "-", color=CORAL_EXPL, lw=1.8, label="Euler Explícito")
    status_txt = ax_r.text(
        0.04, 0.08, "", transform=ax_r.transAxes, fontsize=9, fontweight="bold",
        color="#EF4444", bbox=dict(facecolor=BG_COLOR, edgecolor="#EF4444", boxstyle="round,pad=0.3")
    )
    ax_r.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8.5, loc="upper left")

    n_frames = 50

    def update(frame: int):
        idx_i = max(1, int((frame + 1) / n_frames * len(t_impl)))
        line_impl.set_data(t_impl[:idx_i], y_impl[:idx_i, 0])

        idx_e = max(1, int((frame + 1) / n_frames * len(t_anim_expl)))
        line_expl.set_data(t_anim_expl[:idx_e], y_anim_expl[:idx_e])
        val_actual = y_anim_expl[idx_e - 1]
        if np.isnan(val_actual) or abs(val_actual) > 15:
            status_txt.set_text("DIVERGENCIA NUMÉRICA (|1 + hλ| > 1)")
        else:
            status_txt.set_text(f"t = {t_anim_expl[idx_e - 1]:.3f} s | Oscilación creciente...")
        return line_impl, line_expl, status_txt

    anim = FuncAnimation(fig_anim, update, frames=n_frames, interval=85, blit=False)
    gif_path = img_dir / "ej1_rlc_animacion.gif"
    anim.save(gif_path, writer=PillowWriter(fps=12))
    plt.close(fig_anim)
    print(f"Archivos guardados: {png_path} y {gif_path}\n")


if __name__ == "__main__":
    main()
