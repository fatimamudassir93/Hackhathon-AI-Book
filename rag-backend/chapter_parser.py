"""
Chapter metadata parser for extracting hierarchical structure from markdown
Parses headers to build document hierarchy (chapter > section > subsection)
"""
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HeaderNode:
    """Represents a header in the document hierarchy"""
    level: int  # 1-6 (H1-H6)
    text: str
    line_number: int
    children: List['HeaderNode']

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "level": self.level,
            "text": self.text,
            "line_number": self.line_number,
            "children": [child.to_dict() for child in self.children]
        }


@dataclass
class DocumentStructure:
    """Represents the complete hierarchical structure of a document"""
    file_path: str
    title: Optional[str]  # First H1
    headers: List[HeaderNode]
    total_lines: int

    def get_chapter_info(self) -> Dict[str, Any]:
        """Extract chapter-level information"""
        chapter_num = None
        chapter_name = None

        # Try to extract from title
        if self.title:
            match = re.search(r'chapter\s+(\d+)', self.title, re.IGNORECASE)
            if match:
                chapter_num = int(match.group(1))
                chapter_name = self.title

        # Try to extract from filename
        if not chapter_num:
            filename = Path(self.file_path).stem
            match = re.search(r'chapter(\d+)', filename, re.IGNORECASE)
            if match:
                chapter_num = int(match.group(1))
                if self.title:
                    chapter_name = self.title
                else:
                    chapter_name = f"Chapter {chapter_num}"

        return {
            "chapter_number": chapter_num,
            "chapter_name": chapter_name or self.title or "Unknown",
            "title": self.title
        }

    def get_sections(self) -> List[str]:
        """Get all H2 headers (sections)"""
        sections = []
        for header in self.headers:
            if header.level == 2:
                sections.append(header.text)
        return sections

    def get_subsections(self) -> List[str]:
        """Get all H3 headers (subsections)"""
        subsections = []
        for header in self.headers:
            if header.level == 3:
                subsections.append(header.text)
            for child in header.children:
                if child.level == 3:
                    subsections.append(child.text)
        return subsections

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "file_path": self.file_path,
            "title": self.title,
            "chapter_info": self.get_chapter_info(),
            "sections": self.get_sections(),
            "subsections": self.get_subsections(),
            "total_headers": len(self.headers),
            "total_lines": self.total_lines
        }


class ChapterParser:
    """
    Parses markdown documents to extract hierarchical structure.
    Builds a tree of headers representing document organization.
    """

    def __init__(self):
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+?)$')

    def parse_file(self, file_path: str) -> DocumentStructure:
        """
        Parse a markdown file and extract its structure.

        Args:
            file_path: Path to the markdown file

        Returns:
            DocumentStructure object with hierarchy
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return self.parse_content(content, str(path.absolute()))

    def parse_content(self, content: str, file_path: str = "") -> DocumentStructure:
        """
        Parse markdown content and extract structure.

        Args:
            content: Markdown text
            file_path: Optional file path for metadata

        Returns:
            DocumentStructure object
        """
        lines = content.split('\n')
        headers = []
        title = None
        header_stack = []  # Stack for building hierarchy

        for line_num, line in enumerate(lines, 1):
            match = self.header_pattern.match(line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()

                # First H1 is the title
                if level == 1 and title is None:
                    title = text

                # Create header node
                node = HeaderNode(
                    level=level,
                    text=text,
                    line_number=line_num,
                    children=[]
                )

                # Build hierarchy
                # Pop headers from stack until we find a parent (lower level)
                while header_stack and header_stack[-1].level >= level:
                    header_stack.pop()

                # Add as child to parent, or as root
                if header_stack:
                    header_stack[-1].children.append(node)
                else:
                    headers.append(node)

                # Push current header to stack
                header_stack.append(node)

        return DocumentStructure(
            file_path=file_path,
            title=title,
            headers=headers,
            total_lines=len(lines)
        )

    def get_header_at_line(
        self,
        structure: DocumentStructure,
        line_number: int
    ) -> Optional[HeaderNode]:
        """
        Find the most relevant header for a given line number.

        Args:
            structure: DocumentStructure object
            line_number: Line number in the document

        Returns:
            HeaderNode if found, None otherwise
        """
        def find_closest(headers: List[HeaderNode]) -> Optional[HeaderNode]:
            closest = None
            for header in headers:
                if header.line_number <= line_number:
                    closest = header
                    # Check children
                    child_result = find_closest(header.children)
                    if child_result:
                        closest = child_result
                else:
                    break
            return closest

        return find_closest(structure.headers)

    def build_breadcrumb(
        self,
        structure: DocumentStructure,
        line_number: int
    ) -> List[str]:
        """
        Build a breadcrumb trail of headers leading to a line.

        Args:
            structure: DocumentStructure object
            line_number: Line number in the document

        Returns:
            List of header texts from root to leaf
        """
        breadcrumb = []

        def collect_path(headers: List[HeaderNode], path: List[str]) -> bool:
            for header in headers:
                current_path = path + [header.text]

                if header.line_number <= line_number:
                    # This header is before or at the line
                    if not header.children or header.children[0].line_number > line_number:
                        # This is the deepest header before the line
                        breadcrumb.extend(current_path)
                        return True

                    # Check children
                    if collect_path(header.children, current_path):
                        return True

            return False

        collect_path(structure.headers, [])
        return breadcrumb


def parse_chapter(file_path: str) -> DocumentStructure:
    """
    Convenience function to parse a chapter file.

    Args:
        file_path: Path to markdown file

    Returns:
        DocumentStructure object
    """
    parser = ChapterParser()
    return parser.parse_file(file_path)


if __name__ == "__main__":
    # Test the parser
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default test file
        file_path = "../physical-ai-book/docs/chapters/chapter1.md"

    abs_path = Path(file_path).resolve()

    if not abs_path.exists():
        print(f"File not found: {abs_path}")
        print("Usage: python chapter_parser.py <path_to_markdown_file>")
        sys.exit(1)

    print(f"Parsing: {abs_path}\n")

    parser = ChapterParser()
    structure = parser.parse_file(str(abs_path))

    print("Document Structure:")
    print("=" * 60)
    print(f"Title: {structure.title}")
    print(f"Total lines: {structure.total_lines}")

    chapter_info = structure.get_chapter_info()
    print(f"\nChapter Info:")
    print(f"  Number: {chapter_info['chapter_number']}")
    print(f"  Name: {chapter_info['chapter_name']}")

    print(f"\nSections (H2): {len(structure.get_sections())}")
    for section in structure.get_sections():
        print(f"  - {section}")

    print(f"\nSubsections (H3): {len(structure.get_subsections())}")
    for subsection in structure.get_subsections()[:10]:
        print(f"  - {subsection}")
    if len(structure.get_subsections()) > 10:
        print(f"  ... and {len(structure.get_subsections()) - 10} more")

    # Test breadcrumb for middle of document
    mid_line = structure.total_lines // 2
    breadcrumb = parser.build_breadcrumb(structure, mid_line)
    print(f"\nBreadcrumb at line {mid_line}:")
    print(" > ".join(breadcrumb) if breadcrumb else "  (no headers found)")
