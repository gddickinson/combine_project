// Entry point: lazy page modules, the mode label, a subtle background of drifting lines, then the router.
import { $, app, isStatic, lazy, route, start } from './core.js';

const PAGES = { 'home.js': ['home'], 'combine.js': ['combine'], 'rules.js': ['rules'], 'about.js': ['about'] };
lazy(Object.fromEntries(Object.entries(PAGES).flatMap(([file, names]) => names.map(n => [n, () => import('./' + file)]))));
route('notfound', () => { app().innerHTML = '<h1>Not found</h1><p><a href="#/">Back to the start</a></p>'; });

$('#mode').textContent = isStatic()
  ? 'static site: combining runs in your browser, files never leave your device'
  : 'local app: combining runs in your browser, files never leave your device';

// Background: short "lines of text" drifting right and merging into one column. Off under prefers-reduced-motion.
function background(canvas) {
  if (!canvas || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const g = canvas.getContext('2d');
  const fit = () => { canvas.width = innerWidth; canvas.height = innerHeight; };
  fit(); addEventListener('resize', fit);
  const cols = ['#ffb347', '#b28cff', '#5ce1e6'];
  const ls = Array.from({ length: 26 }, (_, i) => ({ x: Math.random(), y: Math.random(), w: 20 + Math.random() * 60, c: cols[i % 3], v: 0.0006 + Math.random() * 0.0012 }));
  let last = 0;
  const tick = t => {
    requestAnimationFrame(tick);
    if (document.hidden || t - last < 50) return;
    last = t;
    g.clearRect(0, 0, canvas.width, canvas.height);
    for (const l of ls) {
      l.x += l.v; l.y += (0.5 - l.y) * l.v * 0.8;
      if (l.x > 1.05) { l.x = -0.05; l.y = Math.random(); }
      g.globalAlpha = 0.5; g.strokeStyle = l.c; g.lineWidth = 2;
      g.beginPath(); g.moveTo(l.x * canvas.width, l.y * canvas.height); g.lineTo(l.x * canvas.width + l.w, l.y * canvas.height); g.stroke();
    }
  };
  requestAnimationFrame(tick);
}
background($('#bg'));
start();
