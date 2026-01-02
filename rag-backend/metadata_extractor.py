"""
Metadata extraction utilities for chapter/section/subsection parsing
Extracts hierarchical structure from markdown documents
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class DocumentMetadata:
    """Metadata extracted from a document"""
    file_path: str
    chapter: str
    chapter_number: Optional[int]
    title: str
    sections: List[str]
    subsections: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return asdict(self)


class MetadataExtractor:
    """
    Extracts hierarchical metadata from markdown documents.
    Identifies chapters, sections, and subsections from header structure.
    """

    # Patterns for matching chapter information
    CHAPTER_PATTERNS = [
        r'chapter\s*(\d+)',  # "chapter 1", "Chapter 2"
        r'ch\s*(\d+)',       # "ch 1", "CH 2"
        r'^(\d+)-',          # "1-", "2-" (in filename)
    ]

    def __init__(self):
        self.chapter_pattern = re.compile(
            '|'.join(self.CHAPTER_PATTERNS),
            re.IGNORECASE
        )

    def extract_from_file(self, file_path: str) -> DocumentMetadata:
        """
        Extract metadata from a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            DocumentMetadata object with extracted information
        """
        path = Path(file_path)

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            content = ""

        # Extract chapter info from filename and content
        chapter, chapter_num = self._extract_chapter_info(path.name, content)

        # Extract title (first H1 header)
        title = self._extract_title(content)

        # Extract section hierarchy
        sections, subsections = self._extract_hierarchy(content)

        return DocumentMetadata(
            file_path=str(path.absolute()),
            chapter=chapter,
            chapter_number=chapter_num,
            title=title or path.stem,
            sections=sections,
            subsections=subsections
        )

    def _extract_chapter_info(
        self,
        filename: str,
        content: str
    ) -> tuple[str, Optional[int]]:
        """
        Extract chapter name and number from filename and content.

        Args:
            filename: Name of the file
            content: File content

        Returns:
            Tuple of (chapter_name, chapter_number)
        """
        chapter_num = None

        # Try to extract from filename first
        match = self.chapter_pattern.search(filename)
        if match:
            chapter_num = int(match.group(1))
            return f"Chapter {chapter_num}", chapter_num

        # Try to extract from first header in content
        header_match = re.search(
            r'^#\s+(.+?)$',
            content,
            re.MULTILINE
        )
        if header_match:
            header_text = header_match.group(1)
            chapter_match = self.chapter_pattern.search(header_text)
            if chapter_match:
                chapter_num = int(chapter_match.group(1))
                return f"Chapter {chapter_num}", chapter_num
            else:
                # Use header text as chapter name if no number found
                return header_text, None

        return "Unknown Chapter", None

    def _extract_title(self, content: str) -> Optional[str]:
        """
        Extract document title from first H1 header.

        Args:
            content: Markdown content

        Returns:
            Title string or None if not found
        """
        match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_hierarchy(
        self,
        content: str
    ) -> tuple[List[str], List[str]]:
        """
        Extract section and subsection headings.

        Args:
            content: Markdown content

        Returns:
            Tuple of (sections_list, subsections_list)
        """
        sections = []
        subsections = []

        lines = content.split('\n')

        for line in lines:
            # Match H2 headers (sections)
            section_match = re.match(r'^##\s+(.+?)$', line)
            if section_match:
                sections.append(section_match.group(1).strip())
                continue

            # Match H3 headers (subsections)
            subsection_match = re.match(r'^###\s+(.+?)$', line)
            if subsection_match:
                subsections.append(subsection_match.group(1).strip())

        return sections, subsections

    def create_chunk_metadata(
        self,
        doc_metadata: DocumentMetadata,
        current_header: str,
        header_level: int
    ) -> Dict[str, Any]:
        """
        Create metadata payload for a specific chunk.

        Args:
            doc_metadata: Document-level metadata
            current_header: Header text for this chunk's section
            header_level: Header level (1=H1, 2=H2, etc.)

        Returns:
            Dictionary with chunk metadata
        """
        metadata = {
            "source": doc_metadata.file_path,
            "chapter": doc_metadata.chapter,
            "title": doc_metadata.title,
        }

        # Add chapter number if available
        if doc_metadata.chapter_number is not None:
            metadata["chapter_number"] = doc_metadata.chapter_number

        # Classify header level
        if header_level == 1:
            metadata["heading"] = current_header
        elif header_level == 2:
            metadata["section"] = current_header
        elif header_level == 3:
            metadata["subsection"] = current_header
        elif header_level >= 4:
            metadata["subsubsection"] = current_header

        return metadata


def extract_metadata(file_path: str) -> DocumentMetadata:
    """
    Convenience function to extract metadata from a file.

    Args:
        file_path: Path to markdown file

    Returns:
        DocumentMetadata object
    """
    extractor = MetadataExtractor()
    return extractor.extract_from_file(file_path)


if __name__ == "__main__":
    # Test with a sample file
    import tempfile
    import os

    # Create a test markdown file
    test_content = """# Chapter 1: Introduction to Physical AI

This is the introduction to physical AI and embodied intelligence.

## What is Physical AI?

Physical AI combines artificial intelligence with physical systems.

### Key Concepts

Embodied intelligence is central to physical AI.

### Applications

Robotics and autonomous systems are key applications.

## History

Physical AI has evolved over decades of research.
"""

    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='_chapter1.md',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(test_content)
        temp_path = f.name

    try:
        # Extract metadata
        metadata = extract_metadata(temp_path)

        print("Extracted Metadata:")
        print(f"  Chapter: {metadata.chapter}")
        print(f"  Chapter Number: {metadata.chapter_number}")
        print(f"  Title: {metadata.title}")
        print(f"  Sections: {metadata.sections}")
        print(f"  Subsections: {metadata.subsections}")

        # Test chunk metadata creation
        extractor = MetadataExtractor()
        chunk_meta = extractor.create_chunk_metadata(
            metadata,
            current_header="Key Concepts",
            header_level=3
        )

        print("\nChunk Metadata Example:")
        for key, value in chunk_meta.items():
            print(f"  {key}: {value}")

    finally:
        # Clean up temp file
        os.unlink(temp_path)
