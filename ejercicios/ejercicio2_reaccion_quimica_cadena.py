"""
Ejercicio 2: Cinética Química en Cadena Rígida A -> B -> C (Sistema Lineal 3x3).
================================================================================
Modela una reacción consecutiva en un reactor químico con especie intermedia B
de vida ultracorta:
    dA/dt = -k1 * A
    dB/dt =  k1 * A - k2 * B
    dC/dt =  k2 * B

con k1 = 0.5 s^-1, k2 = 100.0 s^-1 (razón de rigidez S = 200), A(0)=1, B(0)=0, C(0)=0.
Demuestra positividad, conservación de masa (A + B + C = 1) y estabilidad del
Método de Euler Implícito frente a las oscilaciones no físicas de Euler Explícito.

Guarda automáticamente en img/:
    - img/ej2_cinetica_quimica.png
    - img/ej2_cinetica_animacion.gif
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
    analizar_estabilidad,
)


BG_COLOR = "#0B1120"
PANEL_COLOR = "#111827"
GRID_COLOR = "#1E293B"
TEXT_COLOR = "#F8FAFC"
MUTED_COLOR = "#94A3B8"
CYAN_A = "#06B6D4"
VIOLET_B = "#8B5CF6"
EMERALD_C = "#10B981"
CORAL_EXPL = "#F97316"


def obtener_carpeta_img() -> Path:
    base = Path(__file__).resolve().parent
    img_dir = (base.parent / "img") if base.name == "ejercicios" else (base / "img")
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir


def euler_implicito(A: np.ndarray, y0: np.ndarray, t_final: float, h: float) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve y' = A y mediante Euler Implícito delegando en el core numérico."""
    return euler_implicito_lineal(A, y0, (0.0, t_final), h)


def euler_explicito(A: np.ndarray, y0: np.ndarray, t_final: float, h: float) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve y' = A y mediante Euler Explícito delegando en el core numérico."""
    return euler_explicito_lineal(A, y0, (0.0, t_final), h, limite_divergencia=1e4)


def solucion_analitica(t: np.ndarray, k1: float, k2: float) -> np.ndarray:
    a_t = np.exp(-k1 * t)
    b_t = (k1 / (k2 - k1)) * (np.exp(-k1 * t) - np.exp(-k2 * t))
    c_t = 1.0 - a_t - b_t
    return np.column_stack([a_t, b_t, c_t])


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

    k1, k2 = 0.5, 100.0
    A_mat = np.array([
        [-k1, 0.0, 0.0],
        [k1, -k2, 0.0],
        [0.0, k2, 0.0],
    ])
    y0 = np.array([1.0, 0.0, 0.0])
    t_final = 8.0
    h = 0.05  # Supera h_critico = 2 / k2 = 0.02 s

    t_impl, y_impl = euler_implicito(A_mat, y0, t_final, h)
    y_exact_impl = solucion_analitica(t_impl, k1, k2)
    t_expl, y_expl = euler_explicito(A_mat, y0, 0.6, h)

    t_fine = np.linspace(0.0, t_final, 800)
    y_exact_fine = solucion_analitica(t_fine, k1, k2)

    masa_impl = np.sum(y_impl, axis=1)
    err_masa = np.max(np.abs(masa_impl - 1.0))
    err_inf = np.max(np.abs(y_impl - y_exact_impl))
    err_l2 = np.sqrt(np.mean(np.sum((y_impl - y_exact_impl) ** 2, axis=1)))

    print("=== EJERCICIO 2: CINÉTICA QUÍMICA EN CADENA A -> B -> C (3x3) ===")
    print(f"Valores propios: [0.0, {-k1}, {-k2}] | Razón de rigidez S = {k2/k1:.1f}")
    print(f"Paso h = {h} s (límite Euler Explícito = {2.0/k2:.3f} s)")
    print(f"Error global L_inf (Euler Implícito): {err_inf:.6e}")
    print(f"Error RMS L_2 (Euler Implícito):      {err_l2:.6e}")
    print(f"Error máx. conservación de masa:      {err_masa:.6e}")
    print(f"Mínimo valor de B(t) en Implícito:    {np.min(y_impl[:, 1]):.6e} (siempre >= 0)")

    # ------------------------------------------------------------------
    # 1. Gráfica estática (PNG 300 DPI)
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8), dpi=300)
    fig.suptitle(
        "Ejercicio 2: Cinética Química Rígida $A \\to B \\to C$ ($k_1=0.5, k_2=100$)",
        fontsize=13,
        fontweight="bold",
        color=TEXT_COLOR,
        y=1.02,
    )

    # Panel 1: Concentraciones A(t) y C(t)
    ax = axes[0]
    ax.plot(t_fine, y_exact_fine[:, 0], color=CYAN_A, lw=2.2, alpha=0.55, label="[A] Exacta")
    ax.plot(t_impl[::4], y_impl[::4, 0], "o", color=CYAN_A, ms=4, label="[A] Euler Implícito")
    ax.plot(t_fine, y_exact_fine[:, 2], color=EMERALD_C, lw=2.2, alpha=0.55, label="[C] Exacta")
    ax.plot(t_impl[::4], y_impl[::4, 2], "s", color=EMERALD_C, ms=3.8, label="[C] Euler Implícito")
    ax.set_title("Reactivo $[A](t)$ y Producto $[C](t)$", fontsize=11, pad=8)
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel("Concentración [mol/L]")
    ax.grid(True)
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8)

    # Panel 2: Especie intermedia B(t) — capa límite y contraste con Explícito
    ax = axes[1]
    ax.plot(t_fine, y_exact_fine[:, 1] * 1e3, color=EMERALD_C, lw=2.2, label="[B] Exacta")
    ax.plot(t_impl, y_impl[:, 1] * 1e3, "o-", color=VIOLET_B, ms=3, lw=1.4, label=f"[B] Implícito (h={h}s)")
    mask_e = (t_expl <= 0.45) & (~np.isnan(y_expl[:, 1]))
    ax.plot(t_expl[mask_e], y_expl[mask_e, 1] * 1e3, "x--", color=CORAL_EXPL, lw=1.3, label=f"[B] Explícito (h={h}s)")
    ax.set_xlim(0, 1.5)
    ax.set_ylim(-12, 12)
    ax.axhline(0.0, color="#475569", lw=0.9)
    ax.set_title("Intermediario $[B](t)$ ($\\times 10^{-3}$ mol/L)", fontsize=11, pad=8)
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel("$[B](t)$ [mmol/L]")
    ax.grid(True)
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8)

    # Panel 3: Conservación de masa y error temporal
    ax = axes[2]
    error_t = np.max(np.abs(y_impl - y_exact_impl), axis=1)
    ax.semilogy(t_impl[1:], error_t[1:], color=CYAN_A, lw=2.0, label="Error $\\|y_k - y(t_k)\\|_\\infty$")
    ax.semilogy(
        t_impl[1:],
        np.maximum(np.abs(masa_impl[1:] - 1.0), 1e-16),
        color=EMERALD_C,
        lw=1.8,
        linestyle="--",
        label="$|A+B+C - 1|$ (Masa)",
    )
    ax.set_title("Error Global y Conservación de Masa", fontsize=11, pad=8)
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel("Magnitud (escala log)")
    ax.grid(True, which="both")
    ax.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8)

    plt.tight_layout()
    png_path = img_dir / "ej2_cinetica_quimica.png"
    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)

    # ------------------------------------------------------------------
    # 2. Gráfica animada (GIF): Reactor de barras + curvas en vivo
    # ------------------------------------------------------------------
    fig_anim, (ax_bar, ax_curve) = plt.subplots(
        1, 2, figsize=(11.2, 4.6), dpi=110, gridspec_kw={"width_ratios": [1, 1.8]}
    )
    fig_anim.suptitle(
        "Animación: Reactor Químico $A \\to B \\to C$ (Euler Implícito, h = 0.05 s)",
        fontsize=11.5,
        fontweight="bold",
        color=TEXT_COLOR,
    )

    especies = ["Reactivo A", "Interm. B (x100)", "Producto C"]
    barras = ax_bar.bar(especies, [1.0, 0.0, 0.0], color=[CYAN_A, VIOLET_B, EMERALD_C], width=0.55)
    ax_bar.set_ylim(0, 1.15)
    ax_bar.set_ylabel("Concentración [mol/L]")
    ax_bar.set_title("Estado del Reactor en Vivo", fontsize=10)
    ax_bar.grid(True, axis="y")
    txt_tiempo = ax_bar.text(
        0.5, 1.05, "t = 0.00 s | A+B+C = 1.000000", ha="center", fontsize=9, fontweight="bold", color=TEXT_COLOR
    )

    ax_curve.set_xlim(0, t_final)
    ax_curve.set_ylim(-0.04, 1.08)
    ax_curve.set_xlabel("Tiempo $t$ [s]")
    ax_curve.set_ylabel("Concentración [mol/L]")
    ax_curve.set_title("Evolución Temporal (Euler Implícito)", fontsize=10)
    ax_curve.grid(True)
    line_a, = ax_curve.plot([], [], color=CYAN_A, lw=2.2, label="[A](t)")
    line_b, = ax_curve.plot([], [], color=VIOLET_B, lw=2.0, linestyle="--", label="[B](t) × 100")
    line_c, = ax_curve.plot([], [], color=EMERALD_C, lw=2.2, label="[C](t)")
    ax_curve.legend(facecolor=BG_COLOR, edgecolor="#334155", fontsize=8.5, loc="center right")

    n_frames = 55

    def update(frame: int):
        idx = max(1, int((frame + 1) / n_frames * len(t_impl)))
        a_val, b_val, c_val = y_impl[idx - 1]
        barras[0].set_height(a_val)
        barras[1].set_height(b_val * 100.0)
        barras[2].set_height(c_val)
        txt_tiempo.set_text(f"t = {t_impl[idx - 1]:.2f} s | A+B+C = {a_val + b_val + c_val:.6f}")

        line_a.set_data(t_impl[:idx], y_impl[:idx, 0])
        line_b.set_data(t_impl[:idx], y_impl[:idx, 1] * 100.0)
        line_c.set_data(t_impl[:idx], y_impl[:idx, 2])
        return (*barras, txt_tiempo, line_a, line_b, line_c)

    anim = FuncAnimation(fig_anim, update, frames=n_frames, interval=85, blit=False)
    gif_path = img_dir / "ej2_cinetica_animacion.gif"
    anim.save(gif_path, writer=PillowWriter(fps=12))
    plt.close(fig_anim)
    print(f"Archivos guardados: {png_path} y {gif_path}\n")


if __name__ == "__main__":
    main()
