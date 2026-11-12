# combine_project -- Interface Map

## Project Structure

```
combine_project/
  combine_project.py        # ProjectCombiner class + CLI (main()); OUTPUT_NAMES
  test_combine_project.py   # Unit tests using tempdir-based project structures (incl. regression tests)
  pyproject.toml            # Packaging metadata
  .gitignore                # Ignores COMBINED_PROJECT.txt, PROJECT_STRUCTURE.txt, caches, site/
  run_web.py                # Starts the web app on 127.0.0.1:8151
  requirements-web.txt      # Pinned web/test deps (fastapi, uvicorn, httpx, pytest)
  web/
    __init__.py             # Docstring listing contents
    app.py                  # FastAPI: / (front end), /api/info (rules), /api/demo (test tree + Python output); STATIC_ENDPOINTS
    project_io.py           # rules() as JSON, materialise() a JSON tree on disk, run_python() -> combined/structure text
    fixture_tree.py         # The test project tree (every rule exercised) + fixed time stamp
    static/
      index.html, style.css, core.js     # shared web kit (theme, hash router, api(), download())
      style_app.css                      # accent palette + page styles
      main.js                            # lazy page registration, mode label, background
      static_api.js                      # answers api() from exported JSON on GitHub Pages
      combine_engine.js                  # JS port of ProjectCombiner: suffix, fnmatch, shouldIgnore, plan, fileText, render*
      folder_input.js                    # folder button (webkitdirectory), drag-and-drop walker, test tree -> file list
      home.js, combine.js, rules.js, about.js   # pages
      combine_engine.test.mjs, folder_input.test.mjs   # node tests: byte-for-byte vs the Python fixture
  scripts/
    make_combine_fixture.py # Writes tests/fixtures/combine_fixture.json (tree, rules, Python output)
    build_static.py         # Exports the static site (site/) for GitHub Pages
    screenshots.py          # Playwright smoke test + README screenshots (docs/img/)
  tests/
    test_web.py             # API, static build, fixture current, rules from the class, node tests
    fixtures/combine_fixture.json
  .github/workflows/pages.yml   # Build + publish the static site on push to main
  README.md, ROADMAP.md, SESSION_LOG.md, INTERFACE.md (this file)
```

## Key Classes and Functions

| Symbol | File | Purpose |
|---|---|---|
| `ProjectCombiner` | `combine_project.py` | Walks the project tree, filters files, generates combined output and structure tree |
| `.should_ignore()` / `.should_include_file()` | `combine_project.py` | Ignore rules (ignored folders inside the project, extensions, hidden names, own output files) / include rules |
| `.collect_files()` | `combine_project.py` | Files to combine in output order (README, .md, .py, rest) |
| `.render_combined(generated)` / `.render_structure(generated)` | `combine_project.py` | Text of the two output files (time stamp injectable) |
| `.combine_files()` / `.create_structure_file()` / `.run()` | `combine_project.py` | Write the files (CLI) |
| `main()` | `combine_project.py` | CLI entry point with argparse (project_root, --output) |
| `plan()`, `renderCombined()`, `renderStructure()`, `fileText()` | `web/static/combine_engine.js` | Browser port of the above |

## How they connect

`web/app.py` -> `web/project_io.py` -> `combine_project.ProjectCombiner` (rules, Python output for the test tree).
The browser fetches `/api/info` (rules) and runs `combine_engine.js` on the user's folder (via `folder_input.js`);
the fixture written by `scripts/make_combine_fixture.py` ties the two implementations together in the node tests.
