// Home: hero, real counts from the rules in combine_project.py, and cards to the pages.
import { api, app, esc, route } from './core.js';

route('home', async () => {
  const info = await api('/info');
  const r = info.rules;
  app().innerHTML = `
  <section class="hero">
    <p class="kicker">One file to paste · one file with the layout</p>
    <h1 class="glow">Project Combiner</h1>
    <p class="lead">${esc(info.description)}: pick a project folder and get <b>COMBINED_PROJECT.txt</b> (every source
      file, with a header per file, README first) and <b>PROJECT_STRUCTURE.txt</b> (a tree view and a count of files by
      type). It all happens in your browser, and your files never leave your device.</p>
    <a class="btn" href="#/combine">Choose a folder</a><a class="btn alt" href="#/rules">What is included</a><a class="btn alt" href="#/about">About</a>
  </section>
  <div class="tiles">
    <div class="tile"><b>${r.include_extensions.length}</b><span>file extensions included</span></div>
    <div class="tile"><b>${r.include_names.length}</b><span>extensionless names included (Makefile, LICENSE...)</span></div>
    <div class="tile"><b>${r.ignore_dirs.length}</b><span>folder names skipped (.git, venv, node_modules...)</span></div>
    <div class="tile"><b>0</b><span>bytes uploaded</span></div>
  </div>
  <h2>Pages</h2>
  <div class="grid">
    <a class="card" href="#/combine"><b>Combine</b><span>Choose or drag in a folder, preview both files, download them or copy them to the clipboard. A small test tree is there to try first.</span></a>
    <a class="card" href="#/rules"><b>Rules</b><span>Which files are included and skipped, the output order and format, read from the Python class itself.</span></a>
    <a class="card" href="#/about"><b>About</b><span>The command-line tool, the local web app, and how the browser version is checked against the Python.</span></a>
  </div>`;
});
