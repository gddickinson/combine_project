// Static-site data layer: answers api() calls from the JSON exported by scripts/build_static.py (rules and the test
// tree with its Python output). The combining itself always runs in the browser (combine_engine.js).
const files = new Map();
async function file(rel) {
  if (!files.has(rel)) files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  return files.get(rel);
}

export async function staticApi(path) {
  return file(path.split('?')[0].replace(/^\/+/, ''));
}
