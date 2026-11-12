#!/usr/bin/env python3
"""
Project Combiner Script
Combines all files in a Python project into a single file for easy sharing,
and creates a separate file with the project structure.
"""

import os
from pathlib import Path
from datetime import datetime

# Names of the two files this tool writes (into output_dir)
COMBINED_NAME = 'COMBINED_PROJECT.txt'
STRUCTURE_NAME = 'PROJECT_STRUCTURE.txt'
OUTPUT_NAMES = (COMBINED_NAME, STRUCTURE_NAME)


class ProjectCombiner:
    def __init__(self, project_root='.', output_dir=None):
        """
        Initialize the project combiner.
        
        Args:
            project_root: Root directory of the project (default: current directory)
            output_dir: Directory to save output files (default: project_root)
        """
        self.project_root = Path(project_root).resolve()
        self.output_dir = Path(output_dir) if output_dir else self.project_root
        
        # Directories and files to ignore
        self.ignore_dirs = {
            '__pycache__', '.git', '.svn', '.hg', 'node_modules',
            '.pytest_cache', '.mypy_cache', '.tox', 'venv', 'env',
            '.venv', 'dist', 'build', '*.egg-info', '.idea', '.vscode'
        }
        
        self.ignore_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
            '.class', '.o', '.obj', '.DS_Store'
        }
        
        # Extensions to include
        self.include_extensions = {
            '.py', '.md', '.txt', '.yml', '.yaml', '.json',
            '.toml', '.cfg', '.ini', '.rst', '.sh'
        }

        # Files without an extension that are included by name
        self.include_names = {'Makefile', 'Dockerfile', 'requirements', 'LICENSE'}

        # Hidden (dot) names that are not ignored
        self.hidden_allowed = {'.gitignore', '.env.example'}
    
    def _matches_ignore_pattern(self, name):
        """Check if a name matches any ignore_dirs pattern (supports glob-style *)."""
        import fnmatch
        for pattern in self.ignore_dirs:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    def _relative_to_root(self, path):
        """Path relative to the project root (resolving the parent, so /var vs /private/var etc. agree), or None."""
        try:
            return path.parent.resolve().joinpath(path.name).relative_to(self.project_root)
        except (ValueError, OSError):
            return None

    def is_output_file(self, path):
        """True for this tool's own output files (COMBINED_PROJECT.txt, PROJECT_STRUCTURE.txt in output_dir)."""
        path = Path(path)
        if path.name not in OUTPUT_NAMES:
            return False
        try:
            return path.parent.resolve() == self.output_dir.resolve()
        except OSError:
            return False

    def should_ignore(self, path):
        """Check if a path should be ignored."""
        path = Path(path)

        # The tool's own output files are never inputs (else a re-run combines the previous output)
        if self.is_output_file(path):
            return True

        # Check if any parent directory inside the project should be ignored (folders above the
        # project root, e.g. ~/build/myproject, do not count)
        rel = self._relative_to_root(path)
        for parent in (rel if rel is not None else path).parents:
            if self._matches_ignore_pattern(parent.name):
                return True

        # Check if directory itself should be ignored
        if path.is_dir() and self._matches_ignore_pattern(path.name):
            return True
        
        # Check file extension
        if path.suffix in self.ignore_extensions:
            return True
        
        # Check if it's a hidden file (starting with .)
        if path.name.startswith('.') and path.name not in self.hidden_allowed:
            return True
        
        return False
    
    def should_include_file(self, path):
        """Check if a file should be included in the combined output."""
        path = Path(path)
        
        if self.should_ignore(path):
            return False
        
        if not path.is_file():
            return False
        
        # Include files with specific extensions
        if path.suffix in self.include_extensions:
            return True
        
        # Include files without extensions if they're in specific locations
        if not path.suffix and path.name in self.include_names:
            return True
        
        return False
    
    def get_relative_path(self, path):
        """Get path relative to project root."""
        try:
            return Path(path).relative_to(self.project_root)
        except ValueError:
            return Path(path)
    
    def generate_tree_structure(self, startpath, prefix='', is_last=True):
        """Generate a tree structure of the project."""
        lines = []
        startpath = Path(startpath)
        
        if startpath == self.project_root:
            lines.append(str(startpath.name) + '/')
        
        try:
            items = sorted(startpath.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            items = [item for item in items if not self.should_ignore(item)]
            
            for i, item in enumerate(items):
                is_last_item = (i == len(items) - 1)
                
                if item == startpath:
                    continue
                
                connector = '└── ' if is_last_item else '├── '
                lines.append(f"{prefix}{connector}{item.name}{'/' if item.is_dir() else ''}")
                
                if item.is_dir():
                    extension = '    ' if is_last_item else '│   '
                    lines.extend(self.generate_tree_structure(item, prefix + extension, is_last_item))
        
        except PermissionError:
            pass
        
        return lines
    
    @staticmethod
    def timestamp():
        """The 'Generated:' time stamp written into both files."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def count_files(self):
        """{extension or 'no extension': count} over the files that would be combined."""
        file_counts = {}
        for root, dirs, files in os.walk(self.project_root):
            # Remove ignored directories from search (uses glob matching)
            dirs[:] = [d for d in dirs if not self._matches_ignore_pattern(d)]

            for file in files:
                filepath = Path(root) / file
                if self.should_include_file(filepath):
                    ext = filepath.suffix if filepath.suffix else 'no extension'
                    file_counts[ext] = file_counts.get(ext, 0) + 1
        return file_counts

    def render_structure(self, generated=None):
        """Text of PROJECT_STRUCTURE.txt (generated: time stamp string, default now)."""
        generated = generated or self.timestamp()
        tree_lines = self.generate_tree_structure(self.project_root)
        out = ['=' * 80 + '\n',
               f'PROJECT STRUCTURE: {self.project_root.name}\n',
               f'Generated: {generated}\n',
               '=' * 80 + '\n\n',
               '\n'.join(tree_lines),
               '\n\n',
               # Count files by type
               '=' * 80 + '\n',
               'FILE SUMMARY\n',
               '=' * 80 + '\n\n']
        file_counts = self.count_files()
        for ext, count in sorted(file_counts.items()):
            out.append(f'{ext}: {count} file(s)\n')
        out.append(f'\nTotal files: {sum(file_counts.values())}\n')
        return ''.join(out)

    def create_structure_file(self, generated=None):
        """Create a file with the project structure."""
        output_file = self.output_dir / STRUCTURE_NAME
        text = self.render_structure(generated)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'✓ Structure file created: {output_file}')
        return output_file

    def collect_files(self):
        """Files to combine, in output order: README first, other .md, .py, then the rest."""
        files_to_combine = []

        # Collect all files
        for root, dirs, files in os.walk(self.project_root):
            # Remove ignored directories from search (uses glob matching)
            dirs[:] = [d for d in dirs if not self._matches_ignore_pattern(d)]

            for file in sorted(files):
                filepath = Path(root) / file
                if self.should_include_file(filepath):
                    files_to_combine.append(filepath)

        # Sort files: documentation first, then Python files, then others
        def sort_key(filepath):
            name = filepath.name.lower()
            if name in {'readme.md', 'readme.txt', 'readme'}:
                return (0, str(filepath))
            elif filepath.suffix == '.md':
                return (1, str(filepath))
            elif filepath.suffix == '.py':
                return (2, str(filepath))
            else:
                return (3, str(filepath))

        files_to_combine.sort(key=sort_key)
        return files_to_combine

    @staticmethod
    def read_text(filepath):
        """A file's text as written into the combined file (universal newlines; placeholder if not UTF-8)."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content if content.endswith('\n') else content + '\n'
        except UnicodeDecodeError:
            return '[Binary file - cannot display content]\n'
        except Exception as e:
            return f'[Error reading file: {e}]\n'

    def render_combined(self, generated=None, files=None):
        """Text of COMBINED_PROJECT.txt (generated: time stamp string, default now)."""
        generated = generated or self.timestamp()
        files_to_combine = self.collect_files() if files is None else files
        n = len(files_to_combine)
        out = ['=' * 80 + '\n',
               f'COMBINED PROJECT: {self.project_root.name}\n',
               f'Generated: {generated}\n',
               f'Total files: {n}\n',
               '=' * 80 + '\n\n']
        for i, filepath in enumerate(files_to_combine, 1):
            relative_path = self.get_relative_path(filepath)
            out.append('\n' + '=' * 80 + '\n')
            out.append(f'FILE {i}/{n}: {relative_path}\n')
            out.append('=' * 80 + '\n\n')
            out.append(self.read_text(filepath))
            out.append('\n')
        return ''.join(out)

    def combine_files(self, generated=None):
        """Combine all project files into a single file."""
        output_file = self.output_dir / COMBINED_NAME
        files_to_combine = self.collect_files()
        text = self.render_combined(generated, files_to_combine)
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write(text)
        print(f'✓ Combined file created: {output_file}')
        print(f'  Contains {len(files_to_combine)} files')
        return output_file

    def run(self):
        """Run the combiner to create both output files."""
        print(f'\nCombining project: {self.project_root.name}')
        print(f'Output directory: {self.output_dir}\n')
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate both files
        structure_file = self.create_structure_file()
        combined_file = self.combine_files()
        
        print('\n' + '=' * 80)
        print('COMPLETE!')
        print('=' * 80)
        print(f'\nYou can now upload these files to chat:')
        print(f'  1. {structure_file.name} - Project structure overview')
        print(f'  2. {combined_file.name} - All project files combined')
        print(f'\nBoth files are in: {self.output_dir}')


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Combine Python project files into a single file for sharing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Combine current directory
  python combine_project.py
  
  # Combine specific project
  python combine_project.py /path/to/project
  
  # Specify output directory
  python combine_project.py --output ./combined_output
  
  # Combine specific project with custom output
  python combine_project.py /path/to/project --output ./output
        """
    )
    
    parser.add_argument(
        'project_root',
        nargs='?',
        default='.',
        help='Root directory of the project (default: current directory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output directory for combined files (default: project root)'
    )
    
    args = parser.parse_args()
    
    combiner = ProjectCombiner(
        project_root=args.project_root,
        output_dir=args.output
    )
    
    combiner.run()


if __name__ == '__main__':
    main()
