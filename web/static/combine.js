// Combine page: pick or drop a folder, run the JS port of ProjectCombiner, preview and download both files.
import { $, $$, api, app, download, esc, list, route } from './core.js';
import { fileText, plan, renderCombined, renderStructure, timestamp } from './combine_engine.js';
import { fromDemo, fromDrop, fromFileList } from './folder_input.js';

const PREVIEW_CHARS = 300000;  // longer outputs are previewed in part; downloads are always complete
let result = null, tab = 'combined';

route('combine', async () => {
  const { rules } = await api('/info');
  app().innerHTML = `
  <p class="kicker">The tool</p>
  <h1 class="glow">Combine a project</h1>
  <p class="lead">Choose your project folder. The two files <code>combine_project.py</code> would write,
    <b>COMBINED_PROJECT.txt</b> and <b>PROJECT_STRUCTURE.txt</b>, are built here in your browser with the same rules
    and formatting.</p>
  <div class="drop panel" id="drop">
    <p>Drag a project folder here, or</p>
    <span class="pick"><input type="file" id="dir" webkitdirectory directory multiple><label for="dir" class="btn">Choose a folder</label></span>
    <button class="alt" id="demo" type="button">Try the test tree</button>
    <p class="privacy">Files never leave your device: nothing is uploaded, the page reads them locally.</p>
  </div>
  <p class="status" id="status" role="status" aria-live="polite"></p>
  <div id="out"></div>`;

  const status = t => { $('#status').textContent = t; };
  const runSafe = async fn => {
    try { await fn(); } catch (e) { console.warn(e); status(''); $('#out').innerHTML = `<p class="err">${esc(e.message)}</p>`; }
  };
  $('#dir').addEventListener('change', e => runSafe(async () => {
    if (!e.target.files.length) return;
    status('Reading folder...');
    await process(fromFileList(e.target.files, rules), rules, status);
    e.target.value = '';
  }));
  $('#demo').addEventListener('click', () => runSafe(async () => {
    status('Loading the test tree...');
    const demo = await api('/demo');
    await process(fromDemo(demo), rules, status, demo);
  }));
  const drop = $('#drop');
  drop.addEventListener('dragover', e => { e.preventDefault(); drop.classList.add('over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('over'));
  drop.addEventListener('drop', e => {
    e.preventDefault(); drop.classList.remove('over');
    runSafe(async () => {
      status('Reading folder...');
      await process(await fromDrop(e.dataTransfer, rules, n => status(`Reading folder... ${n} files`)), rules, status);
    });
  });
  if (result) show();
});

async function process(project, rules, status, demo = null) {
  const byPath = new Map(project.files.map(f => [f.path, f.file]));
  const planned = plan(project.name, [...byPath.keys()], project.dirs, rules);
  status(`Reading ${planned.included.length} files...`);
  const texts = new Map();
  for (const p of planned.included) {
    try { texts.set(p, fileText(new Uint8Array(await byPath.get(p).arrayBuffer()))); }
    catch (e) { texts.set(p, `[Error reading file: ${e.message}]\n`); }
  }
  const generated = demo ? demo.generated : timestamp();
  const combined = renderCombined(project.name, planned, texts, generated);
  const structure = renderStructure(project.name, planned, generated);
  const sizes = new Map(planned.included.map(p => [p, byPath.get(p).size]));
  result = { project, planned, combined, structure, sizes, demo, seen: project.files.length };
  status('');
  show();
}

const bytes = s => new TextEncoder().encode(s).length;
const kb = n => n < 1024 ? `${n} B` : n < 1048576 ? `${(n / 1024).toFixed(1)} KB` : `${(n / 1048576).toFixed(2)} MB`;

function show() {
  const { project, planned, combined, structure, sizes, demo, seen } = result;
  const verdict = demo ? (combined === demo.combined && structure === demo.structure
    ? '<p class="verdict ok">Identical, byte for byte, to the files the Python code wrote for this tree (time stamp fixed to the one Python used).</p>'
    : '<p class="verdict err">Differs from the Python output for this tree: please report this.</p>') : '';
  $('#out').innerHTML = `
  <h2>${esc(project.name)}/</h2>
  ${demo ? '<p class="small mute">The test tree is a small made-up project from <code>web/fixture_tree.py</code> that exercises every include/exclude rule.</p>' : ''}
  ${verdict}
  <div class="tiles">
    <div class="tile"><b>${planned.total}</b><span>files combined</span></div>
    <div class="tile"><b>${seen}</b><span>files seen (outside ignored folders)</span></div>
    <div class="tile"><b>${planned.treeLines.length - 1}</b><span>entries in the tree</span></div>
    <div class="tile"><b>${kb(bytes(combined))}</b><span>COMBINED_PROJECT.txt</span></div>
  </div>
  ${planned.total ? '' : '<p class="callout">No files matched the include rules (see the Rules page).</p>'}
  ${project.emptyDirsKnown ? '' : '<p class="small mute">Picked with the folder button: browsers do not report empty folders that way, so they are missing from the tree. Drag the folder in to include them.</p>'}
  <div class="actions">
    <span class="label">Download</span>
    <button id="dl-c" type="button">COMBINED_PROJECT.txt</button><button id="dl-s" type="button">PROJECT_STRUCTURE.txt</button>
  </div>
  <div class="actions">
    <span class="label">Copy</span>
    <button class="alt" id="cp-c" type="button">Combined text</button><button class="alt" id="cp-s" type="button">Structure text</button>
    <span class="small mute" id="cp-msg" role="status" aria-live="polite"></span>
  </div>
  <h2>Preview</h2>
  <div class="seg" role="tablist" aria-label="Preview">
    ${list([['combined', 'Combined'], ['structure', 'Structure'], ['files', 'Included files']],
      ([k, t]) => `<button type="button" role="tab" data-tab="${k}" aria-selected="${tab === k}" class="${tab === k ? 'on' : ''}">${t}</button>`)}
  </div>
  <div id="pv"></div>`;
  $('#dl-c').onclick = () => download('COMBINED_PROJECT.txt', combined, 'text/plain;charset=utf-8');
  $('#dl-s').onclick = () => download('PROJECT_STRUCTURE.txt', structure, 'text/plain;charset=utf-8');
  const copy = async (text, what) => {
    try { await navigator.clipboard.writeText(text); $('#cp-msg').textContent = `${what} copied.`; }
    catch { $('#cp-msg').textContent = 'Copy is blocked here: use the download buttons.'; }
  };
  $('#cp-c').onclick = () => copy(combined, 'Combined text');
  $('#cp-s').onclick = () => copy(structure, 'Structure text');
  $$('[data-tab]').forEach(b => b.addEventListener('click', () => { tab = b.dataset.tab; show(); }));
  const pv = $('#pv');
  if (tab === 'files') {
    pv.innerHTML = `<div class="scroll"><table class="files"><thead><tr><th>#</th><th>File (in output order)</th><th>Size</th></tr></thead><tbody>
      ${list(planned.included, (p, i) => `<tr><td class="n">${i + 1}</td><td>${esc(p)}</td><td class="n">${kb(sizes.get(p))}</td></tr>`)}</tbody></table></div>`;
  } else {
    const text = tab === 'combined' ? combined : structure;
    const cut = text.length > PREVIEW_CHARS;
    pv.innerHTML = `${cut ? `<p class="small mute">Showing the first ${PREVIEW_CHARS.toLocaleString()} of ${text.length.toLocaleString()} characters; the download has everything.</p>` : ''}
      <pre class="preview" tabindex="0" aria-label="${tab} file preview">${esc(cut ? text.slice(0, PREVIEW_CHARS) : text)}</pre>`;
  }
}
