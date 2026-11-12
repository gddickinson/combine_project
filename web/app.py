"""FastAPI web app for Project Combiner: serves the front end in static/ and the JSON API under /api.

The combining itself runs in the browser (static/combine_engine.js, a byte-for-byte port of combine_project.py), so the
files a user picks never leave their device, locally or on GitHub Pages. The API supplies the rules straight from
ProjectCombiner and the test tree with the output the real Python code produces for it.

Run with `python run_web.py` (http://127.0.0.1:8151, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.
"""
import tomllib
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web import fixture_tree
from web.project_io import ROOT, rules, run_python

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Project Combiner")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary and the include/exclude rules exactly as combine_project.ProjectCombiner defines them."""
    meta = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    return {"title": "Project Combiner", "name": meta["name"], "version": meta["version"],
            "description": meta["description"], "rules": rules()}


@app.get("/api/demo")
def demo():
    """The test tree (every rule exercised) and the two files the Python code writes for it."""
    tree = fixture_tree.tree()
    return {"tree": tree, "generated": fixture_tree.GENERATED, **run_python(tree, fixture_tree.GENERATED)}


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/demo"]
