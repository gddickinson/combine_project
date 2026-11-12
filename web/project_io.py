"""Bridge between JSON file trees and the real ProjectCombiner (used by the API, the fixture script and the tests).

A tree is {"name": root folder name, "files": [{"path": "a/b.py", "b64": base64 bytes}], "dirs": ["empty/dir"]}.
"""
import base64
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from combine_project import OUTPUT_NAMES, ProjectCombiner  # noqa: E402


def rules():
    """The include/exclude rules exactly as ProjectCombiner holds them (sorted lists for JSON)."""
    c = ProjectCombiner(ROOT)
    return {
        "ignore_dirs": sorted(c.ignore_dirs),
        "ignore_extensions": sorted(c.ignore_extensions),
        "include_extensions": sorted(c.include_extensions),
        "include_names": sorted(c.include_names),
        "hidden_allowed": sorted(c.hidden_allowed),
        "output_names": list(OUTPUT_NAMES),
        "readme_names": ["readme", "readme.md", "readme.txt"],
    }


def materialise(tree, parent):
    """Write a JSON tree under parent/<name>; return the project root path."""
    root = Path(parent) / tree["name"]
    root.mkdir(parents=True)
    for d in tree.get("dirs", []):
        (root / d).mkdir(parents=True, exist_ok=True)
    for f in tree["files"]:
        p = root / f["path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(base64.b64decode(f["b64"]))
    return root


def run_python(tree, generated):
    """Combined and structure text produced by the Python ProjectCombiner for a JSON tree."""
    with tempfile.TemporaryDirectory() as tmp:
        root = materialise(tree, tmp)
        c = ProjectCombiner(root, output_dir=root)
        return {"combined": c.render_combined(generated), "structure": c.render_structure(generated)}
