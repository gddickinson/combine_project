// Rules: the include/exclude sets (from ProjectCombiner via api/info), output order and format, and known quirks.
import { api, app, esc, route, tags } from './core.js';

route('rules', async () => {
  const { rules: r } = await api('/info');
  app().innerHTML = `
  <p class="kicker">Read from combine_project.py</p>
  <h1 class="glow">What gets combined</h1>
  <p class="lead">These lists come straight from <code>ProjectCombiner</code>, so the browser and the command line use
    the same rules. Names and extensions are case-sensitive.</p>
  <div class="two">
    <div class="panel"><h3>Included extensions</h3><div class="rule-list">${tags(r.include_extensions, 'a')}</div>
      <h3>Included files without an extension</h3><div class="rule-list">${tags(r.include_names, 'a')}</div>
      <p class="small mute">Everything else (images, .js, .csv, upper-case .PY ...) is shown in the tree but not combined.</p></div>
    <div class="panel"><h3>Folders skipped (with everything inside)</h3><div class="rule-list">${tags(r.ignore_dirs, 'b')}</div>
      <h3>Extensions skipped</h3><div class="rule-list">${tags(r.ignore_extensions, 'b')}</div>
      <h3>Hidden names that are kept</h3><div class="rule-list">${tags(r.hidden_allowed, 'c')}</div>
      <p class="small mute">Any other name starting with a dot is hidden. ${tags(r.output_names)} in the project folder are the
        tool's own output and are never read back in.</p></div>
  </div>
  <h2>Order and format</h2>
  <p>Files are combined in this order: README files (<code>${esc(r.readme_names.join(', '))}</code>, any case, any folder)
    first, then other <code>.md</code> files, then <code>.py</code>, then the rest; within each group by path. Each file gets a
    header of 80 <code>=</code> signs with <code>FILE i/n: path</code>. Text is read as UTF-8; Windows (CRLF) and old Mac (CR)
    line endings become LF, and a missing final newline is added. A file that is not valid UTF-8 is replaced by
    <code>[Binary file - cannot display content]</code>.</p>
  <p>The structure file is a tree (folders first, then files, sorted by name with upper case before lower case),
    followed by a count of combined files per extension and the total.</p>
  <h2>Quirks kept from the Python</h2>
  <p class="quirk">The browser copies the Python behaviour exactly, including two inconsistencies (left for the author to decide on):</p>
  <ul class="quirk">
    <li>Files inside a <b>hidden folder</b> such as <code>.github/</code> are combined (and counted), but the folder is hidden in the tree.</li>
    <li>A <b>folder whose name ends in a skipped extension</b> (e.g. <code>lib.so/</code>) is hidden in the tree, but the files in it are still combined.</li>
  </ul>
  <p class="small mute">Differences from running the Python on disk: the browser cannot see symbolic links or file
    permissions, and empty folders only appear when the folder is dragged in (the folder button does not report them).</p>`;
});
