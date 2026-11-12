"""A small test project tree that exercises every include/exclude and formatting rule of ProjectCombiner.

It is test data (not a real project): used by scripts/make_combine_fixture.py, the node test of the JS port and the
web page's "try the test tree" button.
"""
import base64

NAME = "fixture_proj"
GENERATED = "2026-01-02 03:04:05"

FILES = {
    "README.md": b"# Fixture project\r\nWindows line endings (CRLF) become LF.\r\n",
    "B_upper.py": b"print('upper-case names sort before lower-case')\n",
    "a_lower.py": b"x = 1",  # no trailing newline: one is added
    "caf\u00e9.md": "Unicode file name and content: café → ✓\n".encode(),
    "z.py": b"# private-use BMP character in the name\n",
    "z\U0001F600.py": b"# astral character in the name (sorts after U+E000 by code point)\n",
    "config.yaml": b"key: value\n",
    "data.json": b'{"a": 1}\n',
    "pyproject.toml": b"[project]\nname = 'fixture'\n",
    "setup.cfg": b"[metadata]\n",
    "run.sh": b"#!/bin/sh\necho hi\n",
    "Makefile": b"all:\n\techo make\n",
    "Dockerfile": b"FROM python:3.12\n",
    "LICENSE": b"MIT\n",
    "requirements": b"numpy\n",
    "notes.TXT": b"upper-case extension: shown in the tree, not combined\n",
    "image.png": b"\x89PNG\r\n\x1a\n\x00\x00",
    "empty.txt": b"",
    "COMBINED_PROJECT.txt": b"output of an earlier run: never an input\n",
    ".gitignore": b"*.pyc\n",
    ".env.example": b"KEY=\n",
    ".secret": b"hidden\n",
    ".DS_Store": b"\x00\x01",
    ".github/workflows/ci.yml": b"on: push\n",
    "docs/guide.md": b"Guide without trailing newline",
    "docs/README.txt": b"A README anywhere sorts first.\n",
    "docs/PROJECT_STRUCTURE.txt": b"same name as an output, but not in the output folder: included\n",
    "docs/venv": b"a FILE called venv is not an ignored directory\n",
    "src/pkg/__init__.py": b"",
    "src/pkg/core.py": b"\xef\xbb\xbf# UTF-8 BOM kept\rold Mac line ending\r\ndef f():\n    return 1\n",
    "src/pkg/__pycache__/core.cpython-312.pyc": b"\x00\x01bytecode",
    "src/pkg/Makefile": b"sub:\n\ttrue\n",
    "src/binary.py": b"\x80\x81\x82\xff not UTF-8",
    "src/mod.pyc": b"\x00",
    "lib.so/inner.py": b"# directory with an ignored suffix: hidden in the tree, still combined\n",
    "foo.egg-info/PKG-INFO": b"Metadata\n",
    "build/out.py": b"# ignored directory\n",
    "node_modules/x/index.json": b"{}\n",
    "venv/lib.py": b"# ignored directory\n",
    ".venv/lib.py": b"# ignored directory\n",
}
EMPTY_DIRS = ["empty_dir", "src/empty_sub"]


def tree():
    """The tree as JSON (paths sorted for a stable file)."""
    return {
        "name": NAME,
        "files": [{"path": p, "b64": base64.b64encode(FILES[p]).decode()} for p in sorted(FILES)],
        "dirs": EMPTY_DIRS,
    }
