"""
Componentes de Animación Fluida (Estilo Manim + Canvas 60fps) para EulerLab
===========================================================================
Provee animaciones interactivas, responsivas y libres de GIFs estáticos:
  1. Derivación animada estilo Manim (TransformMatchingTex con FLIP 60fps).
  2. Animación en vivo del Circuito RLC Rígido (Esquema + Osciloscopio).
  3. Animación en vivo del Reactor Químico A -> B -> C.
  4. Animación en vivo del Edificio de 2 Pisos bajo Sismo.
"""

import json
import numpy as np


def html_manim_inicio() -> str:
    """Retorna HTML5/CSS/JS con burbujas interactivas y fórmula animada estilo Manim."""
    return r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Fraunces:wght@600;800&display=swap" rel="stylesheet">
<style>
  :root{--bg:#0e1a17;--pn:#152823;--ink:#f1ead8;--mu:#a3a58f;--bd:#26413a;--board:#091512;--c1:#3ecf9f;--c2:#ff7a66;--c3:#f4b942;--c4:#38bdf8}
  *{box-sizing:border-box}
  body{margin:0;background:transparent;color:var(--ink);font-family:"DM Sans",system-ui,sans-serif;overflow-x:hidden}
  .wrap{background:var(--pn);border:1.5px solid var(--bd);border-radius:20px;padding:20px 22px}
  .bub{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:4px 0 14px;position:relative}
  .bub:before{content:"";position:absolute;left:12%;right:12%;top:30px;border-top:2px dashed var(--bd);z-index:0}
  .bb{position:relative;z-index:1;background:none;border:0;cursor:pointer;color:var(--ink);font:700 12.5px "DM Sans";display:flex;flex-direction:column;align-items:center;gap:7px;padding:4px}
  .bb i{width:58px;height:58px;border-radius:50%;background:var(--bg);border:2.5px solid var(--bd);display:grid;place-items:center;font:800 20px Fraunces,Georgia,serif;font-style:normal;transition:transform .35s cubic-bezier(.22,1,.36,1),background .3s,border-color .3s,box-shadow .3s;color:var(--ink)}
  .bb:hover i{border-color:var(--c3);transform:translateY(-4px)}
  .bb.on i{background:var(--c3);border-color:var(--c3);color:#12342f;transform:scale(1.12);box-shadow:0 0 20px rgba(244,185,66,.32)}
  .say{padding:12px 16px;border-radius:14px;background:var(--board);border:1px solid var(--bd);color:var(--ink);font-size:14px;line-height:1.55;transition:opacity .25s}
  .say b{color:var(--c3)}
  .head-row{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin:20px 0 4px}
  h3{font:800 20px Fraunces,Georgia,serif;margin:0;color:var(--ink)}
  .pills{display:flex;gap:6px;flex-wrap:wrap}
  .pill{border:1px solid var(--bd);background:var(--board);color:var(--mu);border-radius:999px;padding:4px 10px;font:700 11.5px "DM Sans";cursor:pointer;transition:.2s}
  .pill:hover{border-color:var(--c3);color:var(--ink)}
  .pill.on{background:var(--c3);border-color:var(--c3);color:#12342f}
  .sub{color:var(--mu);font-size:13.5px;margin:0 0 12px}
  .scene{position:relative;height:132px;background:radial-gradient(circle at 50% 50%, #102520 0%, #091512 85%);border:1px solid var(--bd);border-radius:16px;overflow:hidden;display:flex;align-items:center;justify-content:center}
  .tk{position:absolute;top:50%;left:0;white-space:nowrap;font:600 clamp(17px, 2.7vw, 29px) "Cambria Math",Georgia,serif;color:var(--ink);will-change:transform,opacity,color;transform-origin:center center;text-shadow:0 2px 10px rgba(0,0,0,.45)}
  .tk.hl{color:var(--c3);text-shadow:0 0 18px rgba(244,185,66,.35)}
  .tk.em{color:var(--c1);text-shadow:0 0 16px rgba(62,207,159,.3)}
  .pg{height:5px;background:var(--bd);border-radius:9px;margin:12px 0 10px;overflow:hidden}
  .pg i{display:block;height:100%;background:linear-gradient(90deg,var(--c1),var(--c3));transition:width .55s cubic-bezier(.22,1,.36,1)}
  .tool{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:12px}
  .btn{display:inline-flex;align-items:center;gap:6px;border:1px solid transparent;border-radius:99px;padding:8px 16px;font:700 13px "DM Sans";cursor:pointer;background:var(--c2);color:#fff;transition:.2s}
  .btn:hover{filter:brightness(1.1);transform:translateY(-1px)}
  .btn.g{background:var(--board);border-color:var(--bd);color:var(--ink)}
  .btn.g:hover{border-color:var(--c3);color:var(--c3)}
  .svg-i{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
  @media(max-width:640px){
    .wrap{padding:14px}
    .bub{grid-template-columns:repeat(2,1fr);gap:8px}
    .bub:before{display:none}
    .bb i{width:44px;height:44px;font-size:16px}
    .scene{height:112px}
  }
</style>
</head>
<body>
<div class="wrap">
  <div class="bub" id="bub"></div>
  <div class="say" id="bt"></div>

  <div class="head-row">
    <h3>Derivación animada estilo Manim</h3>
    <div class="pills" id="pills"></div>
  </div>
  <p class="sub">Observa cómo cada término matemático se desliza suavemente hacia su nueva posición algebraica.</p>
  <div class="scene" id="scene"></div>
  <div class="pg"><i id="pg"></i></div>
  <div class="say" id="cp"></div>
  <div class="tool">
    <button class="btn g" id="fp"><svg class="svg-i" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>Anterior</button>
    <button class="btn" id="fa"><svg class="svg-i" viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"/></svg><span>Reproducir</span></button>
    <button class="btn g" id="fn">Siguiente<svg class="svg-i" viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg></button>
    <button class="btn g" id="fr"><svg class="svg-i" viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>Reiniciar</button>
  </div>
</div>

<script>
const $=id=>document.getElementById(id);
const B=[
  ['El Problema','Un sistema rígido combina dinámicas ultrarrápidas y lentas al mismo tiempo (como un capacitor rápido y una resistencia alta). Los métodos explícitos se ven obligados a usar pasos minúsculos para no explotar.'],
  ['Idea Implícita','En lugar de usar la pendiente actual, Euler Implícito evalúa la pendiente en el instante futuro k+1. Esa visión hacia adelante actúa como un freno automático que estabiliza la trayectoria.'],
  ['Factorización LU','Al agrupar las incógnitas obtenemos (I − hA)·yₖ₊₁ = yₖ + h·g. Como la matriz (I − hA) no cambia entre pasos, se factoriza en L·U una sola vez y cada iteración se resuelve casi al instante.'],
  ['A y L-Estabilidad','Todo el semiplano complejo izquierdo es estable. Incluso con pasos h enormes frente a la escala rápida, la solución no oscila ni diverge: amortigua los transitorios al instante.']
];
$('bub').innerHTML=B.map((b,i)=>`<button class="bb ${i?'':'on'}" data-b="${i}"><i>${i+1}</i>${b[0]}</button>`).join('');
const sb=i=>{document.querySelectorAll('.bb').forEach((x,j)=>x.classList.toggle('on',j===i));$('bt').innerHTML=`<b>${B[i][0]}.</b> ${B[i][1]}`};
document.querySelectorAll('.bb').forEach(b=>b.onclick=()=>sb(+b.dataset.b));sb(0);

// 6 etapas fluidas estilo Manim TransformMatchingTex
const EQ=[
  [['y_p',"y'(t)",'hl'], ['eq','='], ['A','A'], ['y','·y(t)'], ['p','+'], ['g','g(t)']],
  [['num','(yₖ₊₁ − yₖ)','hl'], ['div','/ h','hl'], ['eq','='], ['A','A'], ['y1','·yₖ₊₁','hl'], ['p','+'], ['g','g(tₖ₊₁)']],
  [['y1','yₖ₊₁'], ['m','−'], ['y0','yₖ'], ['eq','='], ['h','h','hl'], ['A','A'], ['y1b','yₖ₊₁'], ['p','+'], ['hg','h·g(tₖ₊₁)','hl']],
  [['y1','yₖ₊₁'], ['m','−'], ['h','h'], ['A','A'], ['y1b','yₖ₊₁','hl'], ['eq','='], ['y0','yₖ','hl'], ['p','+'], ['hg','h·g(tₖ₊₁)']],
  [['lhs','(I − hA)','hl'], ['y1','yₖ₊₁','em'], ['eq','='], ['y0','yₖ'], ['p','+'], ['hg','h·g(tₖ₊₁)']],
  [['lu','L · U','em'], ['y1','yₖ₊₁','hl'], ['eq','='], ['y0','yₖ'], ['p','+'], ['hg','h·g(tₖ₊₁)']]
];
const CP=[
  'Paso 1 / 6 · Sistema continuo lineal: la tasa de cambio y′(t) acopla todas las variables mediante la matriz A.',
  'Paso 2 / 6 · Discretización regresiva: sustituimos y′ por la diferencia hacia atrás y evaluamos el lado derecho en k+1.',
  'Paso 3 / 6 · Despeje del paso h: multiplicamos toda la ecuación por el tamaño de paso h.',
  'Paso 4 / 6 · Agrupación de incógnitas: pasamos el término h·A·yₖ₊₁ al lado izquierdo de la igualdad.',
  'Paso 5 / 6 · Forma matricial estándar: factorizamos yₖ₊₁ para obtener la matriz constante del sistema M = (I − hA).',
  'Paso 6 / 6 · Descomposición LU: expresamos M como L·U una sola vez; cada avance en el tiempo es una sustitución directa.'
];

$('pills').innerHTML=EQ.map((_,i)=>`<button class="pill ${i?'':'on'}" data-s="${i}">Paso ${i+1}</button>`).join('');

let fs=0,ft=null;
const nodes={};

function layoutStep(s){
  const sc=$('scene');
  const tokens=EQ[s];
  const scW=sc.clientWidth;

  // Medir anchos reales en el DOM de forma invisible
  const meas=document.createElement('div');
  meas.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;display:flex;gap:10px';
  sc.appendChild(meas);
  const widths=tokens.map(t=>{
    const el=document.createElement('span');
    el.className='tk';
    el.style.cssText='position:static;transform:none';
    el.textContent=t[1];
    meas.appendChild(el);
    return el.getBoundingClientRect().width;
  });
  const gap=Math.max(6, Math.min(14, scW * 0.015));
  const totalW=widths.reduce((a,b)=>a+b,0) + gap*(tokens.length-1);
  let cursorX=(scW - totalW)/2;
  meas.remove();

  const activeKeys=new Set();
  tokens.forEach((t,i)=>{
    const [key, text, cls]=t;
    activeKeys.add(key);
    const targetX=cursorX;
    cursorX += widths[i] + gap;

    let el=nodes[key];
    if(!el){
      el=nodes[key]=document.createElement('div');
      el.className='tk' + (cls?' '+cls:'');
      el.textContent=text;
      el.style.opacity='0';
      el.style.transform=`translate3d(${targetX}px, -30%, 0) scale(0.82)`;
      sc.appendChild(el);
      requestAnimationFrame(()=>{
        el.style.transition='transform .75s cubic-bezier(.22,1,.36,1), opacity .55s ease, color .4s ease';
        el.style.opacity='1';
        el.style.transform=`translate3d(${targetX}px, -50%, 0) scale(1)`;
      });
    } else {
      el.textContent=text;
      el.className='tk' + (cls?' '+cls:'');
      el.style.transition='transform .78s cubic-bezier(.22,1,.36,1), opacity .45s ease, color .4s ease';
      el.style.opacity='1';
      el.style.transform=`translate3d(${targetX}px, -50%, 0) scale(1)`;
    }
  });

  Object.keys(nodes).forEach(k=>{
    if(!activeKeys.has(k)){
      const el=nodes[k];
      delete nodes[k];
      el.style.transition='transform .45s ease, opacity .35s ease';
      el.style.opacity='0';
      el.style.transform=el.style.transform.replace('scale(1)','scale(0.75)') + ' translateY(-14px)';
      setTimeout(()=>el.remove(), 480);
    }
  });

  $('cp').textContent=CP[s];
  $('pg').style.width=((s+1)/EQ.length*100)+'%';
  document.querySelectorAll('.pill').forEach((p,idx)=>p.classList.toggle('on',idx===s));
}

function stopAnim(){
  clearInterval(ft);ft=null;
  $('fa').innerHTML='<svg class="svg-i" viewBox="0 0 24 24"><polygon points="6 4 20 12 6 20 6 4"/></svg><span>Reproducir</span>';
}
function setStep(s){fs=Math.max(0,Math.min(EQ.length-1,s));layoutStep(fs)}
$('fa').onclick=()=>{
  if(ft){stopAnim();return}
  if(fs>=EQ.length-1)setStep(0);
  $('fa').innerHTML='<svg class="svg-i" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg><span>Pausar</span>';
  ft=setInterval(()=>{if(fs>=EQ.length-1){stopAnim();return}setStep(fs+1)},2300);
};
$('fp').onclick=()=>{stopAnim();setStep(fs-1)};
$('fn').onclick=()=>{stopAnim();setStep(fs+1)};
$('fr').onclick=()=>{stopAnim();setStep(0)};
document.querySelectorAll('.pill').forEach(p=>p.onclick=()=>{stopAnim();setStep(+p.dataset.s)});
window.addEventListener('resize',()=>layoutStep(fs));
layoutStep(0);
</script>
</body>
</html>
"""


def html_animacion_rlc(
    t_impl: np.ndarray,
    y_impl: np.ndarray,
    t_fine: np.ndarray,
    y_exact: np.ndarray,
    t_expl: np.ndarray,
    y_expl: np.ndarray,
) -> str:
    """Animación Canvas 60fps: Circuito RLC vivo + Osciloscopio sincronizado."""
    payload = {
        "ti": np.round(t_impl, 4).tolist(),
        "vi": np.round(y_impl[:, 0], 4).tolist(),
        "ii": np.round(y_impl[:, 1], 5).tolist(),
        "tf": np.round(t_fine, 4).tolist(),
        "vf": np.round(y_exact[:, 0], 4).tolist(),
        "te": np.round(t_expl, 4).tolist(),
        "ve": [None if np.isnan(v) else round(float(v), 4) for v in y_expl[:, 0]],
    }
    data_json = json.dumps(payload)
    html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  *{box-sizing:border-box}
  body{margin:0;background:transparent;color:#f1ead8;font-family:"DM Sans",system-ui,sans-serif}
  .box{background:#152823;border:1.5px solid #26413a;border-radius:18px;padding:16px}
  canvas{width:100%;height:auto;display:block;background:#091512;border-radius:14px;border:1px solid #26413a}
  .ctrl{display:flex;align-items:center;gap:10px;margin-top:12px;flex-wrap:wrap}
  .btn{border:1px solid #26413a;background:#091512;color:#f1ead8;border-radius:99px;padding:7px 16px;font:700 13px "DM Sans";cursor:pointer;transition:.2s}
  .btn.pri{background:#ff7a66;border-color:#ff7a66;color:#fff}
  .btn:hover{border-color:#f4b942}
  input[type=range]{flex:1;min-width:140px;accent-color:#3ecf9f}
  .stat{font:600 12.5px "JetBrains Mono",monospace;color:#f4b942}
</style>
</head>
<body>
<div class="box">
  <canvas id="cv" width="900" height="360"></canvas>
  <div class="ctrl">
    <button class="btn pri" id="playBtn">Pausar</button>
    <button class="btn" id="rstBtn">Reiniciar</button>
    <input type="range" id="scrubber" min="0" max="1000" value="0">
    <span class="stat" id="lbl">t = 0.00 s | Vc = 10.00 V</span>
  </div>
</div>
<script>
const D = __DATA_JSON__;
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
const sc = document.getElementById('scrubber'), lbl = document.getElementById('lbl');
const playBtn = document.getElementById('playBtn'), rstBtn = document.getElementById('rstBtn');

let prog = 0, playing = true, lastTs = 0;
const tMax = D.ti[D.ti.length - 1];

function interp(tArr, vArr, t){
  if(t <= tArr[0]) return vArr[0];
  if(t >= tArr[tArr.length-1]) return vArr[vArr.length-1];
  for(let i=0; i<tArr.length-1; i++){
    if(t >= tArr[i] && t <= tArr[i+1]){
      const u = (t - tArr[i]) / (tArr[i+1] - tArr[i]);
      const a = vArr[i], b = vArr[i+1];
      if(a === null || b === null) return null;
      return a + u*(b - a);
    }
  }
  return vArr[vArr.length-1];
}

function draw(){
  const W = cv.width, H = cv.height;
  ctx.clearRect(0, 0, W, H);
  const tCur = prog * tMax;
  const vCur = interp(D.ti, D.vi, tCur) ?? 0;
  const iCur = interp(D.ti, D.ii, tCur) ?? 0;

  // Panel izquierdo: Esquema animado del circuito RLC
  ctx.save();
  ctx.strokeStyle = '#26413a';
  ctx.lineWidth = 2;
  ctx.strokeRect(16, 16, 290, H - 32);

  ctx.fillStyle = '#f1ead8';
  ctx.font = '700 14px "DM Sans"';
  ctx.fillText('Circuito RLC en Vivo', 32, 42);

  // Lazo del circuito
  ctx.strokeStyle = '#64748b';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.roundRect(55, 80, 210, 175, 14);
  ctx.stroke();

  // Resistor (arriba)
  ctx.fillStyle = '#091512';
  ctx.fillRect(115, 68, 90, 24);
  ctx.strokeStyle = '#f4b942';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.moveTo(115, 80);
  for(let k=0;k<6;k++) ctx.lineTo(122+k*13, k%2===0?70:90);
  ctx.lineTo(205, 80);
  ctx.stroke();
  ctx.fillStyle = '#f4b942';
  ctx.font = '600 11px "JetBrains Mono"';
  ctx.fillText('R = 1001 Ω', 124, 62);

  // Capacitor (izquierda) con brillo proporcional a Vc
  const glow = Math.max(0, Math.min(1, vCur / 10));
  ctx.fillStyle = '#091512';
  ctx.fillRect(38, 145, 34, 42);
  ctx.strokeStyle = `rgba(62, 207, 159, ${0.35 + 0.65*glow})`;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(38, 156); ctx.lineTo(72, 156);
  ctx.moveTo(38, 176); ctx.lineTo(72, 176);
  ctx.stroke();
  ctx.fillStyle = `rgba(62, 207, 159, ${0.18 + 0.45*glow})`;
  ctx.fillRect(40, 158, 30, 16);
  ctx.fillStyle = '#3ecf9f';
  ctx.fillText(`Vc = ${vCur.toFixed(2)}V`, 28, 206);

  // Inductor (derecha)
  ctx.fillStyle = '#091512';
  ctx.fillRect(252, 130, 24, 70);
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  for(let k=0;k<4;k++) ctx.arc(265, 142+k*15, 7, -Math.PI/2, Math.PI/2);
  ctx.stroke();
  ctx.fillStyle = '#38bdf8';
  ctx.fillText('L = 1H', 240, 222);

  // Partículas de corriente fluyendo
  const phase = (prog * 12) % 1;
  ctx.fillStyle = '#3ecf9f';
  for(let p=0; p<6; p++){
    const u = (p/6 + phase) % 1;
    let px, py;
    if(u < 0.25){ px = 55 + (u/0.25)*210; py = 80; }
    else if(u < 0.5){ px = 265; py = 80 + ((u-0.25)/0.25)*175; }
    else if(u < 0.75){ px = 265 - ((u-0.5)/0.25)*210; py = 255; }
    else { px = 55; py = 255 - ((u-0.75)/0.25)*175; }
    ctx.beginPath();
    ctx.arc(px, py, 3.8, 0, Math.PI*2);
    ctx.fill();
  }

  ctx.fillStyle = '#a3a58f';
  ctx.font = '500 12px "DM Sans"';
  ctx.fillText('Euler Implícito descarga suavemente', 32, 304);
  ctx.fillText('sin oscilaciones numéricas.', 32, 322);
  ctx.restore();

  // Panel derecho: Osciloscopio en vivo
  const ox = 335, oy = 45, ow = W - 360, oh = H - 90;
  ctx.strokeStyle = '#1c332d';
  ctx.lineWidth = 1;
  for(let g=0; g<=4; g++){
    const yy = oy + (oh/4)*g;
    ctx.beginPath(); ctx.moveTo(ox, yy); ctx.lineTo(ox+ow, yy); ctx.stroke();
  }
  const mapX = t => ox + (t / tMax) * ow;
  const mapY = v => oy + oh - ((Math.max(-2, Math.min(11, v)) + 2) / 13) * oh;

  // Exacta (referencia sutil)
  ctx.strokeStyle = 'rgba(241, 234, 216, 0.35)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  D.tf.forEach((t, idx)=>{
    const x = mapX(t), y = mapY(D.vf[idx]);
    if(idx===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
  });
  ctx.stroke();

  // Euler Explícito (divergente al inicio)
  ctx.strokeStyle = '#ff7a66';
  ctx.lineWidth = 2;
  ctx.setLineDash([5,4]);
  ctx.beginPath();
  let started = false;
  D.te.forEach((t, idx)=>{
    if(t <= tCur && D.ve[idx] !== null){
      const x = mapX(t), y = mapY(D.ve[idx]);
      if(!started){ctx.moveTo(x,y); started=true;} else ctx.lineTo(x,y);
    }
  });
  ctx.stroke();
  ctx.setLineDash([]);

  // Euler Implícito (progresiva)
  ctx.strokeStyle = '#3ecf9f';
  ctx.lineWidth = 3;
  ctx.beginPath();
  D.ti.forEach((t, idx)=>{
    if(t <= tCur){
      const x = mapX(t), y = mapY(D.vi[idx]);
      if(idx===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
  });
  ctx.lineTo(mapX(tCur), mapY(vCur));
  ctx.stroke();

  // Punto actual
  ctx.fillStyle = '#f4b942';
  ctx.beginPath();
  ctx.arc(mapX(tCur), mapY(vCur), 6, 0, Math.PI*2);
  ctx.fill();

  // Leyenda
  ctx.font = '700 12px "DM Sans"';
  ctx.fillStyle = '#f1ead8'; ctx.fillText('Exacta', ox+10, 30);
  ctx.fillStyle = '#3ecf9f'; ctx.fillText('● Euler Implícito (Estable)', ox+85, 30);
  ctx.fillStyle = '#ff7a66'; ctx.fillText('--- Euler Explícito (Divergente)', ox+275, 30);

  lbl.textContent = `t = ${tCur.toFixed(2)} s | Vc = ${vCur.toFixed(2)} V | I = ${(iCur*1000).toFixed(2)} mA`;
  sc.value = Math.round(prog * 1000);
}

function loop(ts){
  if(!lastTs) lastTs = ts;
  const dt = (ts - lastTs) / 1000;
  lastTs = ts;
  if(playing){
    prog += dt * 0.16;
    if(prog >= 1) prog = 0;
  }
  draw();
  requestAnimationFrame(loop);
}
playBtn.onclick = ()=>{ playing = !playing; playBtn.textContent = playing ? 'Pausar' : 'Reproducir'; };
rstBtn.onclick = ()=>{ prog = 0; playing = true; playBtn.textContent = 'Pausar'; };
sc.oninput = ()=>{ playing = false; playBtn.textContent = 'Reproducir'; prog = sc.value / 1000; draw(); };
requestAnimationFrame(loop);
</script>
</body>
</html>
"""
    return html.replace("__DATA_JSON__", data_json)


def html_animacion_cinetica(t_impl: np.ndarray, y_impl: np.ndarray) -> str:
    """Animación Canvas 60fps: Reactor Químico A -> B -> C + Curvas en vivo."""
    payload = {
        "t": np.round(t_impl, 4).tolist(),
        "a": np.round(y_impl[:, 0], 5).tolist(),
        "b": np.round(y_impl[:, 1], 6).tolist(),
        "c": np.round(y_impl[:, 2], 5).tolist(),
    }
    data_json = json.dumps(payload)
    html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  *{box-sizing:border-box}
  body{margin:0;background:transparent;color:#f1ead8;font-family:"DM Sans",system-ui,sans-serif}
  .box{background:#152823;border:1.5px solid #26413a;border-radius:18px;padding:16px}
  canvas{width:100%;height:auto;display:block;background:#091512;border-radius:14px;border:1px solid #26413a}
  .ctrl{display:flex;align-items:center;gap:10px;margin-top:12px;flex-wrap:wrap}
  .btn{border:1px solid #26413a;background:#091512;color:#f1ead8;border-radius:99px;padding:7px 16px;font:700 13px "DM Sans";cursor:pointer;transition:.2s}
  .btn.pri{background:#ff7a66;border-color:#ff7a66;color:#fff}
  input[type=range]{flex:1;min-width:140px;accent-color:#3ecf9f}
  .stat{font:600 12.5px "JetBrains Mono",monospace;color:#3ecf9f}
</style>
</head>
<body>
<div class="box">
  <canvas id="cv" width="900" height="350"></canvas>
  <div class="ctrl">
    <button class="btn pri" id="playBtn">Pausar</button>
    <button class="btn" id="rstBtn">Reiniciar</button>
    <input type="range" id="scrubber" min="0" max="1000" value="0">
    <span class="stat" id="lbl">A+B+C = 1.000000</span>
  </div>
</div>
<script>
const D = __DATA_JSON__;
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
const sc = document.getElementById('scrubber'), lbl = document.getElementById('lbl');
const playBtn = document.getElementById('playBtn'), rstBtn = document.getElementById('rstBtn');

let prog = 0, playing = true, lastTs = 0;
const tMax = D.t[D.t.length - 1];

function interp(arr, t){
  if(t <= D.t[0]) return arr[0];
  if(t >= tMax) return arr[arr.length-1];
  for(let i=0; i<D.t.length-1; i++){
    if(t >= D.t[i] && t <= D.t[i+1]){
      const u = (t - D.t[i])/(D.t[i+1]-D.t[i]);
      return arr[i] + u*(arr[i+1]-arr[i]);
    }
  }
  return arr[arr.length-1];
}

function draw(){
  const W = cv.width, H = cv.height;
  ctx.clearRect(0, 0, W, H);
  const tCur = prog * tMax;
  const aV = interp(D.a, tCur), bV = interp(D.b, tCur), cV = interp(D.c, tCur);

  // Panel izquierdo: Barras vivas del reactor
  ctx.strokeStyle = '#26413a'; ctx.lineWidth = 2;
  ctx.strokeRect(16, 16, 285, H - 32);
  ctx.fillStyle = '#f1ead8'; ctx.font = '700 14px "DM Sans"';
  ctx.fillText('Concentraciones en el Reactor', 32, 42);

  const bars = [
    ['[A]', aV, '#38bdf8'],
    ['[B] ×100', Math.min(1, bV*100), '#f4b942'],
    ['[C]', cV, '#3ecf9f']
  ];
  bars.forEach((b, idx)=>{
    const bx = 46 + idx*82, by = 275, bw = 46, maxH = 190;
    ctx.fillStyle = '#152823';
    ctx.fillRect(bx, by - maxH, bw, maxH);
    const bh = Math.max(0, b[1] * maxH);
    ctx.fillStyle = b[2];
    ctx.fillRect(bx, by - bh, bw, bh);
    ctx.fillStyle = '#f1ead8';
    ctx.font = '700 12px "DM Sans"';
    ctx.fillText(b[0], bx+4, by+20);
    ctx.font = '600 11px "JetBrains Mono"';
    ctx.fillText((idx===1 ? (bV*1000).toFixed(2)+'m' : b[1].toFixed(2)), bx+2, by - bh - 6);
  });

  // Panel derecho: Curvas temporales
  const ox = 335, oy = 45, ow = W - 360, oh = H - 85;
  ctx.strokeStyle = '#1c332d'; ctx.lineWidth = 1;
  for(let g=0; g<=4; g++){
    const yy = oy + (oh/4)*g;
    ctx.beginPath(); ctx.moveTo(ox, yy); ctx.lineTo(ox+ow, yy); ctx.stroke();
  }
  const mapX = t => ox + (t/tMax)*ow;
  const mapY = v => oy + oh - Math.max(0, Math.min(1.05, v))*oh/1.05;

  function drawSeries(arr, color, scale){
    ctx.strokeStyle = color; ctx.lineWidth = 2.8;
    ctx.beginPath();
    D.t.forEach((t, idx)=>{
      if(t <= tCur){
        const x = mapX(t), y = mapY(arr[idx]*scale);
        if(idx===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
      }
    });
    const curVal = interp(arr, tCur)*scale;
    ctx.lineTo(mapX(tCur), mapY(curVal));
    ctx.stroke();
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(mapX(tCur), mapY(curVal), 5, 0, Math.PI*2); ctx.fill();
  }
  drawSeries(D.a, '#38bdf8', 1);
  drawSeries(D.b, '#f4b942', 100);
  drawSeries(D.c, '#3ecf9f', 1);

  ctx.font = '700 12px "DM Sans"';
  ctx.fillStyle = '#38bdf8'; ctx.fillText('● [A](t) Reactivo', ox+10, 30);
  ctx.fillStyle = '#f4b942'; ctx.fillText('● [B](t)×100 Intermediario', ox+145, 30);
  ctx.fillStyle = '#3ecf9f'; ctx.fillText('● [C](t) Producto', ox+330, 30);

  lbl.textContent = `t = ${tCur.toFixed(2)} s | Masa A+B+C = ${(aV+bV+cV).toFixed(6)}`;
  sc.value = Math.round(prog*1000);
}

function loop(ts){
  if(!lastTs) lastTs = ts;
  const dt = (ts - lastTs)/1000; lastTs = ts;
  if(playing){ prog += dt*0.14; if(prog>=1) prog=0; }
  draw(); requestAnimationFrame(loop);
}
playBtn.onclick = ()=>{ playing=!playing; playBtn.textContent=playing?'Pausar':'Reproducir'; };
rstBtn.onclick = ()=>{ prog=0; playing=true; playBtn.textContent='Pausar'; };
sc.oninput = ()=>{ playing=false; playBtn.textContent='Reproducir'; prog=sc.value/1000; draw(); };
requestAnimationFrame(loop);
</script>
</body>
</html>
"""
    return html.replace("__DATA_JSON__", data_json)


def html_animacion_edificio(t_impl: np.ndarray, y_impl: np.ndarray, y_ref: np.ndarray) -> str:
    """Animación Canvas 60fps: Estructura 2D del edificio oscilando + traza sísmica."""
    payload = {
        "t": np.round(t_impl, 4).tolist(),
        "x1": np.round(y_impl[:, 0], 4).tolist(),
        "x2": np.round(y_impl[:, 1], 4).tolist(),
        "xr": np.round(y_ref[:, 1], 4).tolist(),
    }
    data_json = json.dumps(payload)
    html = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<style>
  *{box-sizing:border-box}
  body{margin:0;background:transparent;color:#f1ead8;font-family:"DM Sans",system-ui,sans-serif}
  .box{background:#152823;border:1.5px solid #26413a;border-radius:18px;padding:16px}
  canvas{width:100%;height:auto;display:block;background:#091512;border-radius:14px;border:1px solid #26413a}
  .ctrl{display:flex;align-items:center;gap:10px;margin-top:12px;flex-wrap:wrap}
  .btn{border:1px solid #26413a;background:#091512;color:#f1ead8;border-radius:99px;padding:7px 16px;font:700 13px "DM Sans";cursor:pointer;transition:.2s}
  .btn.pri{background:#ff7a66;border-color:#ff7a66;color:#fff}
  input[type=range]{flex:1;min-width:140px;accent-color:#3ecf9f}
  .stat{font:600 12.5px "JetBrains Mono",monospace;color:#f4b942}
</style>
</head>
<body>
<div class="box">
  <canvas id="cv" width="900" height="360"></canvas>
  <div class="ctrl">
    <button class="btn pri" id="playBtn">Pausar</button>
    <button class="btn" id="rstBtn">Reiniciar</button>
    <input type="range" id="scrubber" min="0" max="1000" value="0">
    <span class="stat" id="lbl">t = 0.00 s | x2 = +0.000 m</span>
  </div>
</div>
<script>
const D = __DATA_JSON__;
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
const sc = document.getElementById('scrubber'), lbl = document.getElementById('lbl');
const playBtn = document.getElementById('playBtn'), rstBtn = document.getElementById('rstBtn');

let prog = 0, playing = true, lastTs = 0;
const tMax = D.t[D.t.length - 1];
const maxAbs = Math.max(0.25, ...D.x2.map(Math.abs));

function interp(arr, t){
  if(t <= D.t[0]) return arr[0];
  if(t >= tMax) return arr[arr.length-1];
  for(let i=0; i<D.t.length-1; i++){
    if(t >= D.t[i] && t <= D.t[i+1]){
      const u = (t - D.t[i])/(D.t[i+1]-D.t[i]);
      return arr[i] + u*(arr[i+1]-arr[i]);
    }
  }
  return arr[arr.length-1];
}

function draw(){
  const W = cv.width, H = cv.height;
  ctx.clearRect(0, 0, W, H);
  const tCur = prog * tMax;
  const x1 = interp(D.x1, tCur), x2 = interp(D.x2, tCur);

  // Panel izquierdo: Edificio 2D animado
  ctx.strokeStyle = '#26413a'; ctx.lineWidth = 2;
  ctx.strokeRect(16, 16, 290, H - 32);
  ctx.fillStyle = '#f1ead8'; ctx.font = '700 14px "DM Sans"';
  ctx.fillText('Estructura 2D bajo Sismo', 32, 42);

  const cx = 161, baseY = 300, hFloor = 95, slabW = 110, scale = 190;
  const dx1 = x1 * scale, dx2 = x2 * scale;

  // Suelo
  ctx.strokeStyle = '#64748b'; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.moveTo(45, baseY); ctx.lineTo(275, baseY); ctx.stroke();

  // Columnas flexibles
  ctx.strokeStyle = '#94a3b8'; ctx.lineWidth = 3.5;
  [-slabW/2, slabW/2].forEach(off=>{
    ctx.beginPath();
    ctx.moveTo(cx + off, baseY);
    ctx.lineTo(cx + off + dx1, baseY - hFloor);
    ctx.lineTo(cx + off + dx2, baseY - 2*hFloor);
    ctx.stroke();
  });

  // Losa Piso 1
  ctx.strokeStyle = '#f4b942'; ctx.lineWidth = 10; ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(cx - slabW/2 + dx1, baseY - hFloor);
  ctx.lineTo(cx + slabW/2 + dx1, baseY - hFloor);
  ctx.stroke();

  // Losa Piso 2
  ctx.strokeStyle = '#3ecf9f'; ctx.lineWidth = 10;
  ctx.beginPath();
  ctx.moveTo(cx - slabW/2 + dx2, baseY - 2*hFloor);
  ctx.lineTo(cx + slabW/2 + dx2, baseY - 2*hFloor);
  ctx.stroke();
  ctx.lineCap = 'butt';

  // Panel derecho: Sismograma
  const ox = 335, oy = 45, ow = W - 360, oh = H - 85;
  const midY = oy + oh/2;
  ctx.strokeStyle = '#1c332d'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(ox, midY); ctx.lineTo(ox+ow, midY); ctx.stroke();
  const mapX = t => ox + (t/tMax)*ow;
  const mapY = v => midY - (v/maxAbs)*(oh*0.44);

  // Referencia Radau
  ctx.strokeStyle = 'rgba(241,234,216,0.3)'; ctx.lineWidth = 1.8;
  ctx.beginPath();
  D.t.forEach((t,i)=>{ const x=mapX(t), y=mapY(D.xr[i]); if(i===0)ctx.moveTo(x,y); else ctx.lineTo(x,y); });
  ctx.stroke();

  function trace(arr, col){
    ctx.strokeStyle = col; ctx.lineWidth = 2.5;
    ctx.beginPath();
    D.t.forEach((t,i)=>{ if(t<=tCur){ const x=mapX(t), y=mapY(arr[i]); if(i===0)ctx.moveTo(x,y); else ctx.lineTo(x,y); });
    const curV = interp(arr, tCur);
    ctx.lineTo(mapX(tCur), mapY(curV));
    ctx.stroke();
    ctx.fillStyle = col;
    ctx.beginPath(); ctx.arc(mapX(tCur), mapY(curV), 5, 0, Math.PI*2); ctx.fill();
  }
  trace(D.x1, '#f4b942');
  trace(D.x2, '#3ecf9f');

  ctx.font = '700 12px "DM Sans"';
  ctx.fillStyle = '#f1ead8'; ctx.fillText('Referencia Radau', ox+10, 30);
  ctx.fillStyle = '#f4b942'; ctx.fillText('● Piso 1 x1(t)', ox+145, 30);
  ctx.fillStyle = '#3ecf9f'; ctx.fillText('● Piso 2 x2(t)', ox+265, 30);

  lbl.textContent = `t = ${tCur.toFixed(2)} s | x1 = ${x1>=0?'+':''}${x1.toFixed(3)} m | x2 = ${x2>=0?'+':''}${x2.toFixed(3)} m`;
  sc.value = Math.round(prog*1000);
}

function loop(ts){
  if(!lastTs) lastTs = ts;
  const dt = (ts - lastTs)/1000; lastTs = ts;
  if(playing){ prog += dt*0.14; if(prog>=1) prog=0; }
  draw(); requestAnimationFrame(loop);
}
playBtn.onclick = ()=>{ playing=!playing; playBtn.textContent=playing?'Pausar':'Reproducir'; };
rstBtn.onclick = ()=>{ prog=0; playing=true; playBtn.textContent='Pausar'; };
sc.oninput = ()=>{ playing=false; playBtn.textContent='Reproducir'; prog=sc.value/1000; draw(); };
requestAnimationFrame(loop);
</script>
</body>
</html>
"""
    return html.replace("__DATA_JSON__", data_json)
