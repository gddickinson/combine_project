"""Web interface for combine_project (FastAPI + plain ES-module front end; the browser does the combining).

Contents:
- app.py         FastAPI app: static front end, JSON API under /api (rules, demo), STATIC_ENDPOINTS for GitHub Pages
- project_io.py  rules of ProjectCombiner as JSON; rebuild a file tree from JSON and run the real Python on it
- fixture_tree.py the small test project tree (every include/exclude rule) used by the fixture, tests and demo
- static/        the browser front end; combine_engine.js is the JS port tested byte-for-byte against the Python
"""
