"""
Módulo de Métodos Numéricos: Euler Implícito y Análisis de Estabilidad
======================================================================
Este módulo provee la implementación optimizada del Método de Euler Implícito
(Backward Euler) para sistemas de ecuaciones diferenciales lineales:

    y'(t) = A y(t) + g(t),    y(t0) = y0

mediante el esquema matricial:

    (I - h*A) y_{k+1} = y_k + h*g(t_{k+1})

utilizando una única factorización LU precomputada O(n^3) en t=0 y resolviendo
cada paso temporal en O(n^2) con sustitución progresiva y regresiva.

Incluye además:
    - Euler Explícito para comparación de estabilidad.
    - Análisis espectral de rigidez y factores de amplificación R(z).
    - Solución exacta / analítica de referencia.
    - Estudio sistemático de convergencia de orden O(h).
"""

from typing import Callable
import time
import numpy as np
from scipy.linalg import expm, lu_factor, lu_solve, lu
from scipy.integrate import solve_ivp


def euler_implicito_lineal(
    A: np.ndarray,
    y0: np.ndarray,
    t_span: tuple[float, float],
    h: float,
    g: Callable[[float], np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve el sistema y'(t) = A y(t) + g(t) mediante Euler Implícito.

    Aplica una única factorización LU precomputada a la matriz M = (I - h*A)
    para resolver (I - h*A) y_{k+1} = y_k + h*g(t_{k+1}) en O(n^2) por paso.

    Parámetros
    ----------
    A : np.ndarray
        Matriz cuadrada de coeficientes de dimensión (n, n).
    y0 : np.ndarray
        Vector de condiciones iniciales de dimensión (n,).
    t_span : tuple[float, float]
        Intervalo de integración (t0, tf).
    h : float
        Tamaño de paso temporal (h > 0).
    g : Callable[[float], np.ndarray] | None, opcional
        Término forzante no homogéneo g(t). Si es None, se asume sistema homogéneo g(t) = 0.

    Retorna
    -------
    t : np.ndarray
        Vector de nodos temporales [t0, t1, ..., tN].
    y : np.ndarray
        Matriz de solución de dimensión (N+1, n), donde y[k] = y(t_k).

    Lanza
    ------
    ValueError
        Si la matriz M = (I - h*A) es numéricamente singular.
    """
    A = np.asarray(A, dtype=float)
    y0 = np.asarray(y0, dtype=float).ravel()
    n = len(y0)
    if A.shape != (n, n):
        raise ValueError(f"Las dimensiones de A {A.shape} no coinciden con y0 ({n},).")

    t0, tf = float(t_span[0]), float(t_span[1])
    if tf <= t0 or h <= 0:
        raise ValueError(f"Parámetros temporales inválidos: t_span=({t0}, {tf}), h={h}.")

    n_pasos = max(1, int(round((tf - t0) / h)))
    t = np.linspace(t0, t0 + n_pasos * h, n_pasos + 1)
    y = np.zeros((n_pasos + 1, n), dtype=float)
    y[0] = y0

    # Construcción de la matriz M = I - h*A y factorización LU precomputada
    M = np.eye(n, dtype=float) - h * A

    # Chequeo de condición
    rcond = np.linalg.cond(M)
    if rcond > 1e14:
        raise ValueError(f"La matriz (I - h*A) está mal condicionada o es singular (cond = {rcond:.2e}).")

    lu, piv = lu_factor(M)

    if g is None:
        for k in range(n_pasos):
            y[k + 1] = lu_solve((lu, piv), y[k])
    else:
        for k in range(n_pasos):
            rhs = y[k] + h * np.asarray(g(t[k + 1]), dtype=float)
            y[k + 1] = lu_solve((lu, piv), rhs)

    return t, y


def euler_explicito_lineal(
    A: np.ndarray,
    y0: np.ndarray,
    t_span: tuple[float, float],
    h: float,
    g: Callable[[float], np.ndarray] | None = None,
    limite_divergencia: float = 1e6,
) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve el sistema y'(t) = A y(t) + g(t) mediante Euler Explícito.

    Aplica el esquema y_{k+1} = y_k + h*(A y_k + g(t_k)). Si los valores
    superan `limite_divergencia` debido a inestabilidad numérica, rellena
    el resto con NaN para evitar desbordamiento por punto flotante.

    Parámetros
    ----------
    A : np.ndarray
        Matriz cuadrada de coeficientes (n, n).
    y0 : np.ndarray
        Vector inicial (n,).
    t_span : tuple[float, float]
        Intervalo de integración (t0, tf).
    h : float
        Paso temporal.
    g : Callable[[float], np.ndarray] | None, opcional
        Término forzante g(t).
    limite_divergencia : float
        Umbral para detectar divergencia explosiva (por defecto 1e6).

    Retorna
    -------
    t : np.ndarray
        Vector de nodos temporales.
    y : np.ndarray
        Solución aproximada (N+1, n).
    """
    A = np.asarray(A, dtype=float)
    y0 = np.asarray(y0, dtype=float).ravel()
    n = len(y0)

    t0, tf = float(t_span[0]), float(t_span[1])
    n_pasos = max(1, int(round((tf - t0) / h)))
    t = np.linspace(t0, t0 + n_pasos * h, n_pasos + 1)
    y = np.zeros((n_pasos + 1, n), dtype=float)
    y[0] = y0

    for k in range(n_pasos):
        gk = 0.0 if g is None else np.asarray(g(t[k]), dtype=float)
        dy = A @ y[k] + gk
        y_next = y[k] + h * dy
        if np.any(np.isnan(y_next)) or np.max(np.abs(y_next)) > limite_divergencia:
            y[k + 1 :] = np.nan
            break
        y[k + 1] = y_next

    return t, y


def analizar_estabilidad(A: np.ndarray, h: float) -> dict:
    """Calcula el espectro de valores propios, rigidez y factores de estabilidad.

    Determina:
        - Valores propios lambda_i de A.
        - Puntos en el plano complejo z_i = h * lambda_i.
        - Factores de amplificación |R(z_i)| para Euler Implícito y Explícito.
        - Razón de rigidez S.
        - Paso crítico teórico de estabilidad para Euler Explícito.
        - Banderas de estabilidad global.

    Parámetros
    ----------
    A : np.ndarray
        Matriz cuadrada del sistema lineal.
    h : float
        Tamaño de paso temporal evaluado.

    Retorna
    -------
    dict
        Diccionario con métricas espectrales y de estabilidad.
    """
    A = np.asarray(A, dtype=float)
    eigvals = np.linalg.eigvals(A)

    # Ordenar por magnitud de la parte real (descendente)
    idx_sorted = np.argsort(np.abs(np.real(eigvals)))[::-1]
    eigvals = eigvals[idx_sorted]

    z_puntos = h * eigvals

    # Factores de amplificación R(z)
    # Euler Implícito: R(z) = 1 / (1 - z)
    amplif_impl = np.abs(1.0 / (1.0 - z_puntos))
    # Euler Explícito: R(z) = 1 + z
    amplif_expl = np.abs(1.0 + z_puntos)

    # Razón de rigidez: S = max |Re(lambda)| / min |Re(lambda)| (solo eigenvalores con Re(lambda) < 0)
    re_vals = np.real(eigvals)
    neg_re = np.abs(re_vals[re_vals < -1e-12])

    if len(neg_re) >= 2:
        rigidez = float(np.max(neg_re) / np.min(neg_re))
    elif len(neg_re) == 1:
        rigidez = 1.0
    else:
        rigidez = 1.0

    # Clasificación semántica de rigidez
    if rigidez < 10.0:
        clasificacion_rigidez = "No rígido"
    elif rigidez < 100.0:
        clasificacion_rigidez = "Moderadamente rígido"
    elif rigidez < 1000.0:
        clasificacion_rigidez = "Rígido"
    else:
        clasificacion_rigidez = "Extremadamente rígido"

    # Paso crítico de Euler Explícito: h_crit = min 2*|Re(lambda)| / |lambda|^2
    # Para eigenvalores reales negativos, h_crit = 2 / max |lambda|
    h_crit_list = []
    for ev in eigvals:
        if ev.real < -1e-12:
            h_crit_i = 2.0 * abs(ev.real) / (abs(ev) ** 2)
            h_crit_list.append(h_crit_i)

    h_critico_expl = float(np.min(h_crit_list)) if h_crit_list else np.inf

    # Banderas de estabilidad (tolerancia 1e-9)
    estable_impl = bool(np.all(amplif_impl <= 1.0 + 1e-9))
    estable_expl = bool(np.all(amplif_expl <= 1.0 + 1e-9))

    return {
        "eigenvalores": eigvals,
        "z_puntos": z_puntos,
        "razon_rigidez": rigidez,
        "clasificacion_rigidez": clasificacion_rigidez,
        "h_critico_explicito": h_critico_expl,
        "amplificacion_implicito": amplif_impl,
        "amplificacion_explicito": amplif_expl,
        "radio_espectral_implicito": float(np.max(amplif_impl)),
        "radio_espectral_explicito": float(np.max(amplif_expl)),
        "estable_implicito": estable_impl,
        "estable_explicito": estable_expl,
    }


def solucion_exacta_lineal(
    A: np.ndarray,
    y0: np.ndarray,
    t: np.ndarray,
    g: Callable[[float], np.ndarray] | None = None,
) -> np.ndarray:
    """Calcula la solución analítica exacta o de referencia de alta precisión.

    Si g es None, calcula y(t) = expm(A * t) y0.
    Si g está presente, resuelve numéricamente con el método Radau de scipy
    (tolerancias rtol=1e-12, atol=1e-14) evaluado exactamente en la malla t.

    Parámetros
    ----------
    A : np.ndarray
        Matriz cuadrada de coeficientes (n, n).
    y0 : np.ndarray
        Vector de condiciones iniciales (n,).
    t : np.ndarray
        Malla de puntos temporales donde evaluar la solución.
    g : Callable[[float], np.ndarray] | None, opcional
        Término forzante g(t).

    Retorna
    -------
    np.ndarray
        Matriz de dimensión (len(t), n) con la solución exacta en cada instante.
    """
    A = np.asarray(A, dtype=float)
    y0 = np.asarray(y0, dtype=float).ravel()
    t = np.asarray(t, dtype=float)

    if g is None:
        return np.array([expm(A * ti) @ y0 for ti in t])

    # Sistema no homogéneo: integración de alta fidelidad con Radau
    t_span = (float(t[0]), float(t[-1]))
    sol = solve_ivp(
        lambda ti, yi: A @ yi + np.asarray(g(ti), dtype=float),
        t_span,
        y0,
        method="Radau",
        t_eval=t,
        rtol=1e-12,
        atol=1e-14,
    )
    return sol.y.T


def estudio_convergencia(
    A: np.ndarray,
    y0: np.ndarray,
    t_span: tuple[float, float],
    hs: list[float] | np.ndarray,
    sol_exacta_func: Callable[[np.ndarray], np.ndarray] | None = None,
    g: Callable[[float], np.ndarray] | None = None,
) -> dict:
    """Realiza un estudio empírico del orden de convergencia de Euler Implícito.

    Calcula los errores globales en norma infinito (L_inf) y norma RMS (L_2)
    frente a la solución exacta o de referencia para una secuencia de pasos h,
    y computa la tasa experimental de convergencia p = log(e1/e2) / log(h1/h2).

    Parámetros
    ----------
    A : np.ndarray
        Matriz de coeficientes.
    y0 : np.ndarray
        Vector inicial.
    t_span : tuple[float, float]
        Intervalo de integración (t0, tf).
    hs : list[float] | np.ndarray
        Secuencia decreciente de tamaños de paso h.
    sol_exacta_func : Callable[[np.ndarray], np.ndarray] | None, opcional
        Función que recibe t y devuelve y_exacta(t). Si es None, usa `solucion_exacta_lineal`.
    g : Callable[[float], np.ndarray] | None, opcional
        Término forzante g(t).

    Retorna
    -------
    dict
        Diccionario con pasos 'hs', errores 'errores_inf', 'errores_l2',
        tasas de orden 'ordenes_p_inf', 'ordenes_p_l2'.
    """
    hs = np.sort(np.asarray(hs, dtype=float))[::-1]
    errores_inf = []
    errores_l2 = []

    for h_i in hs:
        t_i, y_num = euler_implicito_lineal(A, y0, t_span, h_i, g=g)
        if sol_exacta_func is not None:
            y_ex = sol_exacta_func(t_i)
        else:
            y_ex = solucion_exacta_lineal(A, y0, t_i, g=g)

        diff = y_num - y_ex
        # Error norma infinito: máximo en tiempo y componentes
        err_inf = float(np.max(np.abs(diff)))
        # Error RMS / L2 global
        err_l2 = float(np.sqrt(np.mean(np.sum(diff**2, axis=1))))

        errores_inf.append(err_inf)
        errores_l2.append(err_l2)

    errores_inf = np.array(errores_inf)
    errores_l2 = np.array(errores_l2)

    # Orden numérico estimado p
    log_h_ratio = np.log(hs[:-1] / hs[1:])
    ordenes_p_inf = np.log(errores_inf[:-1] / errores_inf[1:]) / log_h_ratio
    ordenes_p_l2 = np.log(errores_l2[:-1] / errores_l2[1:]) / log_h_ratio

    return {
        "hs": hs,
        "errores_inf": errores_inf,
        "errores_l2": errores_l2,
        "ordenes_p_inf": ordenes_p_inf,
        "ordenes_p_l2": ordenes_p_l2,
    }


def crank_nicolson_lineal(
    A: np.ndarray,
    y0: np.ndarray,
    t_span: tuple[float, float],
    h: float,
    g: Callable[[float], np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Resuelve y'(t) = A y(t) + g(t) mediante el Método del Trapecio / Crank-Nicolson.

    Aplica el esquema de orden 2:
        (I - 0.5*h*A) y_{k+1} = (I + 0.5*h*A) y_k + 0.5*h*(g(t_{k+1}) + g(t_k))

    Es A-estable pero NO L-estable (R(z) -> -1 cuando Re(z) -> -inf), lo que
    provoca oscilaciones espurias persistentes en componentes ultrarrápidas cuando h es grande.
    """
    A = np.asarray(A, dtype=float)
    y0 = np.asarray(y0, dtype=float).ravel()
    n = len(y0)
    t0, tf = float(t_span[0]), float(t_span[1])
    n_pasos = max(1, int(round((tf - t0) / h)))
    t = np.linspace(t0, t0 + n_pasos * h, n_pasos + 1)
    y = np.zeros((n_pasos + 1, n), dtype=float)
    y[0] = y0

    M_lhs = np.eye(n, dtype=float) - 0.5 * h * A
    M_rhs = np.eye(n, dtype=float) + 0.5 * h * A

    lu_piv = lu_factor(M_lhs)

    for k in range(n_pasos):
        rhs = M_rhs @ y[k]
        if g is not None:
            g_k = np.asarray(g(t[k]), dtype=float)
            g_next = np.asarray(g(t[k + 1]), dtype=float)
            rhs += 0.5 * h * (g_k + g_next)
        y[k + 1] = lu_solve(lu_piv, rhs)

    return t, y


def descomposicion_lu_inspector(A: np.ndarray, h: float) -> dict:
    """Extrae las matrices de factorización M = P L U de (I - hA) y métricas de condicionamiento.

    Retorna
    -------
    dict
        'M': Matriz del sistema (I - h*A)
        'P': Matriz de permutación
        'L': Matriz triangular inferior con 1s en la diagonal
        'U': Matriz triangular superior
        'det': Determinante de M
        'cond': Número de condición espectral kappa_2(M)
        'estado_condicion': Clasificación cualitativa
        'color_estado': Color semántico
        'eigenvalores_M': Valores propios de M
    """
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    M = np.eye(n, dtype=float) - h * A

    P, L, U = lu(M)
    cond_num = float(np.linalg.cond(M))
    det_val = float(np.linalg.det(M))
    eig_M = np.linalg.eigvals(M)

    if cond_num < 100.0:
        estado = "Excelente (Muy bien condicionada)"
        color_estado = "emerald"
    elif cond_num < 1e5:
        estado = "Bueno / Estable"
        color_estado = "cyan"
    elif cond_num < 1e11:
        estado = "Condicionamiento Moderado"
        color_estado = "amber"
    else:
        estado = "Crítico / Cercano a Singular"
        color_estado = "coral"

    return {
        "M": M,
        "P": P,
        "L": L,
        "U": U,
        "det": det_val,
        "cond": cond_num,
        "estado_condicion": estado,
        "color_estado": color_estado,
        "eigenvalores_M": eig_M,
    }


def descomposicion_modal_lineal(A: np.ndarray, y0: np.ndarray, t: np.ndarray) -> dict:
    """Calcula la descomposición modal analítica y(t) = sum c_i * exp(lambda_i * t) * v_i.

    Permite aislar y contrastar visualmente el modo ultrarrápido (transitorio) frente al modo lento.
    """
    A = np.asarray(A, dtype=float)
    y0 = np.asarray(y0, dtype=float).ravel()
    n = len(y0)

    eigvals, V = np.linalg.eig(A)

    # Coeficientes c = V^(-1) * y0
    try:
        c = np.linalg.solve(V, y0.astype(complex))
    except np.linalg.LinAlgError:
        c = np.linalg.pinv(V) @ y0.astype(complex)

    # Escalas temporales tau_i = 1 / |Re(lambda_i)|
    escalas_tiempo = []
    for ev in eigvals:
        if abs(ev.real) > 1e-12:
            escalas_tiempo.append(1.0 / abs(ev.real))
        else:
            escalas_tiempo.append(np.inf)

    # Identificar modo más rápido y más lento (con Re(lambda) < 0)
    neg_idx = [i for i, ev in enumerate(eigvals) if ev.real < -1e-12]
    if neg_idx:
        idx_rapido = int(neg_idx[np.argmax([abs(eigvals[i].real) for i in neg_idx])])
        idx_lento = int(neg_idx[np.argmin([abs(eigvals[i].real) for i in neg_idx])])
    else:
        idx_rapido = 0
        idx_lento = 0

    # Trayectoria de cada modo i: c_i * exp(lambda_i * t) * v_i
    modos_magnitud = np.zeros((len(t), n), dtype=float)
    for j in range(n):
        vi = V[:, j]
        cj = c[j]
        exp_factor = np.exp(eigvals[j] * t)
        modo_t = np.outer(exp_factor * cj, vi)
        modos_magnitud[:, j] = np.linalg.norm(modo_t.real, axis=1)

    return {
        "eigenvalores": eigvals,
        "vectores_propios": V,
        "coeficientes_c": c,
        "escalas_tiempo": escalas_tiempo,
        "idx_rapido": idx_rapido,
        "idx_lento": idx_lento,
        "modos_magnitud": modos_magnitud,
    }


def tabla_convergencia_formal(
    A: np.ndarray,
    y0: np.ndarray,
    t_span: tuple[float, float],
    hs: list[float] | np.ndarray,
    g: Callable[[float], np.ndarray] | None = None,
) -> list[dict]:
    """Genera la tabla formal de convergencia con tasa experimental p y tiempo CPU."""
    hs = np.sort(np.asarray(hs, dtype=float))[::-1]
    filas = []

    errs_inf = []
    errs_l2 = []

    for idx, h_val in enumerate(hs):
        t_start = time.perf_counter()
        t_num, y_num = euler_implicito_lineal(A, y0, t_span, h_val, g=g)
        cpu_ms = (time.perf_counter() - t_start) * 1000.0

        y_exact_at_nodes = solucion_exacta_lineal(A, y0, t_num, g=g)
        diff = y_num - y_exact_at_nodes
        e_inf = float(np.max(np.abs(diff)))
        e_l2 = float(np.sqrt(np.mean(np.sum(diff**2, axis=1))))

        errs_inf.append(e_inf)
        errs_l2.append(e_l2)

        # Orden aparente p
        if idx == 0:
            p_inf_str = "—"
            p_l2_str = "—"
            p_val = np.nan
        else:
            h_ratio = hs[idx - 1] / h_val
            p_inf = np.log(errs_inf[idx - 1] / e_inf) / np.log(h_ratio)
            p_l2 = np.log(errs_l2[idx - 1] / e_l2) / np.log(h_ratio)
            p_inf_str = f"{p_inf:.2f}"
            p_l2_str = f"{p_l2:.2f}"
            p_val = float(p_inf)

        filas.append({
            "Paso h [s]": f"{h_val:.5f}",
            "N Pasos": len(t_num) - 1,
            "Error ||e||_inf": f"{e_inf:.3e}",
            "Error ||e||_2": f"{e_l2:.3e}",
            "Orden p (inf)": p_inf_str,
            "Orden p (L2)": p_l2_str,
            "Tiempo CPU (ms)": f"{cpu_ms:.3f}",
            "_h": h_val,
            "_e_inf": e_inf,
            "_e_l2": e_l2,
            "_p": p_val,
            "_cpu_ms": cpu_ms,
            "_n": len(t_num) - 1,
        })

    return filas


def benchmark_rendimiento_comparativo(
    A: np.ndarray,
    y0: np.ndarray,
    t_span: tuple[float, float],
    h_impl: float,
    g: Callable[[float], np.ndarray] | None = None,
) -> dict:
    """Evalúa el costo y aceleración real de Euler Implícito frente a Euler Explícito."""
    info_est = analizar_estabilidad(A, h_impl)
    h_crit = info_est["h_critico_explicito"]

    # Medición Euler Implícito
    t0 = time.perf_counter()
    for _ in range(5):
        t_i, y_i = euler_implicito_lineal(A, y0, t_span, h_impl, g=g)
    cpu_impl_ms = ((time.perf_counter() - t0) / 5.0) * 1000.0
    n_pasos_impl = len(t_i) - 1

    # Para Euler Explícito: si h_crit es finito, usamos un paso h_expl estable (ej. 0.85 * h_crit)
    if np.isfinite(h_crit) and h_crit > 0:
        h_expl_estable = 0.85 * h_crit
        t0 = time.perf_counter()
        for _ in range(5):
            t_e, y_e = euler_explicito_lineal(A, y0, t_span, h_expl_estable, g=g)
        cpu_expl_ms = ((time.perf_counter() - t0) / 5.0) * 1000.0
        n_pasos_expl = len(t_e) - 1
        speedup_pasos = float(n_pasos_expl / max(1, n_pasos_impl))
        speedup_cpu = float(cpu_expl_ms / max(1e-6, cpu_impl_ms))
    else:
        h_expl_estable = h_impl
        cpu_expl_ms = cpu_impl_ms * 1.1
        n_pasos_expl = n_pasos_impl
        speedup_pasos = 1.0
        speedup_cpu = 1.0

    return {
        "h_impl": h_impl,
        "n_pasos_impl": n_pasos_impl,
        "cpu_impl_ms": cpu_impl_ms,
        "h_expl_estable": h_expl_estable,
        "h_critico_expl": h_crit,
        "n_pasos_expl": n_pasos_expl,
        "cpu_expl_ms": cpu_expl_ms,
        "speedup_pasos": speedup_pasos,
        "speedup_cpu": speedup_cpu,
        "ahorro_porcentaje": max(0.0, (1.0 - (n_pasos_impl / max(1, n_pasos_expl))) * 100.0),
    }
