// About: what the tool is, how to run the command line and the web app, how the port is checked, credits.
import { api, app, esc, isStatic, route } from './core.js';

route('about', async () => {
  const info = await api('/info');
  app().innerHTML = `
  <p class="kicker">About</p>
  <h1 class="glow">Project Combiner</h1>
  <p class="lead">${esc(info.description)}. Version ${esc(info.version)}, MIT licence.</p>
  <h2>Command line</h2>
  <p>A single Python file with no dependencies (Python 3.8+):</p>
  <pre>python combine_project.py                      # current folder
python combine_project.py /path/to/project     # a specific project
python combine_project.py /path/to/project --output ./combined_output</pre>
  <p>It writes <code>COMBINED_PROJECT.txt</code> and <code>PROJECT_STRUCTURE.txt</code> into the project folder (or <code>--output</code>).</p>
  <h2>This web version</h2>
  <p>The combining runs in the browser in <code>web/static/combine_engine.js</code>, a port of
    <code>ProjectCombiner</code>. A node test builds a test tree that hits every rule (CRLF and CR line endings, a byte-order
    mark, a non-UTF-8 <code>.py</code>, empty files, hidden and ignored folders, a folder named <code>lib.so</code>, Unicode names, a stale output file) and
    requires both files to equal the Python output byte for byte. The only difference in the text is the time stamp,
    which is the moment you click.</p>
  ${isStatic() ? '' : '<p class="callout a">You are running the local app. It serves the same page; your files are still read only by the browser.</p>'}
  <p>Run it locally:</p>
  <pre>pip install -r requirements-web.txt
python run_web.py        # http://127.0.0.1:8151</pre>
  <h2>Credits</h2>
  <p>By George Dickinson (<a href="https://github.com/gddickinson/combine_project">gddickinson/combine_project</a>). Built with
    AI assistance from <a href="https://claude.com/">Claude (Anthropic)</a>.</p>`;
});
