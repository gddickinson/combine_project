"""Tests for combine_project.py using temporary directory structures."""

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

from combine_project import ProjectCombiner


class TestProjectCombiner(unittest.TestCase):
    """Tests for ProjectCombiner."""

    def setUp(self):
        """Create a temporary project directory with known structure."""
        self.tmpdir = tempfile.mkdtemp()
        # Create some files
        self._write(os.path.join(self.tmpdir, "main.py"), "print('hello')\n")
        self._write(os.path.join(self.tmpdir, "README.md"), "# Test Project\n")
        self._write(os.path.join(self.tmpdir, "config.yaml"), "key: value\n")
        # Create a subdirectory with a file
        sub = os.path.join(self.tmpdir, "src")
        os.makedirs(sub)
        self._write(os.path.join(sub, "utils.py"), "def helper(): pass\n")
        # Create an ignored directory
        pycache = os.path.join(self.tmpdir, "__pycache__")
        os.makedirs(pycache)
        self._write(os.path.join(pycache, "main.cpython-311.pyc"), "bytecode")

    def _write(self, path, content):
        with open(path, "w") as f:
            f.write(content)

    def test_should_include_python_files(self):
        combiner = ProjectCombiner(self.tmpdir)
        main_py = Path(self.tmpdir) / "main.py"
        self.assertTrue(combiner.should_include_file(main_py))

    def test_should_exclude_pycache(self):
        combiner = ProjectCombiner(self.tmpdir)
        pyc_file = Path(self.tmpdir) / "__pycache__" / "main.cpython-311.pyc"
        self.assertFalse(combiner.should_include_file(pyc_file))

    def test_combine_files_creates_output(self):
        output_dir = tempfile.mkdtemp()
        combiner = ProjectCombiner(self.tmpdir, output_dir=output_dir)
        result = combiner.combine_files()
        self.assertTrue(result.exists())
        content = result.read_text()
        self.assertIn("main.py", content)
        self.assertIn("print('hello')", content)

    def test_create_structure_file(self):
        output_dir = tempfile.mkdtemp()
        combiner = ProjectCombiner(self.tmpdir, output_dir=output_dir)
        result = combiner.create_structure_file()
        self.assertTrue(result.exists())
        content = result.read_text()
        self.assertIn("main.py", content)
        self.assertIn("src/", content)

    def test_readme_sorted_first(self):
        output_dir = tempfile.mkdtemp()
        combiner = ProjectCombiner(self.tmpdir, output_dir=output_dir)
        result = combiner.combine_files()
        content = result.read_text()
        # README.md should appear before main.py
        readme_pos = content.index("README.md")
        main_pos = content.index("main.py")
        self.assertLess(readme_pos, main_pos)

    def test_encoding_error_handled(self):
        """Binary file with .py extension should not crash the combiner."""
        binary_path = os.path.join(self.tmpdir, "binary.py")
        with open(binary_path, "wb") as f:
            f.write(b"\x80\x81\x82\x83\xff\xfe")
        output_dir = tempfile.mkdtemp()
        combiner = ProjectCombiner(self.tmpdir, output_dir=output_dir)
        # Should not raise
        result = combiner.combine_files()
        content = result.read_text()
        self.assertIn("binary.py", content)

    def test_hidden_files_ignored(self):
        hidden = Path(self.tmpdir) / ".secret"
        self._write(str(hidden), "secret data")
        combiner = ProjectCombiner(self.tmpdir)
        self.assertFalse(combiner.should_include_file(hidden))

    def test_gitignore_not_ignored_by_should_ignore(self):
        """`.gitignore` passes should_ignore (whitelisted) but is not in include_extensions."""
        gitignore = Path(self.tmpdir) / ".gitignore"
        self._write(str(gitignore), "*.pyc")
        combiner = ProjectCombiner(self.tmpdir)
        # should_ignore whitelists .gitignore
        self.assertFalse(combiner.should_ignore(gitignore))


class TestEggInfoGlobPattern(unittest.TestCase):
    """Verify that *.egg-info ignore pattern works correctly."""

    def test_egg_info_directory_ignored(self):
        tmpdir = tempfile.mkdtemp()
        egg_dir = os.path.join(tmpdir, "foo.egg-info")
        os.makedirs(egg_dir)
        filepath = os.path.join(egg_dir, "PKG-INFO")
        with open(filepath, "w") as f:
            f.write("Metadata")
        combiner = ProjectCombiner(tmpdir)
        result = combiner.should_ignore(Path(egg_dir))
        # After fix: glob matching via fnmatch, so '*.egg-info' matches 'foo.egg-info'.
        self.assertTrue(result)


class TestProjectInsideIgnoredNamedFolder(unittest.TestCase):
    """Folders ABOVE the project root must not trigger the ignore rules (e.g. a project kept under ~/build/)."""

    def test_project_under_build_folder_is_combined(self):
        root = Path(tempfile.mkdtemp()) / "build" / "proj"
        (root / "src").mkdir(parents=True)
        (root / "main.py").write_text("x = 1\n")
        (root / "src" / "util.py").write_text("y = 2\n")
        combiner = ProjectCombiner(root, output_dir=tempfile.mkdtemp())
        content = combiner.combine_files().read_text()
        self.assertIn("Total files: 2", content)
        self.assertIn("FILE 2/2: src/util.py", content)
        self.assertFalse(combiner.should_ignore(root / "main.py"))
        tree = combiner.generate_tree_structure(combiner.project_root)
        self.assertIn("├── src/", tree)


class TestOutputFilesNotCombined(unittest.TestCase):
    """The tool's own output files (written into the project root by default) must not be fed back in."""

    def test_rerun_does_not_include_previous_outputs(self):
        root = Path(tempfile.mkdtemp()) / "proj"
        root.mkdir()
        (root / "main.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            ProjectCombiner(root).run()
            ProjectCombiner(root).run()
        combined = (root / "COMBINED_PROJECT.txt").read_text()
        structure = (root / "PROJECT_STRUCTURE.txt").read_text()
        self.assertIn("Total files: 1", combined)
        self.assertNotIn("FILE 2/", combined)
        self.assertNotIn("PROJECT_STRUCTURE.txt", structure.split("FILE SUMMARY")[0])
        self.assertNotIn("COMBINED_PROJECT.txt", structure)
        self.assertIn("Total files: 1", structure)

    def test_same_names_elsewhere_still_included(self):
        root = Path(tempfile.mkdtemp()) / "proj"
        (root / "docs").mkdir(parents=True)
        (root / "docs" / "COMBINED_PROJECT.txt").write_text("kept\n")
        combiner = ProjectCombiner(root, output_dir=tempfile.mkdtemp())
        self.assertTrue(combiner.should_include_file(root / "docs" / "COMBINED_PROJECT.txt"))


if __name__ == "__main__":
    unittest.main()
