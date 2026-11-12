// Turn a picked or dropped folder into { name, files: [{ path, file }], dirs: [path] } with paths relative to the
// folder. Nothing is uploaded: File objects stay in the page and only the files that will be combined are read.
// Ignored and hidden directories are skipped while walking (Python's os.walk prunes them too, and the
// tree never shows them), so a dropped project with node_modules or .venv stays quick.
import { skipDir as ignoredDir } from './combine_engine.js';

// <input type="file" webkitdirectory>: webkitRelativePath is "root/sub/file". Empty folders are not reported.
export function fromFileList(list, rules) {
  const all = [...list];
  if (!all.length) throw new Error('No files in that folder (the browser does not list empty folders).');
  const name = all[0].webkitRelativePath.split('/')[0];
  const files = [];
  for (const f of all) {
    const parts = f.webkitRelativePath.split('/').slice(1);
    if (!parts.length || parts.slice(0, -1).some(p => ignoredDir(p, rules))) continue;
    files.push({ path: parts.join('/'), file: f });
  }
  return { name, files, dirs: [], emptyDirsKnown: false };
}

const readAll = reader => new Promise((resolve, reject) => {
  const out = [];
  const more = () => reader.readEntries(batch => { if (!batch.length) resolve(out); else { out.push(...batch); more(); } }, reject);
  more();
});
const entryFile = entry => new Promise((resolve, reject) => entry.file(resolve, reject));

// Drag and drop: one folder. Walks with the FileSystem entry API, which also reports empty folders.
export async function fromDrop(dataTransfer, rules, onProgress = () => {}) {
  const entries = [...dataTransfer.items].filter(i => i.kind === 'file').map(i => i.webkitGetAsEntry && i.webkitGetAsEntry()).filter(Boolean);
  if (entries.length !== 1 || !entries[0].isDirectory) throw new Error('Drop one folder (the project root), not loose files.');
  const root = entries[0], files = [], dirs = [];
  const walk = async (dir, prefix) => {
    for (const e of await readAll(dir.createReader())) {
      const path = prefix ? prefix + '/' + e.name : e.name;
      if (e.isDirectory) {
        if (ignoredDir(e.name, rules)) continue;
        dirs.push(path);
        await walk(e, path);
      } else {
        files.push({ path, file: await entryFile(e) });
        if (files.length % 200 === 0) onProgress(files.length);
      }
    }
  };
  await walk(root, '');
  return { name: root.name, files, dirs, emptyDirsKnown: true };
}

// The test tree from api/demo as the same shape (bytes decoded from base64, wrapped as Blobs).
export function fromDemo(demo) {
  const files = demo.tree.files.map(f => ({
    path: f.path, file: new Blob([Uint8Array.from(atob(f.b64), c => c.charCodeAt(0))]),
  }));
  return { name: demo.tree.name, files, dirs: demo.tree.dirs, emptyDirsKnown: true };
}
