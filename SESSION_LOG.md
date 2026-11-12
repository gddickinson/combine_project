# Session log

## 2026-11-12 -- web interface and static site (branch `web-interface`)

- Fixed two bugs in `combine_project.py` (regression tests in `test_combine_project.py`):
  - `should_ignore()` checked every parent folder of a path, including folders ABOVE the project root, so a project
    stored under e.g. `~/build/`, `~/env/` or `~/dist/` produced an empty combined file. Now only folders inside the
    project count.
  - The two output files are written into the project root by default, so the structure file was combined into
    `COMBINED_PROJECT.txt`, and a re-run combined the previous output (and listed both in the tree and counts). The
    tool's own outputs in the output folder are now never inputs.
- Added the `.gitignore` that INTERFACE.md and ROADMAP.md said existed.
- Refactor (output unchanged, checked byte for byte against the previous code on the test tree): `render_combined()`,
  `render_structure()`, `collect_files()`, `count_files()`, `read_text()` with an injectable time stamp; the
  extensionless include names and allowed hidden names are now attributes (`include_names`, `hidden_allowed`).
- Web interface (FastAPI, port 8151) + GitHub Pages static site. The tool itself runs in the browser
  (`web/static/combine_engine.js`), byte-for-byte equal to the Python on `web/fixture_tree.py` (node tests), and on a
  copy of this repo picked through the real folder input in Chrome (Playwright).
- Left as is, for George to decide: files inside hidden folders (e.g. `.github/`) are combined but the folder is not
  shown in the tree; a folder whose name ends in an ignored extension (e.g. `lib.so/`) is hidden in the tree but its
  files are combined. The web port copies both behaviours and documents them on the Rules page.
