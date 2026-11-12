// Pure JS port of combine_project.ProjectCombiner (no DOM): the same include/exclude rules, ordering and text
// formatting, so the files produced in the browser equal the Python output byte for byte (combine_engine.test.mjs).
// Paths are relative to the project root, '/'-separated. The rules object comes from the Python class (api/info).

// --- Python semantics ---------------------------------------------------------------------------------------------
// pathlib.PurePath.suffix (Python 3.12): last '.' that is not the first or last character of the name.
export function suffix(name) {
  const i = name.lastIndexOf('.');
  return i > 0 && i < name.length - 1 ? name.slice(i) : '';
}

// Python compares str by code point; JS '<' compares UTF-16 units (differs for characters above U+FFFF).
export function cmpCodepoints(a, b) {
  const x = [...a], y = [...b];
  for (let i = 0; i < Math.min(x.length, y.length); i++) {
    const d = x[i].codePointAt(0) - y[i].codePointAt(0);
    if (d) return d;
  }
  return x.length - y.length;
}

// fnmatch.fnmatch on POSIX (case-sensitive): '*', '?' and '[seq]' / '[!seq]'.
const fnCache = new Map();
export function fnmatch(name, pattern) {
  if (!fnCache.has(pattern)) {
    let re = '', i = 0;
    while (i < pattern.length) {
      const c = pattern[i++];
      if (c === '*') re += '[\\s\\S]*';
      else if (c === '?') re += '[\\s\\S]';
      else if (c === '[') {
        const j = pattern.indexOf(']', i + (pattern[i] === '!' ? 2 : 1));
        if (j < 0) { re += '\\['; continue; }
        let body = pattern.slice(i, j).replace(/\\/g, '\\\\');
        if (body[0] === '!') body = '^' + body.slice(1);
        re += '[' + body + ']'; i = j + 1;
      } else re += c.replace(/[.*+?^${}()|[\]\\/]/g, '\\$&');
    }
    fnCache.set(pattern, new RegExp('^' + re + '$', 'u'));
  }
  return fnCache.get(pattern).test(name);
}

// --- rules ----------------------------------------------------------------------------------------------------------
const baseName = p => p.slice(p.lastIndexOf('/') + 1);
const matchesIgnore = (name, R) => R.ignore_dirs.some(p => fnmatch(name, p));

// ProjectCombiner.should_ignore (default output_dir = project root, so outputs are root-level names).
export function shouldIgnore(path, isDir, R) {
  const parts = path.split('/'), name = parts[parts.length - 1];
  if (parts.length === 1 && R.output_names.includes(name)) return true;
  for (const part of parts.slice(0, -1)) if (matchesIgnore(part, R)) return true;
  if (isDir && matchesIgnore(name, R)) return true;
  if (R.ignore_extensions.includes(suffix(name))) return true;
  if (name.startsWith('.') && !R.hidden_allowed.includes(name)) return true;
  return false;
}

// ProjectCombiner.should_include_file
export function shouldIncludeFile(path, R) {
  if (shouldIgnore(path, false, R)) return false;
  const name = baseName(path), ext = suffix(name);
  if (R.include_extensions.includes(ext)) return true;
  return !ext && R.include_names.includes(name);
}

// Readme first, then .md, then .py, then the rest; ties by path (Python sorts str(absolute path)).
function sortKey(path, R) {
  const name = baseName(path), ext = suffix(name);
  if (R.readme_names.includes(name.toLowerCase())) return 0;
  return ext === '.md' ? 1 : ext === '.py' ? 2 : 3;
}

// --- planning ---------------------------------------------------------------------------------------------------
// files: list of relative file paths; dirs: extra (e.g. empty) directory paths. Directories are also implied by files.
// Returns { included: sorted paths to combine, treeLines, counts: [[ext, n]...], total }.
export function plan(name, files, dirs, R) {
  const children = new Map([['', new Map()]]);   // dir path -> Map(child name -> isDir)
  const addDir = d => {
    if (children.has(d)) return;
    const i = d.lastIndexOf('/'), parent = i < 0 ? '' : d.slice(0, i);
    addDir(parent);
    children.get(parent).set(d.slice(i + 1), true);
    children.set(d, new Map());
  };
  for (const d of dirs) if (d) addDir(d.replace(/\/+$/, ''));
  for (const f of files) {
    const i = f.lastIndexOf('/'), parent = i < 0 ? '' : f.slice(0, i);
    addDir(parent);
    if (!children.get(parent).has(f.slice(i + 1))) children.get(parent).set(f.slice(i + 1), false);
  }

  // generate_tree_structure: dirs first, then by name; ignored entries dropped after sorting
  const treeLines = [name + '/'];
  const walk = (dir, prefix) => {
    const items = [...children.get(dir)].map(([n, isDir]) => ({ n, isDir, p: dir ? dir + '/' + n : n }))
      .sort((a, b) => (a.isDir === b.isDir ? cmpCodepoints(a.n, b.n) : a.isDir ? -1 : 1))
      .filter(it => !shouldIgnore(it.p, it.isDir, R));
    items.forEach((it, i) => {
      const last = i === items.length - 1;
      treeLines.push(`${prefix}${last ? '└── ' : '├── '}${it.n}${it.isDir ? '/' : ''}`);
      if (it.isDir) walk(it.p, prefix + (last ? '    ' : '│   '));
    });
  };
  walk('', '');

  // os.walk prunes directories matching ignore_dirs; should_ignore checks the same parents, so filtering is enough
  const included = files.filter(f => shouldIncludeFile(f, R));
  const keyed = included.map(p => [sortKey(p, R), p]);
  keyed.sort((a, b) => a[0] - b[0] || cmpCodepoints(a[1], b[1]));
  const counts = new Map();
  for (const f of included) {
    const ext = suffix(baseName(f)) || 'no extension';
    counts.set(ext, (counts.get(ext) || 0) + 1);
  }
  return {
    included: keyed.map(k => k[1]), treeLines,
    counts: [...counts].sort((a, b) => cmpCodepoints(a[0], b[0])), total: included.length,
  };
}

// --- text ---------------------------------------------------------------------------------------------------------
const RULE = '='.repeat(80);

// What ProjectCombiner.read_text writes for one file's bytes: strict UTF-8 (BOM kept), universal newlines.
export function fileText(bytes) {
  let s;
  try {
    s = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes);
  } catch {
    return '[Binary file - cannot display content]\n';
  }
  s = s.replace(/\r\n?/g, '\n');
  return s.endsWith('\n') ? s : s + '\n';
}

// datetime.now().strftime("%Y-%m-%d %H:%M:%S") in local time.
export function timestamp(d = new Date()) {
  const p = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

export function renderStructure(name, planned, generated) {
  const out = [`${RULE}\nPROJECT STRUCTURE: ${name}\nGenerated: ${generated}\n${RULE}\n\n`,
    planned.treeLines.join('\n'), '\n\n', `${RULE}\nFILE SUMMARY\n${RULE}\n\n`];
  for (const [ext, n] of planned.counts) out.push(`${ext}: ${n} file(s)\n`);
  out.push(`\nTotal files: ${planned.total}\n`);
  return out.join('');
}

// texts: Map(path -> text from fileText, or an '[Error reading file: ...]\n' line).
export function renderCombined(name, planned, texts, generated) {
  const n = planned.included.length;
  const out = [`${RULE}\nCOMBINED PROJECT: ${name}\nGenerated: ${generated}\nTotal files: ${n}\n${RULE}\n\n`];
  planned.included.forEach((p, i) => {
    out.push(`\n${RULE}\nFILE ${i + 1}/${n}: ${p}\n${RULE}\n\n`, texts.get(p), '\n');
  });
  return out.join('');
}
