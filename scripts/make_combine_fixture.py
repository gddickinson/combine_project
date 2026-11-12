"""Write tests/fixtures/combine_fixture.json: the test tree, the rules, and the Python output for it.

The node test web/static/combine_engine.test.mjs rebuilds the same tree in memory, runs the JS port and requires the
combined and structure text to equal the Python output byte for byte. tests/test_web.py checks this file is current.

Run: python scripts/make_combine_fixture.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web import fixture_tree  # noqa: E402
from web.project_io import rules, run_python  # noqa: E402

OUT = ROOT / "tests" / "fixtures" / "combine_fixture.json"


def build():
    t = fixture_tree.tree()
    return {"tree": t, "generated": fixture_tree.GENERATED, "rules": rules(),
            **run_python(t, fixture_tree.GENERATED)}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
