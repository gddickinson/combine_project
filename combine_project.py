#!/usr/bin/env python3
"""
Project Combiner Script
Combines all files in a Python project into a single file for easy sharing,
and creates a separate file with the project structure.
"""

import os
from pathlib import Path
from datetime import datetime


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
    
    def should_ignore(self, path):
        """Check if a path should be ignored."""
        path = Path(path)
        
        # Check if any parent directory should be ignored
        for parent in path.parents:
            if parent.name in self.ignore_dirs:
                return True
        
        # Check if directory itself should be ignored
        if path.is_dir() and path.name in self.ignore_dirs:
            return True
        
        # Check file extension
        if path.suffix in self.ignore_extensions:
            return True
        
        # Check if it's a hidden file (starting with .)
        if path.name.startswith('.') and path.name not in {'.gitignore', '.env.example'}:
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
        if not path.suffix and path.name in {'Makefile', 'Dockerfile', 'requirements', 'LICENSE'}:
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
    
    def create_structure_file(self):
        """Create a file with the project structure."""
        output_file = self.output_dir / 'PROJECT_STRUCTURE.txt'
        
        tree_lines = self.generate_tree_structure(self.project_root)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('=' * 80 + '\n')
            f.write(f'PROJECT STRUCTURE: {self.project_root.name}\n')
            f.write(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('=' * 80 + '\n\n')
            
            f.write('\n'.join(tree_lines))
            f.write('\n\n')
            
            # Count files by type
            f.write('=' * 80 + '\n')
            f.write('FILE SUMMARY\n')
            f.write('=' * 80 + '\n\n')
            
            file_counts = {}
            total_files = 0
            
            for root, dirs, files in os.walk(self.project_root):
                # Remove ignored directories from search
                dirs[:] = [d for d in dirs if not self.should_ignore(Path(root) / d)]
                
                for file in files:
                    filepath = Path(root) / file
                    if self.should_include_file(filepath):
                        ext = filepath.suffix if filepath.suffix else 'no extension'
                        file_counts[ext] = file_counts.get(ext, 0) + 1
                        total_files += 1
            
            for ext, count in sorted(file_counts.items()):
                f.write(f'{ext}: {count} file(s)\n')
            
            f.write(f'\nTotal files: {total_files}\n')
        
        print(f'✓ Structure file created: {output_file}')
        return output_file
    
    def combine_files(self):
        """Combine all project files into a single file."""
        output_file = self.output_dir / 'COMBINED_PROJECT.txt'
        
        files_to_combine = []
        
        # Collect all files
        for root, dirs, files in os.walk(self.project_root):
            # Remove ignored directories from search
            dirs[:] = [d for d in dirs if not self.should_ignore(Path(root) / d)]
            
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
        
        # Write combined file
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write('=' * 80 + '\n')
            out.write(f'COMBINED PROJECT: {self.project_root.name}\n')
            out.write(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            out.write(f'Total files: {len(files_to_combine)}\n')
            out.write('=' * 80 + '\n\n')
            
            for i, filepath in enumerate(files_to_combine, 1):
                relative_path = self.get_relative_path(filepath)
                
                out.write('\n' + '=' * 80 + '\n')
                out.write(f'FILE {i}/{len(files_to_combine)}: {relative_path}\n')
                out.write('=' * 80 + '\n\n')
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        out.write(content)
                        if not content.endswith('\n'):
                            out.write('\n')
                except UnicodeDecodeError:
                    out.write(f'[Binary file - cannot display content]\n')
                except Exception as e:
                    out.write(f'[Error reading file: {e}]\n')
                
                out.write('\n')
        
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
