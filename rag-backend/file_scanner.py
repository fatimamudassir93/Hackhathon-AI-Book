"""
Markdown file discovery for textbook content ingestion
Scans directories and filters out tutorial/example content
"""
import os
from pathlib import Path
from typing import List, Set

# Directories to exclude from ingestion (tutorials, examples, generated content)
EXCLUDE_DIRS = {
    "tutorial-basics",
    "tutorial-extras",
    "node_modules",
    ".docusaurus",
    "build",
    "dist",
    ".git",
    "__pycache__"
}

# File patterns to exclude
EXCLUDE_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "LICENSE.md",
    ".gitignore"
}


class FileScanner:
    """
    Scans directories for markdown files suitable for ingestion.
    Filters out tutorial content and other non-textbook files.
    """

    def __init__(
        self,
        exclude_dirs: Set[str] = None,
        exclude_files: Set[str] = None
    ):
        """
        Initialize the file scanner.

        Args:
            exclude_dirs: Set of directory names to skip
            exclude_files: Set of filenames to skip
        """
        self.exclude_dirs = exclude_dirs or EXCLUDE_DIRS
        self.exclude_files = exclude_files or EXCLUDE_FILES

    def scan_directory(
        self,
        root_path: str,
        recursive: bool = True
    ) -> List[str]:
        """
        Scan a directory for markdown files.

        Args:
            root_path: Root directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of absolute file paths to markdown files
        """
        root = Path(root_path).resolve()

        if not root.exists():
            raise FileNotFoundError(f"Directory not found: {root_path}")

        if not root.is_dir():
            raise NotADirectoryError(f"Not a directory: {root_path}")

        markdown_files = []

        if recursive:
            # Recursive scan using glob
            for md_file in root.rglob("*.md"):
                if self._should_include(md_file, root):
                    markdown_files.append(str(md_file))
        else:
            # Non-recursive scan
            for md_file in root.glob("*.md"):
                if self._should_include(md_file, root):
                    markdown_files.append(str(md_file))

        # Sort for deterministic order
        markdown_files.sort()

        return markdown_files

    def _should_include(self, file_path: Path, root: Path) -> bool:
        """
        Determine if a file should be included in the scan results.

        Args:
            file_path: Path to the file
            root: Root directory of the scan

        Returns:
            True if file should be included, False otherwise
        """
        # Check if filename is in exclude list
        if file_path.name in self.exclude_files:
            return False

        # Check if any parent directory is in exclude list
        try:
            relative_path = file_path.relative_to(root)
            for part in relative_path.parts[:-1]:  # Exclude filename itself
                if part in self.exclude_dirs:
                    return False
        except ValueError:
            # file_path is not relative to root
            return False

        return True

    def get_textbook_files(self, docs_root: str) -> List[str]:
        """
        Get all textbook markdown files from a Docusaurus docs directory.

        This method specifically targets the common Docusaurus structure
        and filters out tutorial content.

        Args:
            docs_root: Path to the Docusaurus docs directory

        Returns:
            List of markdown file paths suitable for ingestion
        """
        all_files = self.scan_directory(docs_root, recursive=True)

        # Additional filtering for textbook content
        textbook_files = []

        for file_path in all_files:
            path = Path(file_path)

            # Prioritize files in 'chapters' directory if it exists
            if 'chapters' in path.parts:
                textbook_files.append(file_path)
                continue

            # Include top-level docs like preface, glossary, intro
            if path.parent.name == 'docs' or path.parent.name == Path(docs_root).name:
                # But exclude generated/example files
                if not any(excl in path.name.lower() for excl in ['template', 'example', 'sample']):
                    textbook_files.append(file_path)
                continue

            # Exclude tutorial subdirectories explicitly
            if 'tutorial' not in str(path).lower():
                textbook_files.append(file_path)

        return textbook_files

    def print_scan_summary(self, files: List[str], root: str):
        """
        Print a summary of scanned files.

        Args:
            files: List of file paths
            root: Root directory that was scanned
        """
        print(f"Scan Summary for: {root}")
        print(f"{'='*60}")
        print(f"Total files found: {len(files)}")

        if files:
            print(f"\nFiles by directory:")
            dirs = {}
            for file_path in files:
                dir_name = Path(file_path).parent.name
                dirs[dir_name] = dirs.get(dir_name, 0) + 1

            for dir_name, count in sorted(dirs.items()):
                print(f"  {dir_name}: {count} files")

            print(f"\nSample files:")
            for file_path in files[:5]:
                print(f"  - {Path(file_path).name}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")
        else:
            print("No files found matching criteria")

        print(f"{'='*60}")


def scan_for_textbook_content(docs_directory: str) -> List[str]:
    """
    Convenience function to scan for textbook content.

    Args:
        docs_directory: Path to the docs directory

    Returns:
        List of markdown file paths
    """
    scanner = FileScanner()
    return scanner.get_textbook_files(docs_directory)


if __name__ == "__main__":
    # Test the scanner
    import sys

    # Default to physical-ai-book/docs if no argument provided
    docs_path = sys.argv[1] if len(sys.argv) > 1 else "../physical-ai-book/docs"

    # Get absolute path
    abs_path = Path(__file__).parent / docs_path
    abs_path = abs_path.resolve()

    print(f"Scanning: {abs_path}\n")

    scanner = FileScanner()
    files = scanner.get_textbook_files(str(abs_path))

    scanner.print_scan_summary(files, str(abs_path))

    if files:
        print(f"\nFull file list:")
        for i, file_path in enumerate(files, 1):
            rel_path = Path(file_path).relative_to(abs_path.parent)
            print(f"  {i}. {rel_path}")
