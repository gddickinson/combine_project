# Project Combiner -- Roadmap

## Current State
A single-file utility (`combine_project.py`) that merges all source files in a Python project into one text file for sharing with LLMs, plus generates a tree-view structure file. `ProjectCombiner` class with smart filtering (includes common source extensions, excludes `__pycache__`/`.git`/etc.), sorted output, and CLI interface. No external dependencies. Clean, well-organized code.

## Short-term Improvements
- [x] Add unit tests using temporary directories with known file structures
- [ ] Add `--dry-run` flag to preview files that would be included without writing output
- [ ] Add file size warnings for large binary files that match include extensions
- [ ] Handle encoding errors gracefully (some files may not be UTF-8)
- [ ] Add `--max-file-size` option to skip files larger than a threshold
- [ ] Add line count per file in `PROJECT_STRUCTURE.txt` output

## Feature Enhancements
- [ ] Add `--include` and `--exclude` CLI flags for custom file patterns
- [ ] Support `.combineignore` file (like `.gitignore` syntax) for per-project customization
- [ ] Add token count estimation for LLM context windows (tiktoken-based)
- [ ] Generate markdown-formatted output as alternative to plain text
- [ ] Add `--split` mode that chunks output into files under a token limit
- [ ] Support combining only git-tracked files (respecting `.gitignore`)
- [ ] Add clipboard copy mode (`--clipboard`) for direct paste into chat

## Long-term Vision
- [ ] Create a VS Code extension that combines and pastes to clipboard with one command
- [ ] Add intelligent file prioritization (most-imported files first, tests last)
- [ ] Support project-specific context templates (e.g., include CLAUDE.md preamble)
- [ ] Add diffing mode: combine only files changed since last commit
- [ ] Package as a pip-installable CLI tool with entry points

## Technical Debt
- [x] `ignore_dirs` set uses glob patterns (`*.egg-info`) but matching logic may be literal -- verify
- [ ] File sorting priority (docs first, Python, then others) is hardcoded -- make configurable
- [x] No `.gitignore` for output files (`COMBINED_PROJECT.txt`, `PROJECT_STRUCTURE.txt`)
- [x] No `pyproject.toml` or packaging metadata -- needed for pip distribution
- [ ] Error handling for permission-denied files is minimal
