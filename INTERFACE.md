# combine_project -- Interface Map

## Project Structure

```
combine_project/
  combine_project.py       # Main module: ProjectCombiner class + CLI (main())
  test_combine_project.py  # Unit tests using tempdir-based project structures
  pyproject.toml           # Packaging metadata
  .gitignore               # Ignores COMBINED_PROJECT.txt, PROJECT_STRUCTURE.txt
  README.md
  ROADMAP.md
  INTERFACE.md             # This file
```

## Key Classes and Functions

| Symbol | File | Purpose |
|---|---|---|
| `ProjectCombiner` | `combine_project.py` | Main class: walks project tree, filters files, generates combined output and structure tree |
| `ProjectCombiner.combine_files()` | `combine_project.py` | Merges all source files into COMBINED_PROJECT.txt |
| `ProjectCombiner.create_structure_file()` | `combine_project.py` | Generates PROJECT_STRUCTURE.txt with tree view |
| `ProjectCombiner.should_ignore()` | `combine_project.py` | Filters __pycache__, .git, hidden files, etc. |
| `main()` | `combine_project.py` | CLI entry point with argparse (project_root, --output) |
