# Project Combiner

A utility that combines all files in a Python project into a single text file for easy sharing (e.g., pasting into an LLM chat). Also generates a tree-view project structure file.

## Features

- **File combination** -- merges all project source files into one `COMBINED_PROJECT.txt`
- **Structure generation** -- creates a `PROJECT_STRUCTURE.txt` with tree view and file statistics
- **Smart filtering**:
  - Includes: `.py`, `.md`, `.txt`, `.yml`, `.yaml`, `.json`, `.toml`, `.cfg`, `.ini`, `.rst`, `.sh`
  - Excludes: `__pycache__`, `.git`, `node_modules`, `venv`, binary files, hidden files
- **Sorted output** -- documentation files first, then Python files, then others
- **CLI interface** with configurable project root and output directory

## Requirements

- Python 3.6+ (no external dependencies)

## Usage

```bash
# Combine current directory
python combine_project.py

# Combine a specific project
python combine_project.py /path/to/project

# Specify output directory
python combine_project.py /path/to/project --output ./combined_output
```

### Output Files

| File | Contents |
|------|----------|
| `COMBINED_PROJECT.txt` | All source files concatenated with headers |
| `PROJECT_STRUCTURE.txt` | Tree view + file count summary |

## Example Output

```
================================================================================
COMBINED PROJECT: my_project
Generated: 2026-04-07 10:00:00
Total files: 12
================================================================================

================================================================================
FILE 1/12: README.md
================================================================================

# My Project
...
```

## Project Structure

```
combine_project/
├── combine_project.py   # ProjectCombiner class + CLI entry point
└── README.md
```
