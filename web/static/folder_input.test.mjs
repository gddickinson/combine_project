// Node test for folder_input.js: the drag-and-drop walker (mocked FileSystem entries), the folder-button list, and the
// test tree, each fed through the engine must give the Python output for the fixture tree. Run: node folder_input.test.mjs
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileText, plan, renderCombined, renderStructure } from './combine_engine.js';
import { fromDemo, fromDrop, fromFileList } from './folder_input.js';

const fx = JSON.parse(readFileSync(new URL('../../tests/fixtures/combine_fixture.json', import.meta.url), 'utf8'));
const blobs = new Map(fx.tree.files.map(f => [f.path, new Blob([Buffer.from(f.b64, 'base64')])]));

// Build a mock directory entry tree (readEntries returns children in two batches, like Chrome's 100-entry pages).
function dirEntry(name, prefix) {
  const kids = new Map();
  for (const p of [...blobs.keys(), ...fx.tree.dirs.map(d => d + '/')]) {
    if (prefix && !p.startsWith(prefix + '/')) continue;
    const rest = prefix ? p.slice(prefix.length + 1) : p, head = rest.split('/')[0];
    if (!head) continue;
    const full = prefix ? prefix + '/' + head : head;
    kids.set(head, rest.includes('/') ? dirEntry(head, full) : { name: head, isDirectory: false, file: ok => ok(blobs.get(full)) });
  }
  const list = [...kids.values()];
  return { name, isDirectory: true, createReader() {
    let calls = 0;
    return { readEntries(ok) { const c = calls++; ok(c === 0 ? list.slice(0, 3) : c === 1 ? list.slice(3) : []); } };
  } };
}

async function run(project) {
  const byPath = new Map(project.files.map(f => [f.path, f.file]));
  const planned = plan(project.name, [...byPath.keys()], project.dirs, fx.rules);
  const texts = new Map();
  for (const p of planned.included) texts.set(p, fileText(new Uint8Array(await byPath.get(p).arrayBuffer())));
  return { combined: renderCombined(project.name, planned, texts, fx.generated), structure: renderStructure(project.name, planned, fx.generated) };
}

const dt = { items: [{ kind: 'file', webkitGetAsEntry: () => dirEntry(fx.tree.name, '') }] };
const dropped = await fromDrop(dt, fx.rules);
assert.ok(!dropped.files.some(f => f.path.startsWith('node_modules/')), 'ignored folders are not walked');
let out = await run(dropped);
assert.equal(out.combined, fx.combined); assert.equal(out.structure, fx.structure);
console.log('ok drop: identical to Python');

await assert.rejects(fromDrop({ items: [{ kind: 'file', webkitGetAsEntry: () => ({ isDirectory: false }) }] }, fx.rules));
console.log('ok drop: loose files rejected');

const list = [...blobs].map(([p, b]) => Object.assign(b, { webkitRelativePath: fx.tree.name + '/' + p }));
const picked = fromFileList(list, fx.rules);
out = await run(picked);
assert.equal(out.combined, fx.combined);
assert.equal(out.structure, fx.structure.replace('├── empty_dir/\n', '').replace('│   ├── empty_sub/\n', ''));
console.log('ok folder button: identical except empty folders (browsers do not list them)');

out = await run(fromDemo(fx));
assert.equal(out.combined, fx.combined); assert.equal(out.structure, fx.structure);
console.log('ok test tree: identical to Python');
