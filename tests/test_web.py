"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- project-specific -----------------------------------------------------------------------------------------------
import json  # noqa: E402

from combine_project import ProjectCombiner  # noqa: E402


def test_rules_come_from_the_python_class():
    r = client.get("/api/info").json()["rules"]
    c = ProjectCombiner(ROOT)
    assert set(r["include_extensions"]) == c.include_extensions
    assert set(r["ignore_dirs"]) == c.ignore_dirs
    assert set(r["ignore_extensions"]) == c.ignore_extensions
    assert set(r["include_names"]) == c.include_names
    assert set(r["hidden_allowed"]) == c.hidden_allowed


def test_fixture_is_current():
    """tests/fixtures/combine_fixture.json must match what the Python code produces now (exact text: no floats)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_combine_fixture
    saved = json.loads(make_combine_fixture.OUT.read_text(encoding="utf-8"))
    assert saved == make_combine_fixture.build(), "run: python scripts/make_combine_fixture.py"


def test_demo_matches_fixture():
    d = client.get("/api/demo").json()
    saved = json.loads((ROOT / "tests" / "fixtures" / "combine_fixture.json").read_text(encoding="utf-8"))
    assert d["combined"] == saved["combined"] and d["structure"] == saved["structure"]
    assert "FILE 25/25: src/pkg/Makefile" in d["combined"]


def test_fixture_covers_the_rules():
    s = json.loads((ROOT / "tests" / "fixtures" / "combine_fixture.json").read_text(encoding="utf-8"))
    combined, structure = s["combined"], s["structure"]
    for skipped in ("build/out.py", "venv/lib.py", ".venv/lib.py", "foo.egg-info", "mod.pyc", ".secret",
                    "image.png", "notes.TXT", "FILE 1/25: COMBINED_PROJECT.txt"):
        assert skipped not in combined, skipped
    assert "[Binary file - cannot display content]" in combined
    assert "\r" not in combined and "﻿# UTF-8 BOM kept" in combined
    assert "├── empty_dir/" in structure and "image.png" in structure and ".secret" not in structure
