# Resolución de Sistemas de EDOs Lineales mediante el Método de Euler Implícito

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36%2B-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=flat&logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-1.10%2B-8CAAE6?style=flat&logo=scipy&logoColor=white)](https://scipy.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.22%2B-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Universidad Mayor de San Andrés (UMSA)**  
> Facultad de Ciencias Puras y Naturales — Carrera de Informática  
> **Materia:** Métodos Numéricos II  
> **Docente:** M.Sc. Carlos Mullisaca Choque  
> **Estudiante:** Cordova Avendaño Yoshua Aaron  

---

## Descripción del Proyecto

Este repositorio contiene la implementación matemática, computacional y visual de un motor numérico de alto rendimiento para resolver **Sistemas de Ecuaciones Diferenciales Ordinarias (EDOs) Lineales** con problemas de **rigidez numérica (*stiffness*)** utilizando el **Método de Euler Implícito (*Backward Euler*)**.

Incluye:
1. **Motor Numérico Reutilizable (`core/euler_implicito.py`)**: Factorización LU precomputada ($O(n^2)$ por paso), análisis espectral de rigidez ($S$), convergencia $O(h)$ y comparación directa con Euler Explícito.
2. **Tres Casos Físicos de Estudio (`ejercicios/`)**:
   - **Circuito RLC Rígido ($2 \times 2$):** Razón de rigidez $S = 1000$, demostrando la explosión numérica de Euler Explícito frente a la estabilidad incondicional de Euler Implícito.
   - **Cinética Química en Cadena $A \to B \to C$ ($3 \times 3$):** Reacciones rápidas y lentas acopladas con verificación de conservación de masa $\sum y_i(t) = y_A(0)$.
   - **Dinámica Sísmica de un Edificio de 2 Pisos ($4 \times 4$):** Sistema no homogéneo forzado con aceleración basal armónica y retratos de fase.
3. **Dashboard Científico Interactivo `EulerLab` (`dashboard/app.py`)**:
   - Diseño responsivo en tema oscuro científico.
   - Animación matemática fluida paso a paso inspirada en Manim.
   - Simulaciones visuales interactivas a 60 FPS en HTML5 Canvas para cada sistema físico.
   - Laboratorio del plano complejo $z = h\lambda$ para explorar la región de estabilidad incondicional.
   - Galería de gráficos estáticos a 300 DPI y animaciones GIF generadas.
4. **Informe Académico en LaTeX (`informe.tex` / `informe.pdf`)**: Documento formal de 7 páginas con rigor teórico, demostraciones analíticas y tablas de convergencia.

---

## Fundamento Matemático

El sistema lineal general de primer orden con valor inicial (PVI) es:

$$\mathbf{y}'(t) = A\mathbf{y}(t) + \mathbf{g}(t), \qquad \mathbf{y}(t_0) = \mathbf{y}_0$$

donde $\mathbf{y}(t) \in \mathbb{R}^n$, $A \in \mathbb{R}^{n \times n}$ y $\mathbf{g}(t) \in \mathbb{R}^n$ es el forzamiento.

### Esquema de Euler Implícito
Discretizando con tamaño de paso $h > 0$ y $t_{k+1} = t_k + h$:

$$\mathbf{y}_{k+1} = \mathbf{y}_k + h\left(A\mathbf{y}_{k+1} + \mathbf{g}(t_{k+1})\right)$$

Reordenando algebraicamente se obtiene un sistema lineal en cada paso:

$$(I - hA)\mathbf{y}_{k+1} = \mathbf{y}_k + h\mathbf{g}(t_{k+1})$$

### Factorización LU Precomputada
Dado que la matriz $M = (I - hA)$ es constante en todo el intervalo cuando $h$ es fijo, se precomputa su factorización $PLU$ una sola vez:

$$PLU = (I - hA) \quad \implies \quad O(n^3) \text{ una sola vez}$$

Cada iteración temporal se resuelve por sustitución progresiva y regresiva en tiempo **$O(n^2)$**:

$$\mathbf{y}_{k+1} = \text{lu\_solve}((P, L, U), \mathbf{y}_k + h\mathbf{g}(t_{k+1}))$$

### A-Estabilidad
La función de estabilidad escalar con $z = h\lambda$ viene dada por:

$$R(z) = \frac{1}{1 - z}$$

Para todo $\text{Re}(z) \le 0$, se cumple estrictamente $|R(z)| \le 1$. La región de estabilidad comprende el exterior del círculo de radio 1 centrado en $z = 1$, abarcando todo el semiplano complejo izquierdo $\mathbb{C}^-$. Además, es **L-estable** pues $\lim_{\text{Re}(z) \to -\infty} |R(z)| = 0$.

---

## Estructura del Repositorio

```text
.
├── core/
│   ├── __init__.py
│   └── euler_implicito.py              # Motor numérico con LU, análisis espectral y convergencia
├── dashboard/
│   ├── app.py                          # Aplicación interactiva Streamlit
│   ├── animaciones.py                  # Componentes Canvas 60fps y animación Manim
│   └── styles.css                      # Estilos personalizados (tema oscuro científico)
├── ejercicios/
│   ├── ejercicio1_circuito_rlc_rigido.py       # Sistema RLC 2x2 rígido
│   ├── ejercicio2_reaccion_quimica_cadena.py   # Cinética 3x3 (A -> B -> C)
│   └── ejercicio3_sismo_edificio_2pisos.py     # Estructura sísmica 4x4
├── figuras/
│   └── LOGOumsa.png                    # Logotipo UMSA para el informe
├── img/
│   ├── ej1_rlc_comparacion.png         # Gráfica alta resolución RLC
│   ├── ej1_rlc_animacion.gif           # Animación GIF RLC
│   ├── ej2_cinetica_quimica.png        # Gráfica alta resolución cinética
│   ├── ej2_cinetica_animacion.gif      # Animación GIF cinética
│   ├── ej3_edificio_sismo.png          # Gráfica alta resolución edificio
│   ├── ej3_edificio_animacion.gif      # Animación GIF edificio
│   └── LOGOumsa.png                    # Escudo UMSA
├── agent.md                            # Especificación técnica del agente
├── design.md                           # Guía de diseño del dashboard
├── informe.tex                         # Código fuente LaTeX del informe técnico
├── informe.pdf                         # Documento compilado de 7 páginas
├── requirements.txt                    # Dependencias del proyecto
└── README.md                           # Documentación principal
```

---

## Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/YoshGreen/Resolucion-de-Sistemas-de-Ecuaciones-Diferenciales-Lineales---Metodo-de-Euler-Implicito.git
cd Resolucion-de-Sistemas-de-Ecuaciones-Diferenciales-Lineales---Metodo-de-Euler-Implicito
```

### 2. Crear y activar entorno virtual (opcional pero recomendado)
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Lanzar el Dashboard Interactivo
```bash
streamlit run dashboard/app.py
```
El observatorio se abrirá automáticamente en tu navegador en `http://localhost:8501`.

### 5. Ejecutar los scripts individuales de los ejercicios
```bash
python ejercicios/ejercicio1_circuito_rlc_rigido.py
python ejercicios/ejercicio2_reaccion_quimica_cadena.py
python ejercicios/ejercicio3_sismo_edificio_2pisos.py
```

---

## Despliegue en la Nube (Streamlit Community Cloud)

El proyecto está 100% optimizado para ejecutarse en **Streamlit Community Cloud**:

1. Ingresa a [share.streamlit.io](https://share.streamlit.io/) e inicia sesión con tu cuenta de GitHub.
2. Haz clic en **"New app"**.
3. Selecciona:
   - **Repository:** `YoshGreen/Resolucion-de-Sistemas-de-Ecuaciones-Diferenciales-Lineales---Metodo-de-Euler-Implicito`
   - **Branch:** `main`
   - **Main file path:** `dashboard/app.py`
4. Haz clic en **"Deploy!"**.
5. ¡Listo! La plataforma detectará `requirements.txt` e iniciará la aplicación en menos de 2 minutos bajo una URL pública segura con certificado SSL.

---

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo de licencia para más detalles.
